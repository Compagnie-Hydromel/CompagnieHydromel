import unittest

from libs.databases.user.users import Users

class TestUser(unittest.TestCase):
    __users : Users
    
    def __init__(self, methodName: str = "runTest") -> None:
        self.__users = Users()
        super().__init__(methodName)
        
    def test_get_root_users(self):
        self.assertTrue(len(self.__users.get_root_users) >= 0)
        
    def test_get_top_users(self):
        self.assertTrue(len(self.__users.get_top_users) >= 0 and len(self.__users.get_top_users) <= 10)