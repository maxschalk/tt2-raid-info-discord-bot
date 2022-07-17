from discord.ext import commands

from src.bot.bot import setup_bot
from src.raid_seed_data_api.raid_seed_data_api import RaidSeedDataAPI
from src.utils import get_env

GUILD_NAME = get_env(key="GUILD_NAME")
SEEDS_CHANNEL_NAME = get_env(key="SEEDS_CHANNEL_NAME")

BOT_TOKEN = get_env(key='DISCORD_TOKEN')

DATA_PROVIDER = RaidSeedDataAPI(
    base_url=get_env(key="RAID_SEED_DATA_API_BASE_URL"),
    auth_key=get_env(key="RAID_SEED_DATA_API_AUTH_SECRET"))


def main():
    bot = commands.Bot(command_prefix='!')

    setup_bot(bot=bot,
              guild_name=GUILD_NAME,
              channel_name=SEEDS_CHANNEL_NAME,
              data_provider=DATA_PROVIDER)

    bot.run(BOT_TOKEN)


if __name__ == '__main__':
    main()
