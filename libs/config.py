import yaml

class Config():
    """This class is designed to manage the config.
    """    
    __default_config = {
        "database": "sqlite",
        "banner": {
            "enable": False,
            "banner_image": "https://shkermit.ch/~ethann/compHydromel/wallpapers/taverne.png",
            "coords": {
                'bar': {"w":390,"h":215, "id": 0},
                'table1': {"w":110,"h":279, "id": 0},
                'table2': {"w":607,"h":293, "id": 0},
                'table3': {"w":450,"h":457, "id": 0}
            },
            "guild_id": 0
        } 
    }
    __config_file = "config.yml"
    
    def __init__(self) -> None:
        """This method is designed to initialize the Config class.
        """
        self.reload()
    
    def __write(self, data: dict[str: any]) -> None:
        """This method is designed to write the config.

        Args:
            data (dict[str: any]): The data to write.
        """
        with open(self.__config_file, "w") as f:
            yaml.dump(data, f)
            
    def __is_config_exist(self) -> bool:
        """This method is designed to check if the config exist.

        Returns:
            bool: True if the config exist, False otherwise.
        """
        try:
            with open(self.__config_file, "r") as f:
                return True
        except FileNotFoundError:
            return False
    
    def __read(self) -> dict[str: any]:
        """This method is designed to read the config.

        Returns:
            dict[str: any]: The config.
        """
        if not self.__is_config_exist():
            self.__write(self.__default_config)
            
        with open(self.__config_file, "r") as f:
            return yaml.load(f, Loader=yaml.FullLoader)
    
    def reload(self) -> None:
        """This method is designed to reload the config.
        """
        self.config = self.__read()
    
    @property
    def value(self) -> dict:
        """This method is designed to get the config.

        Returns:
            dict: The config.
        """
        return self.config