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
        },
        "sex_commands": {
            "enable": False,
            "porn": "",
            "hentai": "",
            "jinx": "",
            "002": "",
            "overwatch": ""
        },
        "bar_commands": {
            "beer": {
                "list": [
                    "https://shkermit.ch/~ethann/compHydromel/biere/Biere1.jpg",
                    "https://shkermit.ch/~ethann/compHydromel/biere/Biere2.jpg",
                    "https://shkermit.ch/~ethann/compHydromel/biere/Biere4.jpg",
                    "https://shkermit.ch/~ethann/compHydromel/biere/Biere5.jpg",
                    "https://shkermit.ch/~ethann/compHydromel/biere/Biere6.jpg",
                    "https://shkermit.ch/~ethann/compHydromel/biere/Biere7.jpg",
                    "https://shkermit.ch/~ethann/compHydromel/biere/Biere8.jpg",
                    "https://shkermit.ch/~ethann/compHydromel/biere/Biere9.jpg",
                    "https://shkermit.ch/~ethann/compHydromel/biere/Biere10.jpg"
                ],
                "price": 5
            }, 
            "soft": {
                "list": [
                    "https://shkermit.ch/~ethann/compHydromel/soft/Verre0.jpg",
                    "https://shkermit.ch/~ethann/compHydromel/soft/Verre1.jpg",
                    "https://shkermit.ch/~ethann/compHydromel/soft/Verre2.jpg",
                    "https://shkermit.ch/~ethann/compHydromel/soft/Verre3.jpg",
                    "https://shkermit.ch/~ethann/compHydromel/soft/Verre4.jpg",
                    "https://shkermit.ch/~ethann/compHydromel/soft/Verre5.jpg"
                ],
                "price": 3
            }, 
            "hydromel": {
                "list": [
                    "https://shkermit.ch/~ethann/compHydromel/hydromel/Hydromel1.jpg"
                ],
                "price": 9
            }, 
            "water": {
                "list": [
                    "https://shkermit.ch/~ethann/compHydromel/water/water.jpg"
                ],
                "price": 0
            },
        },
        "reactions": {
            "enable": False,
            "list": [
                {
                    "emoji": "✅",
                    "role_id": 0,
                    "message_id": 0,
                }
            ]
        },
        "music": {
            "enable": False,
            "lavalink_ip": "127.0.0.1",
            "lavalink_port": 2333,
        },
        "information_channel_id": 0
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