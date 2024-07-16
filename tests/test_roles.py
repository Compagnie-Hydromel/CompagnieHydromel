import unittest

from libs.databases.databases_selecter import DatabasesSelecter
from libs.databases.model.roles.roles import Roles
from libs.exception.role.level_should_be_greater_than_one_exception import LevelShouldBeGreaterThanOneException
from libs.exception.role.role_already_exist_exception import RoleAlreadyExistException
from libs.exception.role.role_not_exist_exception import RoleNotExistException
from tests.utils import Utils


class TestRoles(unittest.TestCase):
    __roles: Roles

    def setUp(self) -> None:
        DatabasesSelecter.databases_file_override = "test_database.db"
        self.__roles = Roles()

    def tearDown(self) -> None:
        Utils.deleteFileIfExist("test_database.db")

    def test_add_remove_role(self):
        self.__roles.add("TestRole", 1)
        self.__roles.remove("TestRole")

    def test_add_existing_role(self):
        self.__roles.add("TestRole", 1)
        with self.assertRaises(RoleAlreadyExistException):
            self.__roles.add("TestRole", 1)
        self.__roles.remove("TestRole")

    def test_remove_not_existing_role(self):
        with self.assertRaises(RoleNotExistException):
            self.__roles.remove("TestRole")

    def test_add_zero_level_role(self):
        with self.assertRaises(LevelShouldBeGreaterThanOneException):
            self.__roles.add("TestRole", 0)