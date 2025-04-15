
from libs.databases.databases_selecter import DatabasesSelecter
from libs.databases.repository.database_access_implement import DatabaseAccessImplement
from libs.databases.dto.layout import Layout
from libs.exception.profile_layout.profile_layout_not_exist import ProfileLayoutNotExist
from libs.exception.profile_layout.profile_layout_already_exist import ProfileLayoutAlreadyExist
from libs.exception.profile_layout.cannot_remove_default_profile_layout import CannotRemoveDefaultProfileLayout


class ProfileLayout:
    """This class is designed to manage a ProfileLayout.
    """
    __profile_layout_name: str
    __db_access: DatabaseAccessImplement

    def __init__(self, profile_layout_name: str) -> None:
        """Constructor of ProfileLayout class.

        Args:
            profile_layout_name (str): The name of the profile layout.

        Raises:
            ProfileLayoutNotExist: If the profile layout doesn't exist.
        """
        self.__profile_layout_name = profile_layout_name
        self.__db_access = DatabasesSelecter().databases

        if not self.__db_access.is_profile_layout_exist(self.__profile_layout_name):
            raise ProfileLayoutNotExist

    @staticmethod
    def all() -> list["ProfileLayout"]:
        """This method is designed to get all profile layouts.

        Returns:
            list[ProfileLayouts]: A list of profile layout.
        """
        return ProfileLayout.__create_list_of_profile_layout_by_list_profile_layout_name(DatabasesSelecter().databases.get_all_profile_layouts_name())

    @staticmethod
    def add(layout_name: str, layout: Layout) -> None:
        """This method is designed to add a profile layout.
        """
        try:
            ProfileLayout(layout_name)
            raise ProfileLayoutAlreadyExist
        except ProfileLayoutNotExist:
            DatabasesSelecter().databases.add_profile_layout(layout_name, layout)

    @staticmethod
    def remove(profile_layout: "ProfileLayout"):
        """This method is designed to remove a profile layout.
        """
        if profile_layout.get_default().name == profile_layout.name:
            raise CannotRemoveDefaultProfileLayout
        DatabasesSelecter().databases.remove_profile_layout(profile_layout.name)

    @staticmethod
    def __create_list_of_profile_layout_by_list_profile_layout_name(list_name: list[str]) -> list["ProfileLayout"]:
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

    @staticmethod
    def get_default():
        """This method is designed to get the default profile layout.

        Returns:
            ProfileLayout: The default profile layout.
        """
        return ProfileLayout(DatabasesSelecter().databases.get_default_profile_layout_name())

    @property
    def name(self) -> str:
        """This method is designed to get the profile layout name.

        Returns:
            str: The profile layout name.
        """
        return self.__profile_layout_name

    @property
    def layout(self) -> Layout:
        """This method is designed to get the profile layout.

        Returns:
            Layout: The profile layout.
        """
        return self.__db_access.get_profile_layout(self.__profile_layout_name)

    @layout.setter
    def layout(self, layout: Layout) -> None:
        """This method is designed to update a profile layout.
        """
        self.__db_access.update_profile_layout(
            self.__profile_layout_name, layout)

    @name.setter
    def name(self, new_name: str) -> None:
        """This method is designed to set the name of a profile layout.
        """
        self.__db_access.rename_profile_layout(
            self.__profile_layout_name, new_name)
        self.__profile_layout_name = new_name

    def __str__(self) -> str:
        """This method is designed to represent the object as a string.

        Returns:
            str: The string representation of the object.
        """
        return "ProfileLayout(name: " + self.__profile_layout_name + ", layout: " + str(self.layout) + ")"
