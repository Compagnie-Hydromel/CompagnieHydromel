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
├── assets                   # All things that's not code
│   ├── fonts
│   └── img
├── libs                    # Librairies
│   ├── image_factory       # Image factory to create profile picture
│   ├── databases           # Database management
│   ├── music               # Music management
│   ├── utils               # Utils functions
│   └── exceptions          # Custom application exceptions
├── tests                   # Folder containing automated tests
├── bot.py                  # Bot base file, used to start the bot
├── requirements.txt        # File containing all required dependencies.
├── LICENSE
└── README.md
```

## Prerequisites

- [Python 3.13.2 or higher](https://www.python.org/downloads/release/python-3132/)
- [Python-pip](https://pip.pypa.io/en/stable/installation/)
- [python-venv](https://packaging.python.org/en/latest/guides/installing-using-pip-and-virtual-environments/)

Before starting the Bot, you'll need to modify/create some files, create the 3 Bot on Discord Developer Portal and make a basic discord test server to make it work and to use it.

First, let's start with the files needed to be modified:
- In the root folder of the discord bot, copy **.env.example** to **.env** and fill in the information (Databases, Discord Bot Tokens, Lavalink Password, etc.).
- Open Discord App or use [Discord Web](https://discord.com/app)
- Click on the **+** icon then click on **Create My Own** and after **For me and my friends**. Now give it a name and after click on **Create**.

Let's now create the 3 Bot on Discord Developer Portal and invite it on the Discord Server created before. For this, follow [this tutorial](https://docs.pycord.dev/en/stable/discord.html).

`WARNING`: Create 3 bot to have 3 individual token

## Installation

```bash
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

```bash
python3 bot.py migrate

# rollback migration if needed
python3 bot.py rollback
```

`WARNING`: check that python3 is the good version of python you want to use. Don't hesitate to specifies the version with python3.* commands

## Usage
```bash
# To start all the bot
python3 bot.py

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

## Usefull links
- https://docs.pycord.dev/en/stable/
- https://discordpy.readthedocs.io/en/stable/
- https://docs.python.org/3/
- https://wavelink.dev/en/v1.3.5/index.html

## Contributing
Please open an issue first to discuss what you would like to change.
Format code with pep8 
```bash
python3 bot.py format
# or
python3 bot.py check-format
```
you can use vscode extension like [Python autopep8](https://marketplace.visualstudio.com/items?itemName=ms-python.autopep8) to format your code automatically.

## License
[MIT](LICENSE)
