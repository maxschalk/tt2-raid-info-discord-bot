from src.constants import REGEX_CONTENT


def full_username(user):
    return f"{user.display_name}#{user.discriminator}"


def seed_data_filename(from_msg_content):
    matches = REGEX_CONTENT.match(from_msg_content)

    seed_date = matches.group(1).replace('/', '')

    suffix = ".json"

    return f"raid_seed_{seed_date}{suffix}"
