from libs.databases.adaptaters.database_access_implement import DatabaseAccessImplement
from libs.databases.adaptaters.sqlite.sqlite_access import SqliteAccess
from libs.databases.profile_layout.profile_layout import ProfileLayout


class ProfileLayouts():
    """This class is designed to manage many ProfileLayouts.
    """
    __db_access : DatabaseAccessImplement
    
    def __init__(self) -> None:
        """This method is designed to initialize the ProfileLayouts class.
        """
        self.__db_access = SqliteAccess()
        
    @property
    def get_all_profile_layouts(self) -> list[ProfileLayout]:
        """This method is designed to get all profile layouts.

        Returns:
            list[ProfileLayouts]: A list of profile layout.
        """
        return self.__create_list_of_profile_layout_by_list_profile_layout_name(self.__db_access.get_all_profile_layouts_name())
    
    def __create_list_of_profile_layout_by_list_profile_layout_name(self, list_name: list[str]) -> list[ProfileLayout]:
        """This method is designed to create a list of ProfileLayout object by a list of profile layout name.

        Args:
            list_name (list[str]): A list of profile layout name

        Returns:
            list[ProfileLayout]: A list of ProfileLayout object.
        """
        list_of_profile_layout = []

        for profile_layout_name in list_name:
            list_of_profile_layout.append(ProfileLayout(profile_layout_name))

        return list_of_profile_layout