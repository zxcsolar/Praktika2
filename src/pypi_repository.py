import json
from urllib.error import HTTPError, URLError
from urllib.parse import quote
from urllib.request import urlopen


def fetch_metadata(repository, package):
    name = quote(package, safe="")
    url = f"{repository.rstrip('/')}/{name}/json"
    try:
        with urlopen(url, timeout=10) as response:
            return json.load(response)
    except HTTPError as error:
        if error.code == 404:
            raise ValueError(f"Пакет {package} не найден") from error
        raise ValueError(f"Ошибка репозитория: HTTP {error.code}") from error
    except URLError as error:
        raise ValueError(f"Репозиторий недоступен: {error.reason}") from error
    except json.JSONDecodeError as error:
        raise ValueError("Репозиторий вернул некорректный JSON") from error


def package_info(metadata):
    if not isinstance(metadata, dict):
        raise ValueError("В ответе отсутствуют метаданные пакета")
    info = metadata.get("info")
    if not isinstance(info, dict):
        raise ValueError("В ответе отсутствуют метаданные пакета")
    return info


def read_requirements(info):
    requirements = info.get("requires_dist")
    if requirements is None:
        return []
    if not isinstance(requirements, list):
        raise ValueError("Некорректный список зависимостей")
    if not all(isinstance(item, str) for item in requirements):
        raise ValueError("Некорректный список зависимостей")
    return requirements