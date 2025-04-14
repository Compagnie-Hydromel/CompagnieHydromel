# Compagnie Hydromel

## Directory

*Can be updated in the future*

```
.
├── cogs                    # Collection of commands
│   ├── archiveuse          # Archiveuse cog
│   |   └── profile.py
│   ├── menestrel           # Menestrel cog 
│   |   └── play.py
│   └── barman              # Barman cog
│       └── bar_commands.py
├── data                    # All things that's not code
│   ├── databases
│   ├── font
│   └── img
├── docs                    # Folder with the documentation
├── libs                    # Personnal librairies
├── tests                   # Folder containing automated tests
├── bot.py                  # Bot base file, used to start the bot
├── requirements.txt        # File containing all required dependencies.
├── databases.db            # Databases containing user, wallpaper, badge, ect... (if using sqlite)
├── LICENSE
└── README.md
```

## Prerequisites

Before starting the Bot, you'll need to modify/create some files, create the 3 Bot on Discord Developer Portal and make a basic discord test server to make it work and to use it.

First, let's start with the files needed to be modified:
- In the root folder of the discord bot, create a file named **.env** with the informations below (remember to replace where it says **COMPLETE_IT** with the real informations)
```env
BARMAN_TOKEN = "COMPLETE_IT"
MENESTREL_TOKEN = "COMPLETE_IT"
ARCHIVEUSE_TOKEN = "COMPLETE_IT"

# https://www.blagues-api.fr/
BLAGUES_API_KEY = "COMPLETE_IT"

# https://github.com/praw-dev/praw
REDDIT_CLIENT_ID = "COMPLETE_IT"
REDDIT_CLIENT_SECRET = "COMPLETE_IT"

# Use it only if you wanna use menestrel as a music player in voice channel
# Need activate music in configuration
# https://dsharpplus.github.io/DSharpPlus/articles/audio/lavalink/setup.html
LAVALINK_PASSWORD = "COMPLETE_IT"
```

After this, let's create a basic Discord Server:
- Open Discord App or use [Discord Web](https://discord.com/app)
- Click on the **+** icon then click on **Create My Own** and after **For me and my friends**. Now give it a name and after click on **Create**.

Let's now create the 3 Bot on Discord Developer Portal and invite it on the Discord Server created before. For this, follow [this tutorial](https://docs.pycord.dev/en/stable/discord.html).

`WARNING`: Create 3 bot to have 3 individual token

## Installation

If you want to make the bot work, you'll need some things.

- For Linux users
``` bash
sudo apt install python3.11
```

- For Windows or mac users
    - [Download Python 3.11](https://www.python.org/downloads/release/python-3114/)

Now, not all things are installed but these ones are for both OS. Open a **CMD/Terminal** and copy/paste these commands below. This command will automatically install the required dependencies for this project.
To manage dependency you need to use [python-venv](https://packaging.python.org/en/latest/guides/installing-using-pip-and-virtual-environments/)
```bash
# install virtual env
python3 -m pip install virtualenv 
# create env folder
python3 -m venv env 
# enable the environement with
source env/bin/activate
# WARNING: use this for windows
.\env\Scripts\Activate.ps1
# Too check if it work execute 'pip list' and it will be almost empty if you were already owning some python package or not
```
now you can install the dependency with
```bash
python3 -m pip install -r requirements.txt
```

`WARNING`: check that python3 is the good version of python you want to use. Don't hesitate to specifies the version with python3.* commands

## Usage
```bash
# To start the bot
./bot.sh

# If doesn't work in like a screen session
bash bot.sh
# or 
zsh bot.sh
```

You can also use the command below to start the bot on by one
```bash
# To start the barman
python3 bot.py barman

# To start the menestrel
python3 bot.py menestrel

# To start the archiveuse
python3 bot.py archiveuse
```

## Avoid users to see admin commands 
use the discord default slash commands permission system
https://discord.com/blog/slash-commands-permissions-discord-apps-bots

## Configuration
You can configure the bot with the **config.yml** file in the root folder of the bot. You can change the prefix, the language, the music, the reddit and the database. The file is generate automatically if it doesn't exist.

exemple of config.yml
```yaml
...
reactions:
  enable: true
  list:
  - action: accept_rules
    emoji: ✅
    message_id: 1139191289737388113
    role_id: 0
...
```

### Music

To use the music feature refer to this documentation [here](https://github.com/Compagnie-Hydromel/CompagnieHydromel/wiki/Lavalink-server-integration)

## Usefull links
- https://docs.pycord.dev/en/stable/
- https://discordpy.readthedocs.io/en/stable/
- https://docs.python.org/3/
- https://wavelink.dev/en/v1.3.5/index.html

## Contributing
Please open an issue first to discuss what you would like to change.
Format code with pep8 
```bash
./bot.sh format
# or
./bot.sh check-format
```

## License
[MIT](LICENSE)
