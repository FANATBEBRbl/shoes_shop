from configparser import ConfigParser
from pathlib import Path


def load_db_config():
    path = Path(__file__).with_name("config.ini")
    config = ConfigParser(interpolation=None)
    if not config.read(path, encoding="utf-8"):
        raise ValueError("Создайте config.ini на основе config.ini.example.")

    database = config["database"]
    return {
        "host": database["host"],
        "port": database.getint("port"),
        "dbname": database["name"],
        "user": database["user"],
        "password": database["password"],
    }
