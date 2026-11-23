from pathlib import Path
import sys

import paths
import db_config


def test_resources_do_not_depend_on_working_directory(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    assert paths.resource_path("static/Icon.png").is_file()


def test_frozen_config_is_next_to_executable(tmp_path, monkeypatch):
    executable = tmp_path / "application" / "ShoeStore.exe"
    executable.parent.mkdir()
    config = executable.with_name("config.ini")
    config.write_text(
        "[database]\nhost=127.0.0.1\nport=5433\nname=demo\n"
        "user=demo\npassword=fake-test-value\n", encoding="utf-8"
    )
    monkeypatch.setattr(sys, "frozen", True, raising=False)
    monkeypatch.setattr(sys, "executable", str(executable))
    monkeypatch.chdir(tmp_path)
    assert paths.external_config_path() == config
    settings = db_config.load_db_config()
    assert settings["dbname"] == "demo"
    assert settings["port"] == 5433
    assert settings["connect_timeout"] == 3
