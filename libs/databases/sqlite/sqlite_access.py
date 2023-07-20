from libs.databases.sqlite.sqlite import Sqlite

class SqliteAccess():
    __sqliteDB : Sqlite
    
    def __init__(self) -> None:
        self.__sqliteDB = Sqlite("database.db")
        if len(self.__sqliteDB.select("SELECT name FROM sqlite_master WHERE type='table' AND name='users';")) == 0:
            self.__create_db()

    # Public 

    def get_user_level(self, discord_id: str) -> int:
        return self.__select_user(discord_id, "level")[0][0]

    def get_user_point(self, discord_id: str) -> int:
        return self.__select_user(discord_id, "point")[0][0]
    
    def get_balance(self, discord_id: str) -> int:
        return self.__select_user(discord_id, "balance")[0][0]
    
    def add_user_point(self, discord_id: str, point: int = 1) -> None:
        self.__sqliteDB.modify("UPDATE users SET point = point + " + str(point) + " WHERE discordId = '" + discord_id + "'")

    def add_user_level(self, discord_id: str, level = 1) -> None:
        self.__sqliteDB.modify("UPDATE users SET level = level + " + str(level) + " WHERE discordId = '" + discord_id + "'")

    def add_balance(self, discord_id, amount=1) -> None:
        self.__sqliteDB.modify("UPDATE users SET balance =  balance + " + str(amount) + " WHERE discordId = " + discord_id)
    
    def remove_balance(self, discord_id, amount=1) -> bool:
        if(self.get_balance - amount < 0):
            return False
        self.__sqliteDB.modify("UPDATE users SET balance = balance - " + str(amount) + " WHERE discordId = " + discord_id)
        return True

    def add_user_if_not_exist(self, discord_id: str) -> None:
        if not self.__sqliteDB.select("SELECT discordId FROM users WHERE discordId = '" + discord_id + "';"):
            self.__sqliteDB.modify("INSERT INTO users(discordId) VALUES ('" + discord_id + "');")
            self.__sqliteDB.modify("INSERT INTO usersBuyWallpapers(usersId, wallpapersId) VALUES (" + str(self.__get_user_id(discord_id)) + ",1);")

    def reset_point(self, discord_id: str) -> None:
        self.__sqliteDB.modify("UPDATE users SET point = 0 WHERE discordId = " + discord_id)


    # Public

    # Private

    def __select_user(self, discord_id: str, selection) -> str:
        return self.__sqliteDB.select("SELECT " + selection + " FROM users WHERE discordId == " + discord_id)
    
    def __get_user_id(self,discord_id: str) -> str:
        return self.__sqliteDB.select("SELECT id FROM users WHERE discordId = '" + discord_id + "';")[0][0]
    
    def __create_db(self) -> None:
        with open("data/databases/sqliteDB.sql", "r") as script:
            for cmd in script.read().split(";"):
                self.__sqliteDB.modify(cmd)
    
    # Private