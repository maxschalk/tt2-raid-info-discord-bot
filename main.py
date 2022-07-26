from discord.ext import commands

from src.bot.bot import setup_bot
from src.raid_seed_data_api.raid_seed_data_api import RaidSeedDataAPI
from src.stage import STAGE
from src.utils.get_env import get_env

DISCORD_GUILD_NAME = get_env(key="DISCORD_GUILD_NAME")
DISCORD_CHANNEL_NAME = get_env(key="DISCORD_CHANNEL_NAME")

DISCORD_BOT_TOKEN = get_env(key='DISCORD_BOT_TOKEN')

DATA_PROVIDER = RaidSeedDataAPI(
    base_url=get_env(key="RAID_SEED_DATA_API_BASE_URL"),
    auth_key=get_env(key="RAID_SEED_DATA_API_AUTH_SECRET"))


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
