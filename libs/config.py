import yaml

class Config():
    """This class is designed to manage the config.
    """    
    __defaultConfig = {
        "database": "sqlite",
    }
    __configFile = "config.yml"
    
    def __init__(self) -> None:
        """This method is designed to initialize the Config class.
        """
        self.reload()
    
    def __write(self, data: dict[str: any]) -> None:
        """This method is designed to write the config.

        Args:
            data (dict[str: any]): The data to write.
        """
        with open(self.__configFile, "w") as f:
            yaml.dump(data, f)
            
    def __is_config_exist(self) -> bool:
        """This method is designed to check if the config exist.

        Returns:
            bool: True if the config exist, False otherwise.
        """
        try:
            with open(self.__configFile, "r") as f:
                return True
        except FileNotFoundError:
            return False
    
    def __read(self) -> dict[str: any]:
        """This method is designed to read the config.

        Returns:
            dict[str: any]: The config.
        """
        if not self.__is_config_exist():
            self.__write(self.__defaultConfig)
            
        with open(self.__configFile, "r") as f:
            return yaml.load(f, Loader=yaml.FullLoader)
    
    def reload(self) -> None:
        """This method is designed to reload the config.
        """
        self.config = self.__read()
        
    def value(self) -> dict:
        """This method is designed to get the config.

        Returns:
            dict: The config.
        """
        return self.config