from libs.databases.dto.coords import Coords

class Layout:
    """Layout DTO
    """    
    __profile_picture: Coords
    __name: Coords
    __username: Coords
    __level: Coords
    __badge: Coords
    __level_bar: Coords
    
    def __init__(self, profil_picture: Coords, name: Coords, username: Coords, level: Coords, badge: Coords, level_bar: Coords):
        """layout Constructor

        Args:
            profil_picture (Coords): the coords of the profil picture
            name (Coords): the coords of the name
            username (Coords): the coords of the username
            level (Coords): the coords of the level
            badge (Coords): the coords of the badge
            level_bar (Coords): the coords of the level bar
        """
        self.__profile_picture = profil_picture
        self.__name = name
        self.__username = username
        self.__level = level
        self.__badge = badge
        self.__level_bar = level_bar
        
    def __str__(self) -> str:
        return f'Layout(profil_picture: {self.__profile_picture}, name: {self.__name}, username: {self.__username}, level: {self.__level}, badge: {self.__badge}, level_bar: {self.__level_bar})'
    
    @property
    def profile_picture(self) -> Coords:
        """Get the coords of the profil picture

        Returns:
            Coords: the coords of the profil picture
        """
        return self.__profile_picture
    
    @property
    def name(self) -> Coords:
        """Get the coords of the name

        Returns:
            Coords: the coords of the name
        """
        return self.__name
    
    @property
    def username(self) -> Coords:
        """Get the coords of the username

        Returns:
            Coords: the coords of the username
        """
        return self.__username
    
    @property
    def level(self) -> Coords:
        """Get the coords of the level

        Returns:
            Coords: the coords of the level
        """
        return self.__level
    
    @property
    def badge(self) -> Coords:
        """Get the coords of the badge

        Returns:
            Coords: the coords of the badge
        """
        return self.__badge
    
    @property
    def level_bar(self) -> Coords:
        """Get the coords of the level bar

        Returns:
            Coords: the coords of the level bar
        """
        return self.__level_bar
        
    def dict(self) -> dict[str, any]:
        """Convert the dto to a dict

        Returns:
            dict[str, any]: the dict of the layout
        """
        return {
            'profil_picture': self.__profile_picture.dict(),
            'name': self.__name.dict(),
            'username': self.__username.dict(),
            'level': self.__level.dict(),
            'badge': self.__badge.dict(),
            'level_bar': self.__level_bar.dict()
        }