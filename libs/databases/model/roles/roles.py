from libs.databases.databases_selecter import DatabasesSelecter
from libs.databases.model.roles.role import Role
from libs.databases.repository.database_access_implement import DatabaseAccessImplement
from libs.exception.role.level_should_be_greater_than_one_exception import LevelShouldBeGreaterThanOneException
from libs.exception.role.role_already_exist_exception import RoleAlreadyExistException
from libs.exception.role.role_level_already_exist_exception import RoleLevelAlreadyExistException
from libs.exception.role.role_not_exist_exception import RoleNotExistException


class Roles:
    """This class is designed to get many role in the database.
    """
    __db_access: DatabaseAccessImplement

    def __init__(self) -> None:
        """This method is designed to initialize the Roles class.
        """
        self.__db_access = DatabasesSelecter().databases

    @property
    def all(self) -> list[Role]:
        """This method is designed to get all the roles in the database.

        Returns:
            list: A list with all the roles.
        """
        return self.__create_list_of_role_by_list_role_discord_id(self.__db_access.get_all_roles())

    def by_level(self, level) -> Role:
        """This method is designed to get a role by the level.

        Args:
            level (int): The level of the role.

        Returns:
            Role: The role.

        Raises:
            RoleNotExistException: If the role does not exist in the database.
        """
        if not self.__db_access.is_role_exist_by_level(level):
            raise RoleNotExistException()
        return Role(self.__db_access.get_role_discord_id_by_role_level(level))

    def add(self, discordId: str, level: int) -> None:
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
        elif self.__db_access.is_role_exist(discordId):
            raise RoleAlreadyExistException()
        elif self.__db_access.is_role_exist_by_level(level):
            raise RoleLevelAlreadyExistException()
        self.__db_access.add_role(discordId, level)

    def remove(self, discordId: str) -> None:
        """This method is designed to remove a role in the database.

        Args:
            discordId (str): The discord id of the role.
        """
        if not self.__db_access.is_role_exist(discordId):
            raise RoleNotExistException()
        self.__db_access.remove_role(discordId)

    def __create_list_of_role_by_list_role_discord_id(self, list_name: list[str]) -> list[Role]:
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
