
from libs.databases.adaptaters.database_access_implement import DatabaseAccessImplement
from libs.databases.adaptaters.sqlite.sqlite_access import SqliteAccess
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
        
    @property
    def name(self) -> str:
        """This method is designed to get the profile layout name.

        Returns:
            str: The profile layout name.
        """
        return self.__profile_layout_name
    
    @property
    def layout(self) -> dict[str,dict[str, int]]:
        """This method is designed to get the profile layout.

        Returns:
            dict[str,dict[str, int]]: The profile layout. (exemple: {"profilPicture": {"x": 0, "y": 0}, ...})
        """
        return self.__db_access.get_profile_layout(self.__profile_layout_name)