from libs.databases.badge import Badge
from libs.databases.database_access_implement import DatabaseAccessImplement
from libs.databases.sqlite.sqlite_access import SqliteAccess


class Badges:
    """This class is designed to manage a lot of badges.
    """
    __db_access : DatabaseAccessImplement

    def __init__(self) -> None:
        self.__db_access = SqliteAccess()
    
    def create_list_badges_by_list_name(self, list_name: list[str]) -> list[Badge]:
        """This method is designed to create a list of badges by a list of name.

        Args:
            list_name (list[str]): A list of badge name.

        Returns:
            list[Badge]: A list of Badge object.
        """
        list_of_badges = []

        for badge_name in list_name:
            list_of_badges.append(Badge(badge_name))

        return list_of_badges