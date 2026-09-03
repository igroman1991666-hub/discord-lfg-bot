import os

import discord
from discord import app_commands
from discord.ext import commands
from dotenv import load_dotenv

load_dotenv()

GUILD_ID = 1544764634387447858


intents = discord.Intents.default()
bot = commands.Bot(command_prefix="!", intents=intents)


class LFGView(discord.ui.View):
    def __init__(self, author: discord.User, mode: str, slots: int):
        super().__init__(timeout=1800)
        self.author = author
        self.mode = mode
        self.slots = slots
        self.players = [author]

    def build_embed(self) -> discord.Embed:
        names = "\n".join(p.mention for p in self.players)
        embed = discord.Embed(
            title="Поиск команды",
            description=f"Режим: **{self.mode}**",
            color=discord.Color.blurple(),
        )
        embed.add_field(
            name=f"Состав {len(self.players)}/{self.slots}",
            value=names,
        )
        return embed

    @discord.ui.button(label="Присоединиться", style=discord.ButtonStyle.success)
    async def join(self, interaction: discord.Interaction, button: discord.ui.Button):
        if interaction.user in self.players:
            await interaction.response.send_message("Ты уже в составе", ephemeral=True)
            return

        self.players.append(interaction.user)

        if len(self.players) >= self.slots:
            button.disabled = True
            self.stop()

        await interaction.response.edit_message(embed=self.build_embed(), view=self)


@bot.event
async def on_ready():
    guild = discord.Object(id=GUILD_ID)
    bot.tree.copy_global_to(guild=guild)
    synced = await bot.tree.sync(guild=guild)
    print(f"Бот запущен как {bot.user}")
    print(f"Синхронизировано команд: {len(synced)}")

@bot.tree.command(name="lfg", description="Собрать команду для игры")
@app_commands.describe(mode="Режим игры", slots="Сколько человек нужно")
@app_commands.choices(mode=[
    app_commands.Choice(name="Valorant — Competitive", value="val_comp"),
    app_commands.Choice(name="CS2 — Premier", value="cs2_premier"),
])
async def lfg(
    interaction: discord.Interaction,
    mode: app_commands.Choice[str],
    slots: app_commands.Range[int, 2, 5],
):
    view = LFGView(interaction.user, mode.name, slots)
    await interaction.response.send_message(embed=view.build_embed(), view=view)


bot.run(os.getenv("DISCORD_TOKEN"))