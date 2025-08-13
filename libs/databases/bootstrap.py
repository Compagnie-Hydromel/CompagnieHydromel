from MIWOS.config import DBConfig
from os import getenv

from libs.config import Config


def init():
    config = Config()
    migration_dir = "libs/databases/migrations"
    match config.value["database"]["type"]:
        case "sqlite":
            DBConfig.set(
                db_connector=config.value["database"]["type"],
                db_database=config.value["database"]["sqlite"]["file"],
                db_collation=config.value["database"]["sqlite"]["collation"],
                db_migration_dir=migration_dir,
                sql_log_file="libs/databases/sqlite.sql.log",
            )
        case "mysql":
            DBConfig.set(
                db_connector=config.value["database"]["type"],
                db_host=config.value["database"]["mysql"]["host"],
                db_port=config.value["database"]["mysql"]["port"],
                db_user=getenv("MYSQL_USER") or "",
                db_password=getenv("MYSQL_PASSWORD") or "",
                db_database=config.value["database"]["mysql"]["database"],
                db_collation=config.value["database"]["mysql"]["collation"],
                db_migration_dir=migration_dir,
                sql_log_file="libs/databases/mysql.sql.log",
            )
