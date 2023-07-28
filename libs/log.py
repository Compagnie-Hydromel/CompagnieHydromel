from enum import Enum
import datetime

import discord

class LogType(Enum):
    INFO = "INFO"
    ERROR = "ERROR"
    WARNING = "WARNING"
    MESSAGE = "MESSAGE"
    COMMAND = "COMMAND"

class Log():
    """This class is designed to manage the log.
    """
    __log : str

    def __init__(self, message : str, type : LogType = LogType.INFO) -> None:
        """This method is designed to initialize the Log class.

        Args:
            message (str): The message to log.
            type (LogType, optional): The type of log (LogType.INFO, LogType.ERROR, etc...). Defaults to LogType.INFO.
        """
        self.__log = str(datetime.datetime.now()) + " ["+type.value+"] : " + message
        self.__print()
        self.__write_log()

    def __print(self):
        """This method is designed to print the log.
        """
        print(self.__log)

    def __write_log(self):
        """This method is designed to write into the log file.
        """
        with open("log.txt", "a") as log:
            log.write(self.__log + "\n")
            
    @staticmethod
    def logMessage(channel: discord.abc.Messageable, message: str, author: str, bot: str, onlyDm: bool = False):
        """This method is designed to log a message.

        Args:
            channel (discord.abc.Messageable): channgel of the message.
            message (str): The message.
            author (str): The author of the message.
            bot (str): The bot who receive the message.
            onlyDm (bool, optional): If the bot want to log only dmMessage. Defaults to False.
        """
        channelName = ""
        if isinstance(channel, discord.DMChannel):
            channelName = bot + " DM with " + author
        else: 
            channelName = channel.name
        if (onlyDm and isinstance(channel, discord.DMChannel)) or not onlyDm:
            Log("(" + channelName + ")" + author + ": " + message, LogType.MESSAGE)