from libs.databases.database_access_implement import DatabaseAccessImplement
from libs.databases.sqlite.sqlite_access import SqliteAccess
from libs.exception.badge_not_exist_exception import BadgeNotExistException


class Badge:
    """This class is designed to manage a badge.
    """
    __badge_name : str
    __db_access : DatabaseAccessImplement
    
    def __init__(self, badge_name : str) -> None:
        """This method is the constructor of the class.

        Args:
            badge_name (str): The name of the badge.

        Raises:
            BadgeNotExistException: If the badge doesn't exist.
        """        
        self.__badge_name = badge_name
        self.__db_access = SqliteAccess()

        if not self.__db_access.is_badge_exist(self.__badge_name):
            raise BadgeNotExistException
    
    @property
    def name(self) -> str:
        """This method is designed to get the name of the badge.

        Returns:
            str: The name of the badge.
        """
        return self.__badge_name

    @property
    def url(self) -> str:
        """This method is designed to get the url of the badge.

        Returns:
            str: The url of the badge.
        """
        return self.__db_access.get_badge_url(self.__badge_name)