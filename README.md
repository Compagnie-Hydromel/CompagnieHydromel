# Compagnie Hydromel

## Directory

*Can be updated in the future*

```
.
├── cogs                # Collection of commands
│   └── Music.py
├── data                # All things that's not code
│   ├── databases
│   ├── font
│   └── img
├── docs                # Folder with the documentation
├── libs                # Personnal librairies
├── tests               # Folder containing automated tests
├── bot.py              # Bot base file, used to start the bot
├── requirements.txt    # File containing all required dependencies.
├── databases.db        # Databases containing user, wallpaper, badge, ect... (if using sqlite)
├── LICENSE
└── README.md
```

## Prerequisites

Before starting the Bot, you'll need to modify/create some files, create a Bot on Discord Developer Portal and make a basic discord server to make it work and to use it.

First, let's start with the files needed to be modified:
- In the root folder of the discord bot, create a file named **.env** with the informations below (remember to replace where it says **COMPLETE_IT** with the real informations)
``` Env
BARMAN_TOKEN = "COMPLETE_IT"
MENESTREL_TOKEN = "COMPLETE_IT"
ARCHIVEUSE_TOKEN = "COMPLETE_IT"
```

After this, let's create a basic Discord Server:
- Open Discord App or use [Discord Web](https://discord.com/app)
- Click on the **+** icon then click on **Create My Own** and after **For me and my friends**. Now give it a name and after click on **Create**.

Let's now create the Bot on Discord Developer Portal and invite it on the Discord Server created before. For this, follow [this tutorial](https://docs.pycord.dev/en/stable/discord.html).

## Installation

If you want to make the bot work, you'll need some things.

- For Linux users
``` bash
sudo apt install python3.11
```

- For Windows users
    - [Download Python 3.11](https://www.python.org/downloads/release/python-3114/)

Now, not all things are installed but these ones are for both OS. Open a **CMD/Terminal** and copy/paste these commands below. This command will automatically install the required dependencies for this project.
```bash
python -m pip install requirements.txt
```

## TODO 

- [ ] Archiveuse
  - [x] Add point when texting 
  - [ ] Add point when in vocal
  - [x] Level up
  - [x] Profile
    - [x] Dynamic name 
    - [x] Dynamic username
    - [x] Dynamic pp
    - [x] Wallpaper show by selecting
    - [x] change text color
    - [x] change bar color
    - [x] display badge
  - [ ] Buy wallpaper 
  - [ ] Add wallpaper as admin 
  - [ ] List wallpaper owned 
  - [ ] List all wallpaper
  - [ ] Obtain wallpaper passing level
  - [ ] Get smartcoin (/iq for the commands)
  - [ ] most level up player commands
- [ ] Barman 
  - [ ] log almost everything 
  - [ ] help command
  - [ ] beer command
  - [ ] hydromel command
  - [ ] water command
  - [ ] non alholic beer
  - [ ] sex command
  - [ ] root command 
    - [ ] clear 
    - [ ] add root
    - [ ] broacast 
    - [ ] authorize command in channel
  - [ ] meme channel 
  - [ ] dynamic server banner with vocal channel
  - [ ] reaction add role
- [ ] Menestrel 
  - [ ] Play
  - [ ] Stop
  - [ ] Wait list 
  - [ ] Next
  - [ ] Admin lock