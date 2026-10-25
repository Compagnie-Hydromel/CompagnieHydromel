from contextlib import redirect_stderr, redirect_stdout
from io import StringIO
from types import SimpleNamespace
import unittest
from unittest.mock import Mock, patch

from commands.superadmin import run


DISCORD_ID = "123456789012345678"


class TestSuperadminCommand(unittest.TestCase):
    def invoke(self, *arguments):
        output = StringIO()
        with patch("sys.argv", ["bot.py", "superadmin", *arguments]), redirect_stdout(output):
            run()
        return output.getvalue()

    def test_add_existing_user(self):
        user = SimpleNamespace(is_superadmin=False, saveOrFail=Mock())
        with patch("commands.superadmin.User.whereFirst", return_value=user) as lookup, patch("commands.superadmin.Log.info") as log:
            self.invoke("add", DISCORD_ID)
        lookup.assert_called_once_with(discord_id=DISCORD_ID)
        self.assertTrue(user.is_superadmin)
        user.saveOrFail.assert_called_once_with()
        log.assert_called_once()

    def test_add_creates_missing_user_and_saves_with_flag(self):
        user = SimpleNamespace(is_superadmin=False, saveOrFail=Mock())
        with patch("commands.superadmin.User") as model, patch("commands.superadmin.Log.info"):
            model.whereFirst.return_value = None
            model.return_value = user
            self.invoke("add", DISCORD_ID)
        model.assert_called_once_with(discord_id=DISCORD_ID)
        self.assertTrue(user.is_superadmin)
        user.saveOrFail.assert_called_once_with()

    def test_remove_revokes_without_deleting_user(self):
        user = SimpleNamespace(
            is_superadmin=True, saveOrFail=Mock(), delete=Mock())
        with patch("commands.superadmin.User.whereFirst", return_value=user), patch("commands.superadmin.Log.info"):
            self.invoke("remove", DISCORD_ID)
        self.assertFalse(user.is_superadmin)
        user.saveOrFail.assert_called_once_with()
        user.delete.assert_not_called()

    def test_remove_unknown_user_does_not_create_user(self):
        with patch("commands.superadmin.User") as model:
            model.whereFirst.return_value = None
            output = self.invoke("remove", DISCORD_ID)
        model.assert_not_called()
        self.assertIn("not a super administrator", output)

    def test_repeated_changes_are_idempotent(self):
        for action, flag in (("add", True), ("remove", False)):
            with self.subTest(action=action):
                user = SimpleNamespace(is_superadmin=flag, saveOrFail=Mock())
                with patch("commands.superadmin.User.whereFirst", return_value=user):
                    self.invoke(action, DISCORD_ID)
                user.saveOrFail.assert_not_called()

    def test_list_uses_stored_ids_without_discord(self):
        with patch("commands.superadmin.User.where", return_value=[SimpleNamespace(discord_id=DISCORD_ID)]) as query:
            output = self.invoke("list")
        query.assert_called_once_with(is_superadmin=True)
        self.assertEqual(output.strip(), DISCORD_ID)

    def test_empty_list(self):
        with patch("commands.superadmin.User.where", return_value=[]):
            self.assertIn("No super administrators", self.invoke("list"))

    def test_invalid_arguments_fail_without_database_access(self):
        for arguments in ((), ("invalid",), ("add",), ("remove", "abc"), ("add", "1"),
                          ("add", "-123456789012345678"), ("add", "0" * 18),
                          ("add", "18446744073709551616"), ("list", DISCORD_ID)):
            with self.subTest(arguments=arguments), patch("commands.superadmin.User.whereFirst") as lookup, redirect_stderr(StringIO()), self.assertRaises(SystemExit) as error:
                self.invoke(*arguments)
            self.assertEqual(error.exception.code, 2)
            lookup.assert_not_called()

    def test_failed_save_is_not_reported_as_success(self):
        user = SimpleNamespace(is_superadmin=False, saveOrFail=Mock(
            side_effect=RuntimeError("database failed")))
        with patch("commands.superadmin.User.whereFirst", return_value=user), patch("commands.superadmin.Log.info") as log, self.assertRaises(RuntimeError):
            self.invoke("add", DISCORD_ID)
        log.assert_not_called()
