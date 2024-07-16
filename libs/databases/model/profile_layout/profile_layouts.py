from libs.databases.databases_selecter import DatabasesSelecter
from libs.databases.dto.layout import Layout
from libs.databases.repository.database_access_implement import DatabaseAccessImplement
from libs.databases.model.profile_layout.profile_layout import ProfileLayout
from libs.exception.profile_layout.cannot_remove_default_profile_layout import CannotRemoveDefaultProfileLayout
from libs.exception.profile_layout.profile_layout_already_exist import ProfileLayoutAlreadyExist
from libs.exception.profile_layout.profile_layout_not_exist import ProfileLayoutNotExist


class ProfileLayouts():
    """This class is designed to manage many ProfileLayouts.
    """
    __db_access : DatabaseAccessImplement
    
    def __init__(self) -> None:
        """This method is designed to initialize the ProfileLayouts class.
        """
        self.__db_access = DatabasesSelecter().databases
        
    @property
    def get_all_profile_layouts(self) -> list[ProfileLayout]:
        """This method is designed to get all profile layouts.

        Returns:
            list[ProfileLayouts]: A list of profile layout.
        """
        return self.__create_list_of_profile_layout_by_list_profile_layout_name(self.__db_access.get_all_profile_layouts_name())
    
    def add(self, layout_name: str, layout: Layout) -> None:
        """This method is designed to add a profile layout.
        """
        try: 
            ProfileLayout(layout_name)
            raise ProfileLayoutAlreadyExist
        except ProfileLayoutNotExist:
            self.__db_access.add_profile_layout(layout_name, layout)
    
    def remove(self, profile_layout: ProfileLayout):
        """This method is designed to remove a profile layout.
        """
        if profile_layout.get_default().name == profile_layout.name:
            raise CannotRemoveDefaultProfileLayout
        self.__db_access.remove_profile_layout(profile_layout.name)
    
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