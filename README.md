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