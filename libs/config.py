import yaml

class Config():
    __defaultConfig = {
        "database": "sqlite",
    }
    __configFile = "config.yml"
    
    def __write(self, data) -> None:
        with open(self.__configFile, "w") as f:
            yaml.dump(data, f)
            
    def __is_config_exist(self) -> bool:
        try:
            with open(self.__configFile, "r") as f:
                return True
        except FileNotFoundError:
            return False
    
    def __read(self) -> dict:
        if not self.__is_config_exist():
            self.__write(self.__defaultConfig)
            
        with open(self.__configFile, "r") as f:
            return yaml.load(f, Loader=yaml.FullLoader)
    
    def reload(self) -> None:
        self.config = self.__read()   
        
    def __init__(self) -> None:
        self.reload()
        
    def value(self) -> dict:
        return self.config