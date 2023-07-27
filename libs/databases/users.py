from libs.databases.database_access_implement import DatabaseAccessImplement
from libs.databases.sqlite.sqlite_access import SqliteAccess
from libs.databases.user import User


class Users:
    __db_access : DatabaseAccessImplement
    
    def __init__(self) -> None:
        self.__db_access = SqliteAccess()

    def get_top_users(self) -> list:
        return self.__create_list_of_users_by_list_user_name(self.__db_access.get_top_users())
    
    def __create_list_of_users_by_list_user_name(self, list_name: list) -> list:
        list_of_users = []

        for user in list_name:
            list_of_users.append(User(user))

        return list_of_users
