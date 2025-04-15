from libs.databases.databases_selecter import DatabasesSelecter
from libs.databases.repository.database_access_implement import DatabaseAccessImplement
from libs.exception.badge.badge_not_exist_exception import BadgeNotExistException


class Badge:
    """This class is designed to manage a badge.
    """
    __badge_name: str
    __db_access: DatabaseAccessImplement

    def __init__(self, badge_name: str) -> None:
        """This method is the constructor of the class.

        Args:
            badge_name (str): The name of the badge.

        Raises:
            BadgeNotExistException: If the badge doesn't exist.
        """
        self.__badge_name = badge_name
        self.__db_access = DatabasesSelecter().databases

        if not self.__db_access.is_badge_exist(self.__badge_name):
            raise BadgeNotExistException

    @staticmethod
    def create_list_badges_by_list_name(list_name: list[str]) -> list["Badge"]:
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
