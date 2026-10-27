import unittest
from unittest.mock import patch

import discord

from libs.databases.models.guild_user import GuildUser


class TestProfileAvatar(unittest.TestCase):
    def avatar_url(self, avatar=None, guild_avatar=None):
        member = object.__new__(discord.Member)
        member._state = None
        member._avatar = guild_avatar
        member.guild = type("Guild", (), {"id": 123})()
        user = object.__new__(discord.User)
        user._state = None
        user.id = 456
        user.discriminator = "0"
        user._avatar = avatar
        member._user = user
        profile = object.__new__(GuildUser)
        profile._attributes = {}
        profile._modified_attributes = {}
        with patch.object(GuildUser, "get_guilduser", return_value=member):
            return profile.avatar_url

    def test_server_avatar_takes_precedence(self):
        self.assertIn("/guilds/123/users/456/avatars/server", self.avatar_url(
            avatar="global", guild_avatar="server"))

    def test_falls_back_to_global_avatar(self):
        self.assertIn("/avatars/456/global", self.avatar_url(avatar="global"))

    def test_falls_back_to_default_avatar(self):
        self.assertIn("/embed/avatars/", self.avatar_url())
