import json
from pathlib import Path

from dependency_graph import normalize_name
from pypi_repository import package_info


def index_repository(entries):
    if not isinstance(entries, list):
        raise ValueError("Тестовый репозиторий должен содержать список JSON")
    packages = {}
    for entry in entries:
        name = normalize_name(package_info(entry).get("name"))
        if name in packages:
            raise ValueError(f"Повтор пакета {name} в тестовом репозитории")
        packages[name] = entry
    return packages


def open_test_repository(path):
    with Path(path).open(encoding="utf-8") as stream:
        packages = index_repository(json.load(stream))

    def fetch(name):
        if name not in packages:
            raise ValueError(f"Пакет {name} не найден в тестовом репозитории")
        return packages[name]

    return fetch