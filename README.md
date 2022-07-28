# TT2 Raid Data Discord Bot

## Context

This repo is part of a bigger project concerning weekly raid data of GameHive's popular mobile game [Tap Titans 2](https://www.gamehive.com/games/tap-titans-2).

The weekly raid data for clans used to only be available on [GameHive's Discord Server](https://discord.gg/gamehive) in raw JSON format. The overarching project is an effort to make this data more accesible to players both programmatically (via API) or visually (via web app).

## Description

This Discord bot is the bridge between the original Discord server and the [TT2 Raid Info API](https://github.com/riskypenguin/tt2-raid-info-api).

Its core purpose is listening to messages in a specified channel, grabbing and `POST`ing raid seeds to the API which then provides standardized programmatic access to the data.

It provides convenience functionalities for interacting with the API, mainly creating, retrieving and deleting data.

It can also perform some basic utility commands on recent message like clearing reactions or deleting them entirely.

## Installation

1. Clone this repository:

   ```bash
   git clone https://github.com/riskypenguin/tt2-raid-info-discord-bot.git tt2-raid-info-discord-bot
   ```

2. Optional but recommended: Create and activate a [virtual environment](https://realpython.com/python-virtual-environments-a-primer/) with Python version 3.10

3. Install requirements

   ```bash
   pip install -r requirements.txt
   ```

## Usage

1. Create a [Discord bot account](https://discordpy.readthedocs.io/en/stable/discord.html), add it to your server and set the relevant credentials as an environment variable ([example](/.env.example)).

2. Create `.env` file and fill all environment variables ([example](/.env.example))

3. Run the bot locally

   ```bash
   python main.py
   ```

If the bot succesfully comes online it will log the following output:

```
STAGE=<Stage.PRODUCTION: 'prod'>
{BotUserName} has connected to Discord!
{BotUserName} connected to {GuildName}.#{ChannelName}
```

After a few seconds you should also see the bot user displayed among the online users in Discord.

### Commands

By default all commands require the user to have an 'admin' role.

- [!help]: display a list of all commands
- [!clear-reactions | !cr] [count: int = 1]: clear the reactions on a specified number of recent messages
- [!delete-messages | !del] [count: int = 1]: delete a specified number of recent messages
- [!process | !p]: process existing messages in the channel until an already processed message is found
  - processes raid seed messages only, not commands
  - deletes messages by the bot itself
- [!seed-identifiers | !sids]: get identifiers of all seeds currently available on the server
- [!seed | !s] [identifier: str]: get seed data for given identifier
- [!delete-seed | !ds] [identifier: str]: delete seed data for given identifier

## Project status & Roadmap

The bot is feature-complete for now.

I am currently working on a suite of unit tests for the bot interface and the internal logic.

## Contributing

Pull requests are welcome. For major changes, please open an issue first to discuss what you would like to change.

Please make sure to update tests as appropriate.

## License

[MIT](https://choosealicense.com/licenses/mit/)
