import configparser
import sys
from pathlib import Path
from urllib.parse import urlparse

REQUIRED_OPTIONS = (
    "package",
    "repository",
    "test_mode",
    "output_file",
    "ascii_tree",
)

def find_config(path):
    config_path = Path(path)
    if config_path.is_file():
        return config_path
    if config_path.name == str(config_path):
        test_path = Path(__file__).resolve().parent.parent / "tests" / config_path
        if test_path.is_file():
            return test_path
    raise ValueError("Конфигурационный файл не найден")


def read_config(path):
    config_path = find_config(path)
    config = configparser.ConfigParser()
    config.read(config_path, encoding="utf-8")
    return config

def validate_options(config):
    if not config.has_section("settings"):
        raise ValueError("Отсутствует секция [settings]")
    for key in REQUIRED_OPTIONS:
        if not config.has_option("settings", key):
            raise ValueError(f"Отсутствует параметр: {key}")
        
def read_nonempty(settings, key, message):
    value = settings[key].strip()
    if not value:
        raise ValueError(message)
    return value

def read_modes(settings):
    try:
        return (
            settings.getboolean("test_mode"),
            settings.getboolean("ascii_tree"),
        )
    except ValueError as error:
        raise ValueError("Некорректное логическое значение") from error

def validate_repository(repository, test_mode):
    if test_mode:
        if not Path(repository).is_file():
            raise ValueError("Файл тестового репозитория не найден")
    elif urlparse(repository).scheme not in ("http", "https"):
        raise ValueError("Некорректный URL репозитория")

def validate_output_file(output_file):
    if not output_file.endswith(".svg"):
        raise ValueError("Выходной файл должен иметь расширение .svg")
    if Path(output_file).name != output_file:
        raise ValueError("Укажите только имя выходного файла")

def load_config(path):
    config = read_config(path)
    validate_options(config)
    settings = config["settings"]
    package = read_nonempty(
        settings, "package", "Имя пакета не может быть пустым"
    )
    repository = read_nonempty(
        settings, "repository", "Репозиторий не может быть пустым"
    )
    output_file = settings["output_file"].strip()
    test_mode, ascii_tree = read_modes(settings)
    validate_repository(repository, test_mode)
    validate_output_file(output_file)
    return {
        "package": package,
        "repository": repository,
        "test_mode": test_mode,
        "output_file": output_file,
        "ascii_tree": ascii_tree,
    }

def main():
    config_path = sys.argv[1] if len(sys.argv) > 1 else "config.ini"
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