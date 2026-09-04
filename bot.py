import os

import discord
from discord import app_commands
from discord.ext import commands
from dotenv import load_dotenv

import db

load_dotenv()

GUILD_ID = int(os.getenv("GUILD_ID"))

intents = discord.Intents.default()
bot = commands.Bot(command_prefix="!", intents=intents)


def build_embed(mode: str, slots: int, player_ids: list[int]) -> discord.Embed:
    names = "\n".join(f"<@{pid}>" for pid in player_ids)
    embed = discord.Embed(
        title="Поиск команды",
        description=f"Режим: **{mode}**",
        color=discord.Color.blurple(),
    )
    embed.add_field(name=f"Состав {len(player_ids)}/{slots}", value=names)
    return embed


class LFGView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)

    @discord.ui.button(
        label="Присоединиться",
        style=discord.ButtonStyle.success,
        custom_id="lfg:join",
    )
    async def join(self, interaction: discord.Interaction, button: discord.ui.Button):
        data = db.get_lfg(interaction.message.id)

        if data is None:
            await interaction.response.send_message(
                "Этот набор больше не активен", ephemeral=True
            )
            return

        if interaction.user.id in data["players"]:
            await interaction.response.send_message("Ты уже в составе", ephemeral=True)
            return

        data["players"].append(interaction.user.id)

        if len(data["players"]) >= data["slots"]:
            db.delete_lfg(interaction.message.id)
            embed = build_embed(data["mode"], data["slots"], data["players"])
            embed.title = "Состав собран"
            embed.color = discord.Color.green()
            await interaction.response.edit_message(embed=embed, view=None)
            return

        db.update_players(interaction.message.id, data["players"])
        await interaction.response.edit_message(
            embed=build_embed(data["mode"], data["slots"], data["players"]),
            view=self,
        )

    @discord.ui.button(
        label="Выйти",
        style=discord.ButtonStyle.danger,
        custom_id="lfg:leave",
    )
    async def leave(self, interaction: discord.Interaction, button: discord.ui.Button):
        data = db.get_lfg(interaction.message.id)

        if data is None:
            await interaction.response.send_message(
                "Этот набор больше не активен", ephemeral=True
            )
            return

        if interaction.user.id not in data["players"]:
            await interaction.response.send_message(
                "Ты и не записан", ephemeral=True
            )
            return

        data["players"].remove(interaction.user.id)

        if not data["players"]:
            db.delete_lfg(interaction.message.id)
            embed = build_embed(data["mode"], data["slots"], [])
            embed.title = "Набор отменён"
            embed.color = discord.Color.red()
            await interaction.response.edit_message(embed=embed, view=None)
            return

        db.update_players(interaction.message.id, data["players"])
        await interaction.response.edit_message(
            embed=build_embed(data["mode"], data["slots"], data["players"]),
            view=self,
        )


@bot.event
async def setup_hook():
    db.init_db()
    bot.add_view(LFGView())


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
    players = [interaction.user.id]
    await interaction.response.send_message(
        embed=build_embed(mode.name, slots, players),
        view=LFGView(),
    )
    message = await interaction.original_response()
    db.create_lfg(message.id, mode.name, slots, players)


bot.run(os.getenv("DISCORD_TOKEN"))