from libs.databases.sqlite.sqlite_access import SqliteAccess
from libs.exception.not_enougt_money import NotEnougtMoneyException

class User():
    __discord_id : str
    
    def __init__(self, discord_id : str) -> None:
        self.__discord_id = discord_id
        self.__db_access = SqliteAccess()
        self.__db_access.add_user_if_not_exist(discord_id)
    
    def discord_id(self) -> str:
        return self.__discord_id
    
    def level(self) -> int:
        return self.__db_access.get_user_level(self.__discord_id)

    def point(self) -> int:
        return self.__db_access.get_user_point(self.__discord_id)
    
    def add_point(self, point = 1) -> None:
        self.__db_access.add_user_point(self.__discord_id, point)
        self.__check_level_up()

    def add_balance(self, amount = 1) -> None: 
        self.__db_access.add_balance(self.__discord_id, amount)

    def remove_balance(self, amount = 1) -> None:
        if not self.__db_access.remove_balance(self.__discord_id, amount):
            raise NotEnougtMoneyException

    def name_color(self) -> str:
        pass
    
    def bar_color(self) -> str:
        pass

    def __check_level_up(self) -> None:
        point = self.point()
        level = self.level()
        if point >= 200 * level:
            self.__db_access.add_user_level(self.__discord_id)
            self.__db_access.reset_point(self.__discord_id)
            self.__db_access.add_user_point(self.__discord_id, point - (200 * level))
            self.add_balance(100+(level*100))