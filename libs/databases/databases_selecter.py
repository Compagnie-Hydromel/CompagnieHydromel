from libs.config import Config
from libs.databases.repository.database_access_implement import DatabaseAccessImplement
from libs.databases.repository.sqlite.sqlite_access import SqliteAccess

class DatabasesSelecter:
    """This class is designed to select the database.
    """
    __config: Config
    __databases_type: str
    databases_file_override: str = ""

    def __init__(self):
        self.__config = Config()
        self.__databases_type = self.__config.value["database"]["type"]

    @property
    def databases_type(self) -> str:
        return self.__databases_type

    @property
    def databases(self) -> DatabaseAccessImplement:
        if DatabasesSelecter.databases_file_override != "":
            return SqliteAccess(self.databases_file_override)

        match(self.databases_type):
            case "sqlite":
                return SqliteAccess(self.__config.value["database"]["sqlite"]["file"])
            case _:
                raise ValueError("The database type is not supported.")
