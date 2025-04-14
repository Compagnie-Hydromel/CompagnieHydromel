class BotException(Exception):
    def __init__(self, message: str = "") -> None:
        self.__exception = self.__class__.__name__
        self.__message = message

    def __str__(self) -> str:
        return self.__exception

    @property
    def message(self) -> str:
        return self.__message
