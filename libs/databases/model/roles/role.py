from libs.databases.repository.database_access_implement import DatabaseAccessImplement
from libs.databases.repository.sqlite.sqlite_access import SqliteAccess
from libs.exception.role.level_should_be_greater_than_one_exception import LevelShouldBeGreaterThanOneException
from libs.exception.role.role_not_exist_exception import RoleNotExistException


class Role:
    """This class is designed to represent a role in the database.
    """
    __discord_id : str
    __db_access : DatabaseAccessImplement

    def __init__(self, discord_id : str) -> None:
        """This method is designed to initialize the User class.

        Args:
            discord_id (str): The discord id of the user.

        Raises:
            RoleNotExistException: If the role does not exist in the database.
        """
        self.__discord_id = discord_id
        self.__db_access = SqliteAccess()

        if not self.__db_access.is_role_exist(self.__discord_id):
            raise RoleNotExistException()
        
    def __eq__(self, value: object) -> bool:
        """This method is designed to compare two roles.

        Args:
            value (object): The value to compare.

        Returns:
            bool: True if the roles are equals, False otherwise.
        """
        return self.__discord_id == value.discord_id and self.level == value.level

    @property
    def discord_id(self) -> str:
        """This method is designed to get the discord id of the user.

        Returns:
            str: The discord id of the user.
        """
        return self.__discord_id

    @property
    def level(self) -> int:
        """This method is designed to get the level which the user need to get the role.

        Returns:
            int: The level of the user.
        """
        return self.__db_access.get_role_level(self.__discord_id)
    
    @level.setter
    def level(self, value: int) -> None:
        """This method is designed to set the level of the user.

        Args:
            value (int): The level of the user.
        
        Raises:
            LevelShouldBeGreaterThanOneException: If the level is less than 1.
        """
        if value < 1:
            raise LevelShouldBeGreaterThanOneException()
        self.__db_access.update_role_level(self.__discord_id, value)