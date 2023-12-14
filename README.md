# Based Bot

WARNING: this bot is currently not based because it runs on OpenAI's GPT (very woke to the point it is not helpful). I am waiting for the Grok API to drop. Until then, the bot can still do a lot of helpful things for your discord: like get sports scores and betting odds, tell you about apex maps, and more stuff.

type `$based` in the chat to see a list of commands

## Self Hosting

Install python

`git clone https://github.com/rustaceanrob/based.git`

`cd based`

Set a lot of environment variables in a folder called `.env`. You'll need an `APEX_TOKEN`, `OPEN_AI_TOKEN`, `METAPHOR_TOKEN` from Metaphor, `SPORTS_TOKEN` from The Odds API, and lastly your discord token as `DISCORD_TOKEN`

`pip install -r requirements.txt`

`python3 main.py`
