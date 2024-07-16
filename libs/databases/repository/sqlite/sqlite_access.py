from libs.databases.repository.database_access_implement import DatabaseAccessImplement, ProfileColoredPart
from libs.databases.repository.sqlite.sqlite import Sqlite
from typing import Any
from libs.databases.dto.coords import Coords
from libs.databases.dto.layout import Layout

class SqliteAccess(DatabaseAccessImplement):
    __sqliteDB : Sqlite
    
    def __init__(self) -> None:
        """This method is designed to initialize the database. Used to initiate the databases and create db if not exist.
        """
        self.__sqliteDB = Sqlite("database.db")
        if len(self.__sqliteDB.select("SELECT name FROM sqlite_master WHERE type='table' AND name='users'")) == 0:
            self.__create_db()

    # Public 

    def get_all_users(self) -> list[str]:
        """This method is designed to get all users.

        Returns:
            list[str]: All users discordId.
        """
        return self.__reorder_list(self.__sqliteDB.select("SELECT discordId FROM users"))

    def get_user_level(self, discord_id: str) -> int:
        """This method is designed to get a user level number.

        Args:
            discord_id (str): Discord user id as a string.

        Returns:
            int: The user level number.
        """
        return self.__select_user(discord_id, "level")[0][0]

    def get_user_point(self, discord_id: str) -> int:
        """This method is designed to get a user number of point.

        Args:
            discord_id (str): Discord user id as a string.

        Returns:
            int: The user number of point.
        """
        return self.__select_user(discord_id, "point")[0][0]
    
    def get_smartpoint(self, discord_id: str) -> int:
        """This method is designed to get a user number of smartpoint.

        Args:
            discord_id (str): Discord user id as a string.

        Returns:
            int: The user number of smartpoint.
        """
        return self.__select_user(discord_id, "smartpoint")[0][0]
    
    def get_number_of_buy(self, discord_id: str) -> int:
        """This method is designed to get a user number of buy.

        Args:
            discord_id (str): Discord user id as a string.

        Returns:
            int: The user number of buy.
        """
        return self.__select_user(discord_id, "numberOfBuy")[0][0]
    
    def add_user_point(self, discord_id: str, point: int = 1) -> None:
        """This method is designed to add point to a user.

        Args:
            discord_id (str): Discord user id as a string.
            point (int, optional): The number of point to add. Defaults to 1.
        """
        self.__sqliteDB.modify("UPDATE users SET point = point + ? WHERE discordId = ?", [point, discord_id])

    def add_user_level(self, discord_id: str, level = 1) -> None:
        """This method is designed to add level to a user.
        
        Args:
            discord_id (str): Discord user id as a string.
            level (int, optional): The number of level to add. Defaults to 1.
        """
        self.__sqliteDB.modify("UPDATE users SET level = level + ? WHERE discordId = ?", [level, discord_id])

    def add_smartpoint(self, discord_id, amount=1) -> None:
        """This method is designed to add smartpoint to a user.

        Args:
            discord_id (_type_): Discord user id as a string.
            amount (int, optional): The number of smartpoint to add. Defaults to 1.
        """
        self.__sqliteDB.modify("UPDATE users SET smartpoint = smartpoint + ? WHERE discordId = ?", [amount, discord_id])
    
    def remove_smartpoint(self, discord_id, amount=1) -> None:
        """This method is designed to remove smartpoint to a user.

        Args:
            discord_id (_type_): Discord user id as a string.
            amount (int, optional): The number of smartpoint to remove. Defaults to 1.
        """
        self.__sqliteDB.modify("UPDATE users SET smartpoint = smartpoint - ? WHERE discordId = ?", [amount, discord_id])
        
    def add_user_monthly_point(self, discord_id: str, point: int = 1) -> None:
        """This method is designed to add monthly point to a user.

        Args:
            discord_id (str): Discord user id as a string.
            point (int, optional): The number of point to add. Defaults to 1.
        """
        self.__sqliteDB.modify("UPDATE users SET monthlyPoint = monthlyPoint + ? WHERE discordId = ?", [point, discord_id])
    
    def remove_user_monthly_point(self, discord_id: str, point: int = 1) -> None:
        """This method is designed to remove monthly point to a user.

        Args:
            discord_id (str): Discord user id as a string.
            point (int, optional): The number of point to remove. Defaults to 1.
        """
        self.__sqliteDB.modify("UPDATE users SET monthlyPoint = monthlyPoint - ? WHERE discordId = ?", [point, discord_id])
    
    def get_user_monthly_point(self, discord_id: str) -> int:
        """This method is designed to get a user number of monthly point.

        Args:
            discord_id (str): Discord user id as a string.

        Returns:
            int: The user number of monthly point.
        """
        return self.__select_user(discord_id, "monthlyPoint")[0][0]
    
    def reset_user_monthly_point(self, discord_id: str) -> None:
        """This method is designed to reset monthly point to 0.

        Args:
            discord_id (str): Discord user id as a string.
        """
        self.__sqliteDB.modify("UPDATE users SET monthlyPoint = 0 WHERE discordId = ?", [discord_id])
    
    def add_user_if_not_exist(self, discord_id: str) -> None:
        """This method is designed to add a user if he doesn't exist.
        
        Args:
            discord_id (str): Discord user id as a string.
        """
        if not self.__sqliteDB.select("SELECT discordId FROM users WHERE discordId = ?", [discord_id]):
            self.__sqliteDB.modify("INSERT INTO users(discordId) VALUES (?)", [discord_id])
            self.add_posseded_wallpaper(discord_id, "default")

    def reset_point(self, discord_id: str) -> None:
        """This method is designed to reset a user point to 0.

        Args:
            discord_id (str): Discord user id as a string.
        """
        self.__sqliteDB.modify("UPDATE users SET point = 0 WHERE discordId = ?", [discord_id])

    def reset_level(self, discord_id: str) -> None:
        """This method is designed to reset a user level to 1.

        Args:
            discord_id (str): Discord user id as a string.
        """
        self.__sqliteDB.modify("UPDATE users SET level = 1 WHERE discordId = ?", [discord_id])

    def get_user_profile_custom_color(self, discord_id: str, profile_colored_part: ProfileColoredPart) -> str:
        """This method is designed to get a user profile custom color.

        Args:
            discord_id (str): Discord user id as a string.
            profile_colored_part (ProfileColoredPart): The profile colored part (NameColor or BarColor).

        Returns:
            str: The user custom bar color as Hex RGB (example: 00ff00, ff00ffaf, etc..).
        """
        return self.__select_user(discord_id, profile_colored_part.value)[0][0]

    def get_if_user_is_root(self, discord_id: str) -> bool:
        """This method is designed to get if a user is root.
        
        Args:
            discord_id (str): Discord user id as a string.
            
        Returns:
            bool: True if the user is root, False if not.
        """
        return bool(self.__select_user(discord_id, "isRoot")[0][0])

    def set_user_root(self, discord_id: str, is_root: bool) -> None:
        """This method is designed to set a user root.

        Args:
            discord_id (str): Discord user id as a string.
            is_root (bool): True if the user is root, False if not.
        """
        self.__sqliteDB.modify("UPDATE users SET isRoot = ? WHERE discordId = ?", [is_root, discord_id])

    def get_user_current_wallpaper(self, discord_id: str) -> str:
        """This method is designed to get a user current wallpaper name.

        Args:
            discord_id (str): Discord user id as a string.

        Returns:
            str: The user current wallpaper name. Return "default" if the user has a deleted wallpaper put on.
        """
        query_result = self.__sqliteDB.select("SELECT wallpapers.name FROM users INNER JOIN wallpapers ON users.wallpapersId = wallpapers.id WHERE discordId = ?", [discord_id])
        if len(query_result) > 0:
            return query_result[0][0]
        return "default"
        
    def get_list_posseded_wallpapers(self, discord_id: str) -> list[str]:
        """This method is designed to get a user posseded wallpapers list.

        Args:
            discord_id (str): Discord user id as a string.

        Returns:
            list[str]: The user posseded wallpapers name list (example: ['default', 'wallpaper_name']).
        """
        return self.__reorder_list(self.__sqliteDB.select("SELECT wallpapers.name FROM users \
                                      INNER JOIN usersBuyWallpapers ON usersBuyWallpapers.usersId = users.id \
                                      INNER JOIN wallpapers ON usersBuyWallpapers.wallpapersId = wallpapers.id \
                                      WHERE discordId = ?", [discord_id]))

    def change_user_current_wallpaper(self, discord_id: str, wallpaper_name: str) -> None:
        """This method is designed to change a user current wallpaper.

        Args:
            discord_id (str): Discord user id as a string.
            wallpaper_name (str): The new wallpaper name.
        """
        self.__sqliteDB.modify("WITH updated_wallpapers AS (\
                                    SELECT id\
                                    FROM wallpapers\
                                    WHERE name = ?)\
                                UPDATE users\
                                SET wallpapersId = (SELECT id FROM updated_wallpapers)\
                                WHERE discordId = ?", [wallpaper_name, discord_id])
    
    def get_all_wallpapers(self) -> list[str]:
        """This method is designed to get all wallpapers name.

        Returns:
            list[str]: All wallpapers name (example: ['default', 'wallpaper_name']).
        """         
        return self.__reorder_list(self.__sqliteDB.select("SELECT name FROM wallpapers"))
    
    def is_wallpaper_exist(self, wallpaper_name: str) -> bool:
        """This method is designed to check if a wallpaper exist.

        Args:
            wallpaper_name (str): The wallpaper name.

        Returns:
            bool: True if the wallpaper exist, False if not.
        """
        return len(self.__sqliteDB.select("SELECT name FROM wallpapers WHERE name = ?", [wallpaper_name])) > 0
    
    def get_wallpaper_price(self, wallpaper_name: str) -> int:
        """This method is designed to get a wallpaper price.

        Args:
            wallpaper_name (str): The wallpaper name.

        Returns:
            int: The wallpaper price.
        """
        return self.__select_wallpaper(wallpaper_name, "price")[0][0]
    
    def get_wallpaper_url(self, wallpaper_name: str) -> str:
        """This method is designed to get a wallpaper url.

        Args:
            wallpaper_name (str): The wallpaper name.

        Returns:
            str: The wallpaper url (example: https://example.com/img.png).
        """
        return self.__select_wallpaper(wallpaper_name, "url")[0][0]
    
    def get_wallpaper_level(self, wallpaper_name: str) -> str:
        """This method is designed to get a wallpaper level.

        Args:
            wallpaper_name (str): The wallpaper name.

        Returns:
            str: The wallpaper level.
        """
        return self.__select_wallpaper(wallpaper_name, "level")[0][0]

    def change_user_profile_custom_color(self, discord_id: str, profile_colored_part: ProfileColoredPart, color: str) -> None:
        """This method is designed to change a user profile custom color.

        Args:
            discord_id (str): Discord user id as a string.
            profile_colored_part (ProfileColoredPart): The profile colored part (NameColor or BarColor).
            color (str): The new color as Hex RGB (example: 00ff00, ff00ffaf, etc..).
        """
        self.__sqliteDB.modify("UPDATE users SET " + profile_colored_part.value + " = ? WHERE discordId = ?", [color, discord_id])

    def get_users_badge_list(self, discord_id: str) -> list[str]:
        """This method is designed to get a user badge list.

        Args:
            discord_id (str): Discord user id as a string.

        Returns:
            list[str]: The user badge list (example: ['badge_name', 'badge_name']).
        """
        return self.__reorder_list(self.__sqliteDB.select("SELECT badges.name FROM users \
                                      INNER JOIN usersHaveBadge ON usersHaveBadge.usersId = users.id \
                                      INNER JOIN badges ON usersHaveBadge.badgesId = badges.id \
                                      WHERE users.discordId = ?", [discord_id]))

    def get_top_users(self) -> list[str]:
        """This method is designed to get the top users.

        Returns:
            list[str]: The top users list (example: ['discord_id', 'discord_id']).
        """
        return self.__reorder_list(self.__sqliteDB.select("SELECT discordId FROM users ORDER BY level DESC, point DESC LIMIT 10"))
    
    def get_root_users(self) -> list[str]:
        """This method is designed to get the root users.

        Returns:
            list[str]: The root users list (example: ['discord_id', 'discord_id']).
        """
        return self.__reorder_list(self.__sqliteDB.select("SELECT discordId FROM users WHERE isRoot = true"))
    
    def add_posseded_wallpaper(self, discordId: str, wallpaper_name: str) -> None:
        """This method is designed to add a wallpaper to a user's possession.

        Args:
            discordId (str): Discord user id as a string.
            wallpaper_name (str): The wallpaper name.
        """
        self.__sqliteDB.modify("INSERT INTO usersBuyWallpapers (usersId, wallpapersId) \
                                SELECT u.id AS userId, w.id AS wallpaperId \
                                FROM users u \
                                CROSS JOIN wallpapers w \
                                WHERE u.discordId = ? \
                                AND w.name = ?", [discordId, wallpaper_name])
        
    def is_badge_exist(self, badge_name: str) -> bool:
        """This method is designed to check if a badge exist.

        Args:
            badge_name (str): The badge name.

        Returns:
            bool: True if the badge exist, False if not.
        """
        return len(self.__sqliteDB.select("SELECT name FROM badges WHERE name = ?", [badge_name])) > 0
    
    def get_badge_url(self, badge_name: str) -> str:
        """This method is designed to get a badge url.

        Args:
            badge_name (str): The badge name.

        Returns:
            str: The badge url (example: https://example.com/img.png).
        """
        return self.__sqliteDB.select("SELECT url FROM badges WHERE name = ?", [badge_name])[0][0]
    
    def increase_number_of_buy(self, discord_id: str) -> None:
        """This method is designed to increase the number of buy of a user.

        Args:
            discord_id (str): Discord user id as a string.
        """
        self.__sqliteDB.modify("UPDATE users SET numberOfBuy = numberOfBuy + 1 WHERE discordId = ?", [discord_id])

    def reset_number_of_buy(self, discord_id: str) -> None:
        """This method is designed to reset the number of buy of a user.

        Args:
            discord_id (str): Discord user id as a string.
        """
        self.__sqliteDB.modify("UPDATE users SET numberOfBuy = 0 WHERE discordId = ?", [discord_id])

    def get_user_profile_layout(self, discord_id: str) -> str:
        """This method is designed to get users profiles layout.

        Args:
            discord_id (str): Discord user id as a string.

        Returns:
            str: The user profile layout name.
        """
        query_result = self.__sqliteDB.select("SELECT profilesLayout.name FROM profilesLayout INNER JOIN users ON users.profilesLayoutId = profilesLayout.id WHERE discordId = ?", [discord_id])

        if len(query_result) > 0:
            return query_result[0][0]
        return self.get_default_profile_layout_name()
    
    def change_user_profile_layout(self, discord_id: str, layout_name: str) -> None:
        """This method is designed to set user profile layout.

        Args:
            discord_id (str): Discord user id as a string.
            layout_name (str): The layout name.
        """
        self.__sqliteDB.modify("WITH updated_profiles_layout AS (\
                                    SELECT id\
                                    FROM profilesLayout\
                                    WHERE name = ?)\
                                UPDATE users\
                                SET profilesLayoutId = (SELECT id FROM updated_profiles_layout)\
                                WHERE discordId = ?", [layout_name, discord_id])
        
    def is_profile_layout_exist(self, layout_name: str) -> bool:
        """This method is designed to check if a profile layout exist.

        Args:
            layout_name (str): The layout name.

        Returns:
            bool: True if the user profile layout exist, False if not.
        """
        return len(self.__sqliteDB.select("SELECT name FROM profilesLayout WHERE name = ?", [layout_name])) > 0
    
    def get_all_profile_layouts_name(self) -> list[str]:
        """This method is designed to list all user profile layout name.

        Returns:
            list[str]: The list of all user profile layout name.
        """
        return self.__reorder_list(self.__sqliteDB.select("SELECT name FROM profilesLayout"))
    
    def get_profile_layout(self, layout_name: str) -> Layout:
        """This method is designed to get a profile layout.

        Args:
            layout_name (str): The layout name.

        Returns:
            Layout: The profile layout.
        """
        raw = self.__sqliteDB.select("SELECT profilPictureX, profilPictureY, nameX, nameY, userNameX, userNameY, levelX, levelY, badgeX, badgeY, levelBarX, levelBarY FROM profilesLayout WHERE name = ?", [layout_name])[0]
        
        return Layout(
            Coords(raw[0], raw[1]),
            Coords(raw[2], raw[3]),
            Coords(raw[4], raw[5]),
            Coords(raw[6], raw[7]),
            Coords(raw[8], raw[9]),
            Coords(raw[10], raw[11])
        )
    
    def get_default_profile_layout_name(self) -> str:
        """This method is designed to get the default profile layout name.

        Returns:
            str: The default profile layout name.
        """
        return self.__sqliteDB.select("SELECT name FROM profilesLayout WHERE id = 1")[0][0]
    
    def add_profile_layout(self, layout_name: str, layout: Layout) -> None:
        """This method is designed to add a profile layout.

        Args:
            layout_name (str): The layout name.
            layout (Layout): The profile layout.
        """
        self.__sqliteDB.modify("INSERT INTO profilesLayout(name, profilPictureX, profilPictureY, nameX, nameY, userNameX, userNameY, levelX, levelY, badgeX, badgeY, levelBarX, levelBarY) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)", [layout_name, layout.profile_picture.x, layout.profile_picture.y, layout.name.x, layout.name.y, layout.username.x, layout.username.y, layout.level.x, layout.level.y, layout.badge.x, layout.badge.y, layout.level_bar.x, layout.level_bar.y])
    
    def remove_profile_layout(self, layout_name: str) -> None:
        """This method is designed to remove a profile layout.

        Args:
            layout_name (str): The layout name.
        """            
        self.__sqliteDB.modify("DELETE FROM profilesLayout WHERE name = ? AND id != 1", [layout_name])
        
    def update_profile_layout(self, layout_name: str, layout: Layout) -> None:
        """This method is designed to update a profile layout.

        Args:
            layout_name (str): The layout name.
            layout (Layout): The profile layout.
        """
        self.__sqliteDB.modify("UPDATE profilesLayout SET profilPictureX = ?, profilPictureY = ?, nameX = ?, nameY = ?, userNameX = ?, userNameY = ?, levelX = ?, levelY = ?, badgeX = ?, badgeY = ?, levelBarX = ?, levelBarY = ? WHERE name = ?", [layout.profile_picture.x, layout.profile_picture.y, layout.name.x, layout.name.y, layout.username.x, layout.username.y, layout.level.x, layout.level.y, layout.badge.x, layout.badge.y, layout.level_bar.x, layout.level_bar.y, layout_name])
    
    def rename_profile_layout(self, old_layout_name: str, new_layout_name: str) -> None:
        """This method is designed to rename a profile layout.

        Args:
            old_layout_name (str): The old layout name.
            new_layout_name (str): The new layout name.
        """
        self.__sqliteDB.modify("UPDATE profilesLayout SET name = ? WHERE name = ?", [new_layout_name, old_layout_name])
    
    def add_wallpaper(self, wallpaper_name: str, url: str, price: int, level: int) -> None:
        """This method is designed to add a wallpaper to the database.

        Args:
            wallpaper_name (str): The wallpaper name.
            url (str): The url of the wallpaper.
            price (int): The price of the wallpaper.
            level (int): The level of the wallpaper.
        """
        self.__sqliteDB.modify("INSERT INTO wallpapers(name, url, price, level) VALUES (?, ?, ?, ?)", [wallpaper_name, url, price, level])
    
    def remove_wallpaper(self, wallpaper_name: str) -> None:
        """This method is designed to remove a wallpaper from the database.

        Args:
            wallpaper_name (str): The wallpaper name.
        """
        self.__sqliteDB.modify("DELETE FROM wallpapers WHERE name = ?", [wallpaper_name])
    
    def set_wallpaper_url(self, wallpaper_name: str, url: str) -> None:
        """This method is designed to set a wallpaper url.

        Args:
            wallpaper_name (str): The wallpaper name.
            url (str): The new url of the wallpaper.
        """
        self.__sqliteDB.modify("UPDATE wallpapers SET url = ? WHERE name = ?;", [url, wallpaper_name])
    
    def set_wallpaper_price(self, wallpaper_name: str, price: int) -> None:
        """This method is designed to set a wallpaper price.

        Args:
            wallpaper_name (str): The wallpaper name.
            price (int): The new price of the wallpaper.
        """
        self.__sqliteDB.modify("UPDATE wallpapers SET price = ? WHERE name = ?", [price, wallpaper_name])

    def set_wallpaper_level(self, wallpaper_name: str, level: int) -> None:
        """This method is designed to set a wallpaper level.

        Args:
            wallpaper_name (str): The wallpaper name.
            level (int): The new level of the wallpaper.
        """
        self.__sqliteDB.modify("UPDATE wallpapers SET level = ? WHERE name = ?", [level, wallpaper_name])
    
    def rename_wallpaper(self, old_wallpaper_name: str, new_wallpaper_name: str) -> None:
        """This method is designed to rename a wallpaper.

        Args:
            old_wallpaper_name (str): The old wallpaper name.
            new_wallpaper_name (str): The new wallpaper name.
        """
        self.__sqliteDB.modify("UPDATE wallpapers SET name = ? WHERE name = ?", [new_wallpaper_name, old_wallpaper_name])
        
    def get_default_wallpaper_name(self) -> str:
        """This method is designed to get the default wallpaper name.

        Returns:
            str: The default wallpaper name.
        """
        return self.__sqliteDB.select("SELECT name FROM wallpapers WHERE id = 1")[0][0]
    
    def get_all_roles(self) -> list[str]:
        """This method is designed to get all roles.

        Returns:
            list[str]: All roles discordId.
        """
        return self.__reorder_list(self.__sqliteDB.select("SELECT discordId FROM roles ORDER BY level ASC"))
    
    def get_role_discord_id_by_role_level(self, level: int) -> str:
        """This method is designed to get a role discordId by role level.

        Args:
            level (int): The role level.
        
        Returns:
            str: The role discordId.
        """
        return self.__sqliteDB.select("SELECT discordId FROM roles WHERE level = ?", [level])[0][0]
    
    def is_role_exist(self, role_discord_id: str) -> bool:
        """This method is designed to check if a role exist.

        Args:
            role_discord_id (str): The role discordId.
        
        Returns:
            bool: True if the role exist, False if not.
        """
        return len(self.__sqliteDB.select("SELECT discordId FROM roles WHERE discordId = ?", [role_discord_id])) > 0
    
    def is_role_exist_by_level(self, role_level: int) -> bool:
        """This method is designed to check if a role exist.

        Args:
            role_level (int): The role of the role.
        
        Returns:
            bool: True if the role exist, False if not.
        """
        return len(self.__sqliteDB.select("SELECT discordId FROM roles WHERE level = ?", [role_level])) > 0

    def get_role_level(self, role_discord_id: str) -> int:
        """This method is designed to get a level which the user need to get the role.

        Args:
            role_discord_id (str): The role discordId.
        
        Returns:
            int: The role level.
        """
        return self.__sqliteDB.select("SELECT level FROM roles WHERE discordId = ?", [role_discord_id])[0][0]

    def add_role(self, role_discord_id: str, level: int) -> None:
        """This method is designed to add a role.

        Args:
            role_discord_id (str): The role discordId.
            level (int): The role level.
        """
        self.__sqliteDB.modify("INSERT INTO roles(discordId, level) VALUES (?, ?)", [role_discord_id, level])

    def remove_role(self, role_discord_id: str) -> None:
        """This method is designed to remove a role.

        Args:
            role_discord_id (str): The role discordId.
        """
        self.__sqliteDB.modify("DELETE FROM roles WHERE discordId = ?", [role_discord_id])

    def update_role_level(self, role_discord_id: str, level: int) -> None:
        """This method is designed to update a role level.

        Args:
            role_discord_id (str): The role discordId.
            level (int): The new role level.
        """
        self.__sqliteDB.modify("UPDATE roles SET level = ? WHERE discordId = ?", [level, role_discord_id])

    def is_user_accepted_rules(self, discord_id: str) -> bool:
        """This method is designed to check if a user accepted the rules.

        Args:
            discord_id (str): Discord user id as a string.
        
        Returns:
            bool: True if the user accepted the rules, False if not.
        """
        return bool(self.__select_user(discord_id, "acceptedRules")[0][0])
    
    def set_user_accepted_rules(self, discord_id: str, accepted: bool) -> None:
        """This method is designed to set a user accepted the rules.

        Args:
            discord_id (str): Discord user id as a string.
            accepted (bool): True if the user accepted the rules, False if not.
        """
        self.__sqliteDB.modify("UPDATE users SET acceptedRules = ? WHERE discordId = ?", [accepted, discord_id])

    def get_5_monthly_most_active_users(self) -> list[str]:
        """This method is designed to get the 5 monthly most active users.

        Returns:
            list[str]: The 5 monthly most active users list.
        """
        return self.__reorder_list(self.__sqliteDB.select("SELECT discordId FROM users ORDER BY monthlyPoint DESC LIMIT 5"))

    # Public

    # Private

    def __select_user(self, discord_id: str, selection) -> list[list[Any]]:
        """This method is designed to select a user's data.

        Args:
            discord_id (str): Discord user id as a string.
            selection (_type_): The data to select. (example: level, point, discordId, etc.. as string with , between each selection)

        Returns:
            list[list[Any]]: The user's data.
        """
        return self.__sqliteDB.select("SELECT " + selection + " FROM users WHERE discordId = ?", [discord_id])
    
    def __select_wallpaper(self, wallpaper_name: str, selection) -> list[list[Any]]:
        """This method is designed to select a wallpaper's data.

        Args:
            wallpaper_name (str): The wallpaper name.
            selection (_type_): The data to select. (example: level, price, url, etc.. as string with , between each selection)

        Returns:
            list[list[Any]]: The wallpaper's data.
        """
        return self.__sqliteDB.select("SELECT " + selection + " FROM wallpapers WHERE name = ?", [wallpaper_name])
    
    def __create_db(self) -> None:
        """This method is designed to create the database.
        """
        with open("data/databases/sqliteDB.sql", "r") as script:
            for cmd in script.read().split(";"):
                self.__sqliteDB.modify(cmd)
    
    def __reorder_list(self, list_to_reorder: list[list[Any]]) -> list[any]:
        """This method is designed to reorder a list.

        Args:
            list_to_reorder (list[list[Any]]): The list to reorder.

        Returns:
            list[any]: The reordered list.
        """
        list_reorder = []
        for item in list_to_reorder:
            list_reorder.append(item[0])
        return list_reorder
    # Private