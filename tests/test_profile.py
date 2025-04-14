import unittest
import os
from libs.image_factory.profile_maker import ProfilMaker


class TestProfileMaker(unittest.TestCase):
    def test_profile_create_file(self):
        self.assertFalse(os.path.isfile(".profile/test.png"))

        profile_maker = ProfilMaker(
            ".profile/test.png",
            "Test",
            "https://ia903204.us.archive.org/4/items/discordprofilepictures/discordblue.png",
            5,
            100,
            "test",
            "https://shkermit.ch/~ethann/compHydromel/wallpapers/taverne.png",
        )

        self.assertTrue(profile_maker.profil_path == ".profile/test.png")
        self.assertTrue(os.path.isfile(profile_maker.profil_path))

        os.remove(profile_maker.profil_path)

    def test_profile_create_gif_file(self):
        self.assertFalse(os.path.isfile(".profile/test.gif"))

        profile_maker = ProfilMaker(
            ".profile/test.gif",
            "Test",
            "https://ia903204.us.archive.org/4/items/discordprofilepictures/discordblue.png",
            5,
            100,
            "test",
            "https://shkermit.ch/~ethann/compHydromel/wallpapers/rickroll.gif",
        )

        self.assertTrue(profile_maker.profil_path == ".profile/test.gif")
        self.assertTrue(os.path.isfile(profile_maker.profil_path))

        os.remove(profile_maker.profil_path)
