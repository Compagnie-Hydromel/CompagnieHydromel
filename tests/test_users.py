import unittest

from libs.databases.model.user.user import User
from libs.databases.model.user.users import Users

class TestUser(unittest.TestCase):
    __users : Users
    
    def setUp(self) -> None:
        self.__users = Users()
        self.__user = User("TestUser")
        
    def test_get_root_users(self):
        self.assertTrue(len(self.__users.get_root_users) >= 0)
        
    def test_get_top_users(self):
        self.assertTrue(len(self.__users.get_top_users) >= 0 and len(self.__users.get_top_users) <= 10)

    def test_get_5_monthly_most_active_users(self):
        self.assertFalse(len(self.__users.get_5_monthly_most_active_users) > 5)