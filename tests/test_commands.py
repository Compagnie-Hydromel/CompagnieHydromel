import unittest
from unittest.mock import Mock, patch

import commands


class TestCommands(unittest.TestCase):
    @patch("commands.load_all_models")
    @patch("commands.init")
    @patch("commands.load_dotenv")
    def test_each_command_dispatches_to_its_file(self, dotenv, init, models):
        for name, module_name in commands.COMMANDS.items():
            with self.subTest(command=name):
                command = Mock()
                with patch("sys.argv", ["bot.py", name]), patch(
                    "commands.importlib.import_module", return_value=command
                ) as import_module:
                    commands.main()

                import_module.assert_called_once_with(
                    f"commands.{module_name}")
                command.run.assert_called_once_with()

        self.assertEqual(dotenv.call_count, len(commands.COMMANDS))
        self.assertEqual(init.call_count, len(commands.COMMANDS))
        self.assertEqual(models.call_count, len(commands.COMMANDS))

    @patch("commands.load_all_models")
    @patch("commands.init")
    @patch("commands.load_dotenv")
    def test_no_command_starts_all_services(self, dotenv, init, models):
        with patch("sys.argv", ["bot.py"]), patch(
            "commands.start.run"
        ) as run:
            commands.main()

        run.assert_called_once_with()
        init.assert_not_called()
        models.assert_not_called()

    @patch("commands.load_all_models")
    @patch("commands.init")
    @patch("commands.load_dotenv")
    def test_unknown_command_logs_error(self, dotenv, init, models):
        with patch("sys.argv", ["bot.py", "unknown"]), patch(
            "commands.Log.error"
        ) as error, patch("commands.importlib.import_module") as import_module:
            commands.main()

        error.assert_called_once_with("Subcommand not found")
        import_module.assert_not_called()
