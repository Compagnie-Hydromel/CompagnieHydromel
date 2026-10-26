import os
import unittest
from unittest.mock import mock_open, patch

from libs.log import Log


class TestLog(unittest.TestCase):
    def test_log_file_path(self):
        for value, expected in (
            (None, "log.txt"),
            ("", "log.txt"),
            ("storages/app.log", "storages/app.log"),
            ("/var/log/app.log", "/var/log/app.log"),
        ):
            with self.subTest(log_file=value):
                environment = {} if value is None else {"LOG_FILE": value}
                with patch.dict(os.environ, environment, clear=True), patch(
                    "libs.log.open", mock_open()
                ) as log_file, patch("builtins.print") as console:
                    Log.info("Test message")

                log_file.assert_called_once_with(expected, "a")
                message = console.call_args.args[0]
                self.assertTrue(message.endswith(" [INFO] : Test message"))
                log_file().write.assert_called_once_with(message + "\n")
