from discord.ext import commands

from src.bot.bot import setup_bot
from src.domain.raid_seed_data_api import RaidSeedDataAPI
from src.utils.get_env import get_env
from src.utils.stage import STAGE

DISCORD_GUILD_NAME = get_env(key="DISCORD_GUILD_NAME")
DISCORD_CHANNEL_NAME = get_env(key="DISCORD_CHANNEL_NAME")

DISCORD_BOT_TOKEN = get_env(key='DISCORD_BOT_TOKEN')

DATA_PROVIDER = RaidSeedDataAPI()


def main():
    print(f"{STAGE=}")

    bot = commands.Bot(command_prefix='!')

    setup_bot(bot=bot,
              guild_name=DISCORD_GUILD_NAME,
              channel_name=DISCORD_CHANNEL_NAME,
              data_provider=DATA_PROVIDER)

    bot.run(DISCORD_BOT_TOKEN)


if __name__ == '__main__':
    main()
