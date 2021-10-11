from dataclasses import dataclass, field
import discord
from discord.ext import commands
import asyncio
from async_timeout import timeout
from os import remove, path
import random

from src.youtube.download import YTDLSource

intents = discord.Intents.all()


@dataclass
class Guild:
    playing: bool = False
    queue: list[tuple[str, str]] = field(default_factory=lambda: [])
    loop: bool = False


class Queue(asyncio.Queue):
    def clear(self):
        self._queue.clear()

    def shuffle(self):
        random.shuffle(self._queue)

    def remove(self, index):
        del self._queue[index]


class Player:
    def __init__(self, ctx):
        self.bot = ctx.bot

        # properties
        self.loop = False
        self.volume = 0.5

        self.current = None
        self.queue = Queue()
        self.next = asyncio.Event()

        self.player = self.bot.create_task(self.player_task())

    def __del__(self):
        self.player.cancel()

    async def player_task(self):
        while True:
            self.next.clear()

            if not self.loop:
                # one second offset between end of song and disconnection
                try:
                    async with timeout(1):
                        self.current = await self.queue.get()
                except asyncio.TimeoutError:
                    self.bot.loop.create_task(self.stop())
                    return

            self.current.source.volume = self.volume
            # self.voice.pl

            await self.next.wait()

    async def stop(self):
        self.queue.clear()


class KakaovyChlebicek(commands.Bot):
    def __init__(self, ffmpeg_path):
        super().__init__(command_prefix='$', intents=intents)
        self.players = {}

        @self.command(name='ping')
        async def ping(ctx):
            await ctx.message.reply('Pong')

        @self.command(name='play')
        async def play(ctx, *, search):
            player = self.players.get(ctx.guild.id)
            if not player:
                player = Player(ctx)
                self.players[ctx.guild.id] = player




        @self.command(name='stop')
        async def stop(ctx):
            if not ctx.voice_client:
                await ctx.send('no jak mam stopowac jak nie gram')
                return

            ctx.

        @self.command(name='queue')
        async def queue(ctx):
            guild_id = ctx.message.guild.id
            if self.guild_dict[guild_id].queue:
                embed = discord.Embed(title='kolejka', description='no kolejka a co innego', colour=0x00ff00)
                for i, t in enumerate(self.guild_dict[guild_id].queue):
                    embed.add_field(name=f'{i+1}: ', value=t[1], inline=False)
                await ctx.send(embed=embed)
            else:
                await ctx.send('kolejka jest pusta!')

        @self.command(name='skip')
        async def skip(ctx):
            voice_client = ctx.message.guild.voice_client
            if voice_client is not None:
                voice_client.stop()
                await ctx.send('juz skipuje')
            else:
                await ctx.send('ale co chcesz skipowac jak nie gram')

        @self.command(name='loop')
        async def loop(ctx):
            guild_id = ctx.message.guild.id
            self.guild_dict[guild_id].loop = not self.guild_dict[guild_id].loop
            await ctx.send(f'teraz {"nie " if not self.guild_dict[guild_id].loop else ""} loopuje')

    async def on_ready(self):
        print('Bot loaded')
        for guild in self.guilds:
            print(guild.name)
            self.guild_dict[guild.id] = Guild()
        print(self.guild_dict)
        await self.change_presence(activity=discord.Game(name='[$] haha ja dzialam na serwerze!'))

    async def on_guild_join(self, guild):
        print(f'joined {guild.name}')
        self.guild_dict[guild.id] = Guild()
