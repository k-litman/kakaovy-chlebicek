from dataclasses import dataclass, field
import discord
from discord.ext import commands
from typing import Dict
from asyncio import sleep
from os import remove, path

from src.youtube.download import YTDLSource

intents = discord.Intents.all()


@dataclass
class Guild:
    playing: bool = False
    queue: list[tuple[str, str]] = field(default_factory=lambda: [])


class KakaovyChlebicek(commands.Bot):
    guild_dict: Dict[int, Guild] = {}

    def __init__(self, ffmpeg_path):
        super().__init__(command_prefix='/', intents=intents)

        @self.command(name='ping')
        async def ping(ctx):
            await ctx.message.reply('Pong')

        @self.command(name='play')
        async def play(ctx, *, url):
            guild_id = ctx.message.guild.id
            if not ctx.message.author.voice:
                await ctx.send(f'{ctx.message.author.name} - no jak mam grac jezeli ciebie na kanale nie ma?!')
                return
            elif ctx.message.guild.voice_client is not None:
                filename, title = await YTDLSource.from_url(url, loop=self.loop)
                self.guild_dict[guild_id].queue.append((filename, title))
                await ctx.send(f'{ctx.message.author.name} - no jak ja juz gram, dodaje do kolejki: {title}')
                return
            else:
                await ctx.message.author.voice.channel.connect()

            filename, title = await YTDLSource.from_url(url, loop=self.loop)
            self.guild_dict[guild_id].queue.append((filename, title))
            while self.guild_dict[guild_id].queue:
                filename, title = self.guild_dict[guild_id].queue.pop(0)
                print(filename, title)
                # self.guild_dict[guild_id].queue.pop(0)

                server = ctx.message.guild
                voice_channel = server.voice_client

                async with ctx.typing():
                    if not path.exists(filename):
                        filename, title = await YTDLSource.from_url(url, loop=self.loop)
                    voice_channel.play(discord.FFmpegPCMAudio(executable=ffmpeg_path, source=filename))
                await ctx.send(f'gram: {title}')
                while voice_channel.is_playing():
                    await sleep(0.1)
                remove(filename)

                print(self.guild_dict[guild_id].queue)

            try:
                await ctx.message.guild.voice_client.disconnect()
            except Exception:
                pass

        @self.command(name='stop')
        async def stop(ctx):
            guild_id = ctx.message.guild.id
            voice_client = ctx.message.guild.voice_client
            if voice_client.is_connected():
                await voice_client.disconnect()

            self.guild_dict[guild_id].queue.clear()

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

    async def on_ready(self):
        print('Bot loaded')
        for guild in self.guilds:
            print(guild.name)
            self.guild_dict[guild.id] = Guild()
        print(self.guild_dict)
        await self.change_presence(activity=discord.Game(name='haha ja dzialam na serwerze!'))
