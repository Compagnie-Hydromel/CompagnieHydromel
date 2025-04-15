from libs.databases.databases_selecter import DatabasesSelecter
from libs.databases.repository.database_access_implement import DatabaseAccessImplement
from libs.exception.role.level_should_be_greater_than_one_exception import LevelShouldBeGreaterThanOneException
from libs.exception.role.role_not_exist_exception import RoleNotExistException
from libs.exception.role.role_already_exist_exception import RoleAlreadyExistException
from libs.exception.role.role_level_already_exist_exception import RoleLevelAlreadyExistException


class Role:
    """This class is designed to represent a role in the database.
    """
    __discord_id: str
    __db_access: DatabaseAccessImplement

    def __init__(self, discord_id: str) -> None:
        """This method is designed to initialize the User class.

        Args:
            discord_id (str): The discord id of the user.

        Raises:
            RoleNotExistException: If the role does not exist in the database.
        """
        self.__discord_id = discord_id
        self.__db_access = DatabasesSelecter().databases

        if not self.__db_access.is_role_exist(self.__discord_id):
            raise RoleNotExistException()

    def __eq__(self, value: "Role") -> bool:
        """This method is designed to compare two roles.

        Args:
            value (object): The value to compare.

        Returns:
            bool: True if the roles are equals, False otherwise.
        """
        return self.__discord_id == value.discord_id and self.level == value.level

    @staticmethod
    def all() -> list["Role"]:
        """This method is designed to get all the roles in the database.

        Returns:
            list: A list with all the roles.
        """
        return Role.__create_list_of_role_by_list_role_discord_id(DatabasesSelecter().databases.get_all_roles())

    @staticmethod
    def by_level(self, level) -> "Role":
        """This method is designed to get a role by the level.

        Args:
            level (int): The level of the role.

        Returns:
            Role: The role.

        Raises:
            RoleNotExistException: If the role does not exist in the database.
        """
        if not DatabasesSelecter().databases.is_role_exist_by_level(level):
            raise RoleNotExistException()
        return Role(DatabasesSelecter().databases.get_role_discord_id_by_role_level(level))

    @staticmethod
    def add(discordId: str, level: int) -> None:
        """This method is designed to add a role in the database.

        Args:
            discordId (str): The discord id of the role.
            level (int): The level of the role.

        Raises:
            LevelShouldBeGreaterThanOneException: If the level is less than 1.
            RoleAlreadyExistException: If the role already exist in the database.
            RoleLevelAlreadyExistException: If the level already exist in the database.
        """
        if level < 1:
            raise LevelShouldBeGreaterThanOneException()
        elif DatabasesSelecter().databases.is_role_exist(discordId):
            raise RoleAlreadyExistException()
        elif DatabasesSelecter().databases.is_role_exist_by_level(level):
            raise RoleLevelAlreadyExistException()
        DatabasesSelecter().databases.add_role(discordId, level)

    @staticmethod
    def remove(discordId: str) -> None:
        """This method is designed to remove a role in the database.

        Args:
            discordId (str): The discord id of the role.
        """
        if not DatabasesSelecter().databases.is_role_exist(discordId):
            raise RoleNotExistException()
        DatabasesSelecter().databases.remove_role(discordId)

    @staticmethod
    def __create_list_of_role_by_list_role_discord_id(self, list_name: list[str]) -> list["Role"]:
        """This method is designed to create a list of role by a list of discord id.

        Args:
            list_name (list[str]): The list of discord id.

        Returns:
            list[Role]: A list of role.
        """
        list_of_role = []

        for role_name in list_name:
            list_of_role.append(Role(role_name))

        return list_of_role

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
