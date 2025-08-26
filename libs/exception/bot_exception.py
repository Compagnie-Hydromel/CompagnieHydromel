class BotException(Exception):
    def __init__(self, message: str = "") -> None:
        self.__message = message

    @property
    def message(self) -> str:
        return self.__message
