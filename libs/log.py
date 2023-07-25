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
    __log : str

    def __init__(self, message : str, type : LogType = LogType.INFO) -> None:
        self.__log = str(datetime.datetime.now()) + " ["+type.value+"] : " + message
        self.__print()
        self.__write_log()

    def __print(self):
        print(self.__log)

    def __write_log(self):
        with open("log.txt", "a") as log:
            log.write(self.__log + "\n")
            
    @staticmethod
    def logMessage(channel: discord.abc.Messageable, message: str, author: str, bot: str, onlyDm: bool = False):
        channelName = ""
        if isinstance(channel, discord.DMChannel):
            channelName = bot + " DM with " + author
        else: 
            channelName = channel.name
        if (onlyDm and isinstance(channel, discord.DMChannel)) or not onlyDm:
            Log("(" + channelName + ")" + author + ": " + message, LogType.MESSAGE)