from os import getenv
from dotenv import load_dotenv

from src.discord.bot import KakaovyChlebicek


def main():
    load_dotenv()
    TOKEN = getenv('DISCORD_TOKEN')
    FFMPEG_PATH = getenv('FFMPEG_PATH')

    bot = KakaovyChlebicek(FFMPEG_PATH)
    bot.run(TOKEN)


if __name__ == '__main__':
    main()
