import os
import config

from disnake.ext import commands
from disnake.flags import Intents

if config.debug:
    bot = commands.Bot(command_prefix="!", test_guilds=config.test_guilds, intents=Intents.all())
else:
    bot = commands.Bot(command_prefix="!", sync_commands_debug=True, intents=Intents.all())


@bot.event
async def on_ready():
    print(f"Загружаю коги...")
    print("---------------")

    for name in os.listdir('./src/cogs'):
        if name.endswith('.py'):
            bot.load_extension(f'cogs.{name[:-3]}')
            print(f'Ког {name} был загружен.')

    print("---------------")
    print("Загрузил все коги!")


@bot.command()
async def echo(inter, *, echo_value):
    if inter.author.id in config.devs:
        await inter.send(echo_value)


@bot.command()
async def load(inter, extension):
    if inter.author.id in config.devs:
        bot.load_extension(f"cogs.{extension}")
        await inter.send("Загружаю ког...")


@bot.command()
async def unload(inter, extension):
    if inter.author.id in config.devs:
        bot.unload_extension(f"cogs.{extension}")
        await inter.send("Выгружаю ког...")


@bot.command()
async def reload(inter, extension):
    if inter.author.id in config.devs:
        bot.unload_extension(f"cogs.{extension}")
        bot.load_extension(f"cogs.{extension}")
        await inter.send("Перезагружаю ког...")


@bot.command()
async def clear(inter, count: int):
    if inter.author.id in config.devs:
        if not (1 <= count <= 500):
            await inter.send("Ограничение")
            return

        await inter.channel.purge(limit=count)

        await inter.send("Успешно...")


bot.run(config.token)
