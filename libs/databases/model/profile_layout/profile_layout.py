
from libs.databases.repository.database_access_implement import DatabaseAccessImplement
from libs.databases.repository.sqlite.sqlite_access import SqliteAccess
from libs.databases.dto.coords import Coords
from libs.databases.dto.layout import Layout
from libs.exception.profile_layout.profile_layout_not_exist import ProfileLayoutNotExist


class ProfileLayout:
    """This class is designed to manage a ProfileLayout.
    """
    __profile_layout_name : str
    __db_access : DatabaseAccessImplement
    
    def __init__(self, profile_layout_name : str) -> None:
        """Constructor of ProfileLayout class.
        
        Args:
            profile_layout_name (str): The name of the profile layout.
            
        Raises:
            ProfileLayoutNotExist: If the profile layout doesn't exist.
        """        
        self.__profile_layout_name = profile_layout_name
        self.__db_access = SqliteAccess()
        
        if not self.__db_access.is_profile_layout_exist(self.__profile_layout_name):
            raise ProfileLayoutNotExist
        
    @staticmethod
    def get_default():
        """This method is designed to get the default profile layout.
        
        Returns:
            ProfileLayout: The default profile layout.
        """
        return ProfileLayout(SqliteAccess().get_default_profile_layout_name())
        
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
        self.__db_access.update_profile_layout(self.__profile_layout_name, layout)
    
    @name.setter
    def name(self, new_name: str) -> None:
        """This method is designed to set the name of a profile layout.
        """
        self.__db_access.rename_profile_layout(self.__profile_layout_name, new_name)
        self.__profile_layout_name = new_name