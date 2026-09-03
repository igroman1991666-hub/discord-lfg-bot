import os
import discord
from discord import app_commands
from discord.ext import commands
from dotenv import load_dotenv

load_dotenv()

GUILD_ID = 1544764634387447858 # вставь свой ID сервера

intents = discord.Intents.default()
bot = commands.Bot(command_prefix="!", intents=intents)


@bot.event
async def on_ready():
    guild = discord.Object(id=GUILD_ID)
    bot.tree.copy_global_to(guild=guild)
    synced = await bot.tree.sync(guild=guild)
    print(f"Бот запущен как {bot.user}")
    print(f"Синхронизировано команд: {len(synced)}")


@bot.tree.command(name="привет", description="Бот поздоровается")
async def hello(interaction: discord.Interaction):
    await interaction.response.send_message("здорова!")


@bot.tree.command(name="lfg", description="Собрать команду для игры")
@app_commands.describe(mode="Режим игры", slots="Сколько человек нужно")
@app_commands.choices(mode=[
    app_commands.Choice(name="Valorant — Competitive", value="val_comp"),
    app_commands.Choice(name="CS2 — Premier", value="cs2_premier"),
])
async def lfg(
    interaction: discord.Interaction,
    mode: app_commands.Choice[str],
    slots: app_commands.Range[int, 1, 4],
):
    embed = discord.Embed(
        title="Поиск команды",
        description=f"Режим: **{mode.name}**",
        color=discord.Color.blurple(),
    )
    embed.add_field(name="Нужно игроков", value=str(slots))
    embed.set_footer(text=f"Создал {interaction.user.display_name}")
    await interaction.response.send_message(embed=embed)

bot.run(os.getenv("DISCORD_TOKEN"))