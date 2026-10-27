import configparser
import sys
from pathlib import Path
from urllib.parse import urlparse


def load_config(path):
    config = configparser.ConfigParser()

    if not Path(path).is_file():
        raise ValueError("Конфигурационный файл не найден")

    config.read(path, encoding="utf-8")

    if not config.has_section("settings"):
        raise ValueError("Отсутствует секция [settings]")

    required = (
        "package",
        "repository",
        "test_mode",
        "output_file",
        "ascii_tree",
    )

    for key in required:
        if not config.has_option("settings", key):
            raise ValueError(f"Отсутствует параметр: {key}")

    settings = config["settings"]

    package = settings["package"].strip()
    repository = settings["repository"].strip()
    output_file = settings["output_file"].strip()

    if not package:
        raise ValueError("Имя пакета не может быть пустым")

    if not repository:
        raise ValueError("Репозиторий не может быть пустым")

    try:
        test_mode = config.getboolean("settings", "test_mode")
        ascii_tree = config.getboolean("settings", "ascii_tree")
    except ValueError as error:
        raise ValueError("Некорректное логическое значение") from error

    if test_mode:
        if not Path(repository).is_file():
            raise ValueError("Файл тестового репозитория не найден")
    elif urlparse(repository).scheme not in ("http", "https"):
        raise ValueError("Некорректный URL репозитория")

    if not output_file.endswith(".svg"):
        raise ValueError("Выходной файл должен иметь расширение .svg")

    if not Path(output_file).name == output_file:
        raise ValueError("Укажите только имя выходного файла")

    return {
        "package": package,
        "repository": repository,
        "test_mode": test_mode,
        "output_file": output_file,
        "ascii_tree": ascii_tree,
    }


def main():
    config_path = (
        sys.argv[1] if len(sys.argv) > 1 else "config.ini"
    )

    try:
        settings = load_config(config_path)
    except (ValueError, configparser.Error, OSError) as error:
        print(f"Ошибка: {error}", file=sys.stderr)
        return 1

    for key, value in settings.items():
        print(f"{key}: {value}")

    return 0


if __name__ == "__main__":
    sys.exit(main())