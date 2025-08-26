from MIWOS.config import DBConfig
from os import getenv


def init():
    db_type = getenv("DB_TYPE") or "sqlite"
    DBConfig.set(
        db_connector=db_type,
        db_host=getenv("DB_HOST") or "localhost",
        db_port=int(getenv("DB_PORT") or 3306),
        db_user=getenv("DB_USER") or "root",
        db_password=getenv("MYSQL_PASSWORD") or "",
        db_database=getenv("DB_NAME") or "compagnieHydromel",
        db_collation=getenv("DB_COLLATION") or "utf8mb4_general_ci",
        db_migration_dir="libs/databases/migrations",
        sql_log_file=getenv(
            "SQL_LOG_FILE") or "libs/databases/" + (db_type) + ".sql.log",
    )
