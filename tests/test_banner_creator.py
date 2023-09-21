import unittest
import os

from libs.banner_bar_creator import BannerBarCreator

class TestBannerCreator(unittest.TestCase):
    def test_banner_bar_creator(self):
        self.assertFalse(os.path.isfile(".profile/test_banner.png"))
        
        bar_channel = {
            'bar': {"w": 390, "h": 215, "id": 0},
            'table1': {"w": 110, "h": 279, "id": 0},
            'table2': {"w": 607, "h": 293, "id": 0},
            'table3': {"w": 450, "h": 457, "id": 0}
        },
        bar_people = {
            'bar': [
                {"username": "People 1", "profil": "https://ia903204.us.archive.org/4/items/discordprofilepictures/discordblue.png" }
            ],
            'table1': [],
            'table2': [
                {"username": "People 2", "profil": "https://ia903204.us.archive.org/4/items/discordprofilepictures/discordblue.png" },
                {"username": "People 3", "profil": "https://ia903204.us.archive.org/4/items/discordprofilepictures/discordblue.png" }
            ],
            'table3': []
        }
            
        bar = BannerBarCreator(
            ".profile/test_banner.png",
            "https://shkermit.ch/~ethann/compHydromel/wallpapers/taverne.png",
            bar_channel[0],
            bar_people
        )
        
        self.assertTrue(bar.file_path == ".profile/test_banner.png")
        self.assertTrue(os.path.isfile(bar.file_path))
        
        os.remove(bar.file_path)