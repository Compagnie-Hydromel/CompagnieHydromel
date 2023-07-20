from enum import Enum
import datetime

class LogType(Enum):
    INFO = "INFO"
    ERROR = "ERROR"
    WARNING = "WARNING"
    MESSAGE = "MESSAGE"

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