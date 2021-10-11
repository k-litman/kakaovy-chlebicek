import youtube_dl
import discord
import asyncio

youtube_dl.utils.bug_reports_message = lambda: ''

ytdl_format_options = {
    'format': 'bestaudio/best',
    'restrictfilenames': True,
    'noplaylist': True,
    'nocheckcertificate': True,
    'ignoreerrors': False,
    'logtostderr': False,
    'quiet': True,
    'no_warnings': True,
    'default_search': 'auto',
    'source_address': '0.0.0.0', # bind to ipv4 since ipv6 addresses cause issues sometimes
    'cachedir': False
}

ffmpeg_options = {
        'options': '-vn',
    }

ytdl = youtube_dl.YoutubeDL(ytdl_format_options)


class NotFoundError(Exception):
    pass


class FetchError(Exception):
    pass


class YTDLSource(discord.PCMVolumeTransformer):
    def __init__(self, ctx, source, *, data, volume=0.5):
        super().__init__(source, volume)
        self.data = data
        self.title = data.get('title')
        self.url = data.get('url')
        self.requester = ctx.author

    @classmethod
    async def create(cls, ctx, search, *, loop=None):
        loop = loop or asyncio.get_event_loop()
        data = await loop.run_in_executor(None, lambda: ytdl.extract_info(search, download=False, process=False))

        if not data:
            raise NotFoundError(f'nie znaleziono nic szukajac "{search}" :c')

        if 'entries' in data:
            data = data['entries'][0]

        url = data['webpage_url']
        data = await loop.run_in_executor(None, lambda: ytdl.extract_info(url, download=False))

        if not data:
            raise FetchError(f'Error with fetching {url=}')

        if 'entries' in data:
            data = data['entries'][0]

        return cls(ctx, discord.FFmpegPCMAudio(data['url'], **ffmpeg_options), data=data)
