from dotenv import load_dotenv

from src.bot import bot

load_dotenv()


def main():
    bot.main()


if __name__ == '__main__':
    main()
