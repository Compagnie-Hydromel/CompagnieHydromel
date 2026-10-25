import os
from pathlib import Path
from tempfile import TemporaryDirectory
import unittest
from unittest.mock import patch

from libs.databases.bootstrap import init


class TestDatabaseBootstrap(unittest.TestCase):
    def test_sqlite_creates_parent_directories(self):
        with TemporaryDirectory() as directory:
            database = Path(directory) / "storage" / "nested" / "test.sqlite3"
            with patch.dict(os.environ, {
                "DB_TYPE": "sqlite", "DB_NAME": str(database)
            }), patch("libs.databases.bootstrap.DBConfig.set") as configure:
                init()
                init()

            self.assertTrue(database.parent.is_dir())
            self.assertFalse(database.exists())
            self.assertEqual(
                configure.call_args.kwargs["db_database"], str(database))

    def test_mariadb_does_not_create_directories(self):
        with TemporaryDirectory() as directory:
            database = Path(directory) / "not-a-directory" / "database"
            with patch.dict(os.environ, {
                "DB_TYPE": "mariadb", "DB_NAME": str(database)
            }), patch("libs.databases.bootstrap.DBConfig.set"):
                init()

            self.assertFalse(database.parent.exists())
