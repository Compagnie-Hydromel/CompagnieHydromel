import yaml


class Config():
    """This class is designed to manage the config.
    """
    _instance = None

    def __new__(cls, *args, **kwargs):
        if not cls._instance:
            cls._instance = super(Config, cls).__new__(cls, *args, **kwargs)
        return cls._instance

    __default_config = {
        "database": {
            "type": "sqlite",
            "sqlite": {
                "file": "database.db",
                "collation": "utf8mb4_general_ci"
            },
            "mysql": {
                "host": "localhost",
                "port": 3306,
                "database": "",
                "collation": "utf8mb4_general_ci"
            }
        },
        "music": {
            "enable": False,
            "lavalink_ip": "127.0.0.1",
            "lavalink_port": 2333
        },
        "reactions": {
            "enable": False,
            "list": [
                {
                    "emoji": "🎨",
                    "role_id": 0,
                    "message_id": 0,
                    "action": "emoji_to_role"
                },
                {
                    "emoji": "✅",
                    "role_id": 0,
                    "message_id": 0,
                    "action": "accept_rules"
                }
            ]
        }
    }
    __config_file = "config.yml"
    __no_check_fields = ["discord_id_to_song"]

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
            yaml.dump(data, f, encoding='utf-8', allow_unicode=True)

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

    def __check_no_missing_field(self):
        """To check if there is no missing field in the config.
        """
        self.__need_to_rewrite = False
        if self.config is None:
            self.config = self.__default_config
            self.__need_to_rewrite = True
        else:
            for field in self.__default_config:
                if field in self.config:
                    self.config[field] = self.__check_subfield_exist(
                        self.config[field], self.__default_config[field])
                else:
                    self.config[field] = self.__default_config[field]
                    self.__need_to_rewrite = True
        if self.__need_to_rewrite:
            self.__write(self.config)

    def __check_subfield_exist(self, subfield, default_subfield) -> any:
        """Useful but only use with __check_no_missing_field to check if subfield exist.

        Args:
            subfield (_type_): the subfield to check and modifiy if needed.
            default_subfield (_type_): the default subfield alias the reference of the check.

        Returns:
            any: the subfield modified or not modified.
        """
        if isinstance(default_subfield, dict) and default_subfield not in self.__no_check_fields:
            if not isinstance(subfield, dict):
                subfield = default_subfield
                self.__need_to_rewrite = True
            for field in default_subfield:
                if field not in subfield:
                    subfield[field] = default_subfield[field]
                    self.__need_to_rewrite = True
                else:
                    subfield[field] = self.__check_subfield_exist(
                        subfield[field], default_subfield[field])
        elif isinstance(default_subfield, list):
            for subfield_number in range(len(subfield)):
                subfield[subfield_number] = self.__check_subfield_exist(
                    subfield[subfield_number], default_subfield[0])

        return subfield

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
        self.__check_no_missing_field()

    @property
    def value(self) -> dict:
        """This method is designed to get the config.

        Returns:
            dict: The config.
        """
        return self.config
