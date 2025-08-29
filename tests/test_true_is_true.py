import unittest


class TestTrueIsTrue(unittest.TestCase):
    def test_true_is_true(self):
        self.assertTrue(True, "True should always be true")

    def test_false_is_not_true(self):
        self.assertFalse(False, "False should not be true")
