from libs.config import Config

class Handler:
    def __init__(self) -> None:
        self.__config = Config()
        
    def response_handler(self, exception: Exception) -> str:
        pass