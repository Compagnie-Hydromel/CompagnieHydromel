import traceback
from libs.config import Config
from libs.exception.bot_exception import BotException
from libs.log import Log, LogType

class Handler:
    """Handler class for handling exception
    """    
    def __init__(self) -> None:
        """Constructor of Handler class
        """        
        self.__config = Config()
        self.__response_exception = self.__config.value["exception_response"]
        
    def response_handler(self, exception: Exception, stacktrace: str) -> str:
        """Response handler for exception to convert exception to response message

        Args:
            exception (Exception): the exceptions throws
            stacktrace (str): the stacktrace of the exception to log if needed

        Returns:
            str: the response message
        """
        if isinstance(exception, BotException):
            match(str(exception)):
                # wallpaper exception
                case "WallpaperNotExistException":
                    return self.__response_exception["wallpaper_not_exist"]
                case "WallpaperAlreadyExistException": 
                    return self.__response_exception["wallpaper_already_exist"]
                case "WallpaperNotPossededException":
                    return self.__response_exception["wallpaper_not_posseded"]
                case "ColorNotCorrectException":
                    return self.__response_exception["color_not_correct"]
                case "NotEnougtSmartpointException":
                    return self.__response_exception["not_enougt_smartpoint"]
                case "WallpaperAlreadyPossededException":
                    return self.__response_exception["wallpaper_already_posseded"]
                case "WallpaperCannotBeBuyedException":
                    return self.__response_exception["wallpaper_cannot_be_buyed"]
                case "WallpaperIsNotDownloadableException":
                    return self.__response_exception["unable_to_download_image"]
                case "WallpaperIsNotDownloadableException":
                    Log(stacktrace, LogType.ERROR)
                    return self.__response_exception["unable_to_download_image"]
                # music exception
                case "AlreadyPlayingException": 
                    return self.__response_exception["already_playing"]
                case "NotConnectedToVoiceChannelException":
                    return self.__response_exception["not_connected_to_voice_channel"]
                case "NoResultsFoundException":
                    return self.__response_exception["no_results_found"]
                case "NoPlayingInstanceException":
                    return self.__response_exception["not_playing_music"]
                case "NothingLeftInBackQueueException":
                    return self.__response_exception["nothing_left_in_previous_queue"]
                case "NothingLeftInQueueException":
                    return self.__response_exception["nothing_left_in_queue"]
                case "NoMusicPlaying":
                    return self.__response_exception["not_playing_music"]
                case "ProfileLayoutNotExist":
                    return self.__response_exception["profile_layout_not_exist"]
                case "ProfileLayoutAlreadyExist":
                    return self.__response_exception["profile_layout_already_exist"]
                case "CannotRemoveDefaultProfileLayout":
                    return self.__response_exception["cannot_remove_default_profile_layout"]
                case _:
                    return self.__default(stacktrace)
        else:
            return self.__default(stacktrace)
        
    def __default(self, stacktrace: str) -> str:
        """Default response for exception

        Args:
            stacktrace (str): the stacktrace of the exception to log if needed

        Returns:
            str: the default response message
        """        
        Log(stacktrace, LogType.ERROR)
        return self.__response_exception["default"]
