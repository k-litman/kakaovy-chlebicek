import discord
from discord.ext import commands

intents = discord.Intents.all()


class KakaovyChlebicek(commands.Bot):
    playing = False

    def __init__(self):
        super().__init__(command_prefix='/', intents=intents)

        @self.command(name='ping')
        async def ping(ctx):
            await ctx.message.reply('Pong')

