from configparser import ConfigParser
from paths import external_config_path


def load_db_config():
    path = external_config_path()
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
        "connect_timeout": 3,
    }
