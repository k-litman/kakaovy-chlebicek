from os import getenv
from dotenv import load_dotenv

from src.discord.bot import KakaovyChlebicek


def main():
    load_dotenv()
    TOKEN = getenv('DISCORD_TOKEN')

    bot = KakaovyChlebicek()
    bot.run(TOKEN)


if __name__ == '__main__':
    main()
