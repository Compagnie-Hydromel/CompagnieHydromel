from libs.databases.repository.database_access_implement import DatabaseAccessImplement
from libs.databases.repository.sqlite.sqlite_access import SqliteAccess
from libs.databases.model.user.user import User


class Users:
    """This class is designed to manage many users.
    """
    __db_access : DatabaseAccessImplement
    
    def __init__(self) -> None:
        """This method is designed to initialize the Users class.
        """
        self.__db_access = SqliteAccess()

    @property
    def get_top_users(self) -> list[User]:
        """This method is designed to get the top users.

        Returns:
            list[User]: A list of User object.
        """
        return self.__create_list_of_users_by_list_user_name(self.__db_access.get_top_users())
    
    @property
    def get_most_smart_users(self) -> list[User]:
        """This method is designed to get the most smart users.

        Returns:
            list[User]: A list of User object.
        """
        return self.__create_list_of_users_by_list_user_name(self.__db_access.get_most_smart_users())
    
    @property
    def get_root_users(self) -> list[User]:
        """This method is designed to get the root users.

        Returns:
            list[User]: The list of root users.
        """
        return self.__create_list_of_users_by_list_user_name(self.__db_access.get_root_users())
    
    @property
    def get_5_monthly_most_active_users(self) -> list[User]:
        """This method is designed to get the 5 monthly most active users.

        Returns:
            list[User]: A list of User object.
        """
        return self.__create_list_of_users_by_list_user_name(self.__db_access.get_5_monthly_most_active_users())
    
    @property
    def all(self) -> list[User]:
        """This method is designed to get all the users.

        Returns:
            list[User]: A list of User object.
        """
        return self.__create_list_of_users_by_list_user_name(self.__db_access.get_all_users())
    
    def __create_list_of_users_by_list_user_name(self, list_name: list[str]) -> list[User]:
        """This method is designed to create a list of User object by a list of user name.

        Args:
            list_name (list[str]): A list of user name.

        Returns:
            list[User]: A list of User object.
        """
        list_of_users = []

        for user in list_name:
            list_of_users.append(User(user))

        return list_of_users
