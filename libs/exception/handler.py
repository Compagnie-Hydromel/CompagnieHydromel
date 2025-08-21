import traceback
from libs.exception.bot_exception import BotException
from libs.log import Log
from MIWOS.libs.exceptions.validation_exception import ValidationException


class Handler:
    """Handler class for handling exception
    """

    def response_handler(self, exception: Exception, stacktrace: str) -> str:
        """Response handler for exception to convert exception to response message

        Args:
            exception (Exception): the exceptions throws
            stacktrace (str): the stacktrace of the exception to log if needed

        Returns:
            str: the response message
        """
        if isinstance(exception, BotException):
            return exception.message
        elif isinstance(exception, ValidationException):
            return str(exception)
        else:
            return self.__default(stacktrace)

    def __default(self, stacktrace: str) -> str:
        """Default response for exception

        Args:
            stacktrace (str): the stacktrace of the exception to log if needed

        Returns:
            str: the default response message
        """
        Log.error(stacktrace)
        return "An error occurred, please try again later."
