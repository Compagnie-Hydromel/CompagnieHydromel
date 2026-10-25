import asyncio
import unittest
from unittest.mock import AsyncMock, Mock, patch

from commands._bot import run_bot


class TestBotStartup(unittest.TestCase):
    def run_with_bot(self, token, error=None):
        bot = Mock()
        bot.start = AsyncMock(side_effect=error)
        bot.close = AsyncMock()

        def create_bot(**kwargs):
            self.assertTrue(asyncio.get_running_loop().is_running())
            return bot

        with patch("commands._bot.discord.Bot", side_effect=create_bot), patch(
            "commands._bot.os.listdir", return_value=["example.py", "ignored.txt"]
        ), patch("commands._bot.os.getenv", return_value=token), patch(
            "commands._bot.Log.error"
        ) as log_error:
            if error is not None:
                with self.assertRaisesRegex(RuntimeError, "login failed"):
                    run_bot("barman")
            else:
                run_bot("barman")

        bot.close.assert_awaited_once_with()
        return bot, log_error

    def test_startup_creates_running_loop_and_loads_cogs(self):
        bot, log_error = self.run_with_bot("test-token")

        bot.start.assert_awaited_once_with("test-token")
        self.assertEqual(bot.load_extension.call_count, 2)
        bot.load_extension.assert_any_call("cogs.barman.example")
        bot.load_extension.assert_any_call("cogs.example")
        bot.event.assert_called_once()
        log_error.assert_not_called()

    def test_missing_token_logs_error_and_closes_bot(self):
        bot, log_error = self.run_with_bot(None)

        bot.start.assert_not_awaited()
        log_error.assert_called_once_with(
            "BARMAN_TOKEN is not defined in .env file")

    def test_login_failure_closes_bot(self):
        self.run_with_bot("test-token", RuntimeError("login failed"))
