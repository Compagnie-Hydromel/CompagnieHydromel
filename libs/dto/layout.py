from libs.dto.coords import Coords


class Layout:
    """Layout DTO
    """    
    __profilPicture: Coords
    __name: Coords
    __userName: Coords
    __level: Coords
    __badge: Coords
    __levelBar: Coords
    
    def __init__(self, profilPicture: Coords, name: Coords, userName: Coords, level: Coords, badge: Coords, levelBar: Coords):
        """layout Constructor

        Args:
            profilPicture (Coords): the coords of the profil picture
            name (Coords): the coords of the name
            userName (Coords): the coords of the username
            level (Coords): the coords of the level
            badge (Coords): the coords of the badge
            levelBar (Coords): the coords of the level bar
        """
        self.__profilPicture = profilPicture
        self.__name = name
        self.__userName = userName
        self.__level = level
        self.__badge = badge
        self.__levelBar = levelBar
    
    @property
    def profilPicture(self) -> Coords:
        """Get the coords of the profil picture

        Returns:
            Coords: the coords of the profil picture
        """
        return self.__profilPicture
    
    @property
    def name(self) -> Coords:
        """Get the coords of the name

        Returns:
            Coords: the coords of the name
        """
        return self.__name
    
    @property
    def userName(self) -> Coords:
        """Get the coords of the username

        Returns:
            Coords: the coords of the username
        """
        return self.__userName
    
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
    def levelBar(self) -> Coords:
        """Get the coords of the level bar

        Returns:
            Coords: the coords of the level bar
        """
        return self.__levelBar
        
    def dict(self) -> dict[str, any]:
        """Convert the dto to a dict

        Returns:
            dict[str, any]: the dict of the layout
        """
        return {
            'profilPicture': self.__profilPicture.dict(),
            'name': self.__name.dict(),
            'userName': self.__userName.dict(),
            'level': self.__level.dict(),
            'badge': self.__badge.dict(),
            'levelBar': self.__levelBar.dict()
        }