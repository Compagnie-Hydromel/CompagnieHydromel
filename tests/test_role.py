import unittest

from libs.databases.databases_selecter import DatabasesSelecter
from libs.databases.model.roles.role import Role
from libs.databases.model.roles.roles import Roles
from libs.exception.role.level_should_be_greater_than_one_exception import LevelShouldBeGreaterThanOneException
from libs.exception.role.role_not_exist_exception import RoleNotExistException
from tests.utils import Utils


class TestRole(unittest.TestCase):
    __role: Role

    def setUp(self) -> None:
        DatabasesSelecter.databases_file_override = "test_database.db"
        Roles().add("TestRole", 1)
        self.__role = Role("TestRole")

    def tearDown(self) -> None:
        Utils.deleteFileIfExist("test_database.db")

    def test_get_role(self):
        self.assertTrue(Role("TestRole") == self.__role)

    def test_get_role_not_exists(self):
        with self.assertRaises(RoleNotExistException):
            Role("TestRoleThatDoesNotExist")

    def test_get_level(self):
        self.assertEqual(1, self.__role.level)

    def test_update_level(self):
        self.__role.level = 2
        self.assertEqual(2, self.__role.level)

    def test_update_level_to_zero(self):
        with self.assertRaises(LevelShouldBeGreaterThanOneException):
            self.__role.level = 0
