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
        "nsfw_commands": {
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
        },
        "music": {
            "enable": False,
            "lavalink_ip": "127.0.0.1",
            "lavalink_port": 2333,
            "music_on_join": {
                "enable": False,
                "default_song": "",
                "discord_id_to_song": {
                    "0": ""
                }
            }
        },  
        "information_channel_id": 0,
        "response": {
            "wallpaper_changed": "Wallpaper changed!",
            "wallpaper_buyed": "Wallpaper buyed!",
            "namecolor_changed": "Name color changed!",
            "barcolor_changed": "Bar color changed!",
            "message_sent": "Message sent!",
            "clearing_channel": "Clearing messages...",
            "channel_cleared": "Message cleared!",
            "user_added_to_root": "User added to root!",
            "user_removed_to_root": "User removed from root!",
            "smartpoint_added": "smartpoint added!",
            "smartpoint_removed": "smartpoint removed!",
            "wallpaper_added": "Wallpaper added!",
            "wallpaper_removed": "Wallpaper Removed!",
            "music_stopping": "Stopping.",
            "pausing_music": "Pausing music: `{music}`",
            "resuming_music": "Resuming music: `{music}`",
            "back_to_previous_music": "Back to the previous music.",
            "skipping_music": "Skipping.",
            "server_boosted": "Thanks {user} for boosting the server!",
            "profile_layout_changed": "Profile layout changed!",
            "profile_layout_added": "Profile layout added!",
            "profile_layout_removed": "Profile layout removed!",
            "profile_layout_updated": "Profile layout updated!",
            "profile_layout_renamed": "Profile layout renamed!",
            "wallpaper_updated": "Wallpaper updated!",
            "wallpaper_renamed": "Wallpaper renamed!",
            "role_added": "Role added!",
            "role_removed": "Role removed!",
            "role_updated": "Role updated!"
        },
        "exception_response": {
            "default": "An error occured",
            "option_not_found": "Option not found!",
            "wallpaper_not_exist": "Wallpaper not exist!",
            "wallpaper_not_posseded": "Wallpaper not posseded!",
            "color_not_correct": "The color is not correct! please use hexadecimal color (ex: #ffffff) or use color name (green, blue, red, yellow, orange, pink, black, white, ect...)",
            "not_enougt_smartpoint": "Your not so smart! You don't have enought smartpoint!",
            "wallpaper_already_posseded": "Be smart! Wallpaper already posseded!",
            "wallpaper_cannot_be_buyed": "Be smart! Wallpaper cannot be buyed!",
            "unable_to_download_image": "Unable to download image!",
            "folder_not_found": "Folder not found!",
            "not_nsfw_channel": "This command can only be used in a NSFW channel",
            "channel_not_messageable": "This channel is not messageable!",
            "user_not_messageable": "This user is not messageable!",
            "information_channel_not_found": "Information channel not found! please add it in config.yml",
            "information_channel_not_messageable": "The information channel is not messageable! please change it in config.yml",
            "cannot_send_message_to_this_user": "Cannot send message to this user!",
            "not_root": "You are not root!",
            "enter_amount": "Please enter an amount!",
            "url_not_an_image": "Please make sure url is an image!",
            "url_not_good_formated": "Please enter an valid url!",
            "wallpaper_already_exist": "Wallpaper already exist!",
            "already_playing": "Already playing. Adding to queue.",
            "not_connected_to_voice_channel": "You need to be connected to a voice channel to play music.",
            "no_results_found": "No results found.",
            "not_playing_music": "The bot is not playing music.",
            "nothing_left_in_previous_queue": "Nothing left in previous song queue.",
            "nothing_left_in_queue": "Nothing left in queue.",
            "profile_layout_not_exist": "Profile layout not exist!",
            "profile_layout_already_exist": "Profile layout already exist!",
            "enter_new_name": "Please enter a new name!",
            "cannot_remove_default_profile_layout": "Cannot remove default profile layout!",
            "cannot_remove_default_wallpaper": "Cannot remove default wallpaper!",
            "level_should_be_greater_than_one": "Level should be set and greater than one!",
            "role_already_exist": "Role already exist!",
            "role_not_exist": "Role not exist!",
            "cannot_manage_default_role": "Cannot manage default role! @(everyone)",
            "role_level_already_exist": "Role level already exist!",
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
                    self.config[field] = self.__check_subfield_exist(self.config[field], self.__default_config[field])
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
            for field in default_subfield:
                if field not in subfield:
                    subfield[field] = default_subfield[field]
                    self.__need_to_rewrite = True
                else:
                    subfield[field] = self.__check_subfield_exist(subfield[field], default_subfield[field])
        elif isinstance(default_subfield, list):
            for subfield_number in range(len(subfield)):
                subfield[subfield_number] = self.__check_subfield_exist(subfield[subfield_number], default_subfield[0])
    
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