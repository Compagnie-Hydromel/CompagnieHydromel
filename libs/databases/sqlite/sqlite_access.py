from libs.databases.database_access_implement import DatabaseAccessImplement, ProfileColoredPart
from libs.databases.sqlite.sqlite import Sqlite

class SqliteAccess(DatabaseAccessImplement):
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
    
    def get_smartcoin(self, discord_id: str) -> int:
        return self.__select_user(discord_id, "smartcoin")[0][0]
    
    def add_user_point(self, discord_id: str, point: int = 1) -> None:
        self.__sqliteDB.modify("UPDATE users SET point = point + " + str(point) + " WHERE discordId = '" + discord_id + "'")

    def add_user_level(self, discord_id: str, level = 1) -> None:
        self.__sqliteDB.modify("UPDATE users SET level = level + " + str(level) + " WHERE discordId = '" + discord_id + "'")

    def add_smartcoin(self, discord_id, amount=1) -> None:
        self.__sqliteDB.modify("UPDATE users SET smartcoin =  smartcoin + " + str(amount) + " WHERE discordId = '" + discord_id + "'")
    
    def remove_smartcoin(self, discord_id, amount=1) -> None:
        self.__sqliteDB.modify("UPDATE users SET smartcoin = smartcoin - " + str(amount) + " WHERE discordId = '" + discord_id + "'")
    
    def add_user_if_not_exist(self, discord_id: str) -> None:
        if not self.__sqliteDB.select("SELECT discordId FROM users WHERE discordId = '" + discord_id + "';"):
            self.__sqliteDB.modify("INSERT INTO users(discordId) VALUES ('" + discord_id + "')")
            self.add_posseded_wallpaper(discord_id, "default")

    def reset_point(self, discord_id: str) -> None:
        self.__sqliteDB.modify("UPDATE users SET point = 0 WHERE discordId = '" + discord_id + "';")

    def get_user_profile_color_bar(self, discord_id: str) -> str:
        return self.__select_user(discord_id, "barColor")[0][0]

    def get_user_profile_color_name(self, discord_id: str) -> str:
        return self.__select_user(discord_id, "nameColor")[0][0]

    def get_if_user_is_root(self, discord_id: str) -> bool:
        return bool(self.__select_user(discord_id, "isRoot")[0][0])

    def get_user_current_wallpaper(self, discord_id: str) -> str:
        return self.__sqliteDB.select("SELECT wallpapers.name FROM users INNER JOIN wallpapers ON users.wallpapersId = wallpapers.id WHERE discordId = '" + discord_id + "';")[0][0]

    def get_list_posseded_wallpapers(self, discord_id: str) -> list:
        return self.__reorder_list(self.__sqliteDB.select("SELECT wallpapers.name FROM users \
                                      INNER JOIN usersBuyWallpapers ON usersBuyWallpapers.usersId = users.id \
                                      INNER JOIN wallpapers ON usersBuyWallpapers.wallpapersId = wallpapers.id \
                                      WHERE discordId = '" + discord_id + "';"))

    def change_user_current_wallpaper(self, discord_id: str, wallpaper_name: str) -> None:
        return self.__sqliteDB.modify("WITH updated_wallpapers AS (\
                                        SELECT id\
                                        FROM wallpapers\
                                        WHERE name = '" + wallpaper_name + "')\
                                    UPDATE users\
                                    SET wallpapersId = (SELECT id FROM updated_wallpapers)\
                                    WHERE discordId = '" + discord_id + "';")
    
    def get_all_wallpapers(self) -> list:
        return self.__reorder_list(self.__sqliteDB.select("SELECT name FROM wallpapers"))
    
    def is_wallpaper_exist(self, wallpaper_name: str) -> bool:
        return len(self.__sqliteDB.select("SELECT name FROM wallpapers WHERE name = '" + wallpaper_name + "'")) > 0
    
    def get_wallpaper_price(self, wallpaper_name: str) -> int:
        return self.__select_wallpaper(wallpaper_name, "price")[0][0]
    
    def get_wallpaper_url(self, wallpaper_name: str) -> str:
        return self.__select_wallpaper(wallpaper_name, "url")[0][0]
    
    def get_wallpaper_level(self, wallpaper_name: str) -> str:
        return self.__select_wallpaper(wallpaper_name, "level")[0][0]

    def change_user_profile_custom_color(self, discord_id: str, profile_colored_part: ProfileColoredPart, color: str) -> None:
        self.__sqliteDB.modify("UPDATE users SET " + profile_colored_part.value + " = '" + color + "' WHERE discordId = '" + discord_id + "';")

    def get_users_badge_list(self, discord_id: str) -> list:
        return self.__sqliteDB.select("SELECT badges.name, badges.url FROM users \
                                      INNER JOIN usersHaveBadge ON usersHaveBadge.usersId = users.id \
                                      INNER JOIN badges ON usersHaveBadge.badgesId = badges.id \
                                      WHERE users.discordId = '" + discord_id + "';")

    def get_top_users(self) -> list:
        return self.__reorder_list(self.__sqliteDB.select("SELECT discordId FROM users ORDER BY level DESC, point DESC LIMIT 10"))
    
    def add_posseded_wallpaper(self, discordId: str, wallpaper_name: str) -> None:
        self.__sqliteDB.modify("INSERT INTO usersBuyWallpapers (usersId, wallpapersId) \
                                SELECT u.id AS userId, w.id AS wallpaperId \
                                FROM users u \
                                CROSS JOIN wallpapers w \
                                WHERE u.discordId = '" + discordId + "' \
                                AND w.name = '" + wallpaper_name + "';")

    # Public

    # Private

    def __select_user(self, discord_id: str, selection) -> str:
        return self.__sqliteDB.select("SELECT " + selection + " FROM users WHERE discordId = '" + discord_id + "'")
    
    def __select_wallpaper(self, wallpaper_name: str, selection) -> str:
        return self.__sqliteDB.select("SELECT " + selection + " FROM wallpapers WHERE name = '" + wallpaper_name + "'")
    
    def __create_db(self) -> None:
        with open("data/databases/sqliteDB.sql", "r") as script:
            for cmd in script.read().split(";"):
                self.__sqliteDB.modify(cmd)
    
    def __reorder_list(self, list_to_reorder: list) -> list:
        list_reorder = []
        for item in list_to_reorder:
            list_reorder.append(item[0])
        return list_reorder

    # Private