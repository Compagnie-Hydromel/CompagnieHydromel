import unittest

from libs.databases.databases_selecter import DatabasesSelecter
from libs.databases.model.role import Role
from libs.exception.role.level_should_be_greater_than_one_exception import LevelShouldBeGreaterThanOneException
from libs.exception.role.role_not_exist_exception import RoleNotExistException
from libs.exception.role.role_already_exist_exception import RoleAlreadyExistException
from tests.utils import Utils


class TestRole(unittest.TestCase):
    __role: Role

    def setUp(self) -> None:
        DatabasesSelecter.databases_file_override = "test_database.db"
        Role.add("TestRole", 1)
        self.__role = Role("TestRole")

    def tearDown(self) -> None:
        Utils.deleteFileIfExist("test_database.db")

    def test_add_role(self):
        Role.add("TestRole2", 3)

    def test_remove_role(self):
        Role.remove("TestRole")

    def test_add_existing_role(self):
        with self.assertRaises(RoleAlreadyExistException):
            Role.add("TestRole", 1)

    def test_remove_not_existing_role(self):
        with self.assertRaises(RoleNotExistException):
            Role.remove("TestRole123")

    def test_add_zero_level_role(self):
        with self.assertRaises(LevelShouldBeGreaterThanOneException):
            Role.add("TestRole", 0)

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
