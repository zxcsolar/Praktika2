import re
from dataclasses import dataclass

from pypi_repository import package_info, read_requirements


NAME = re.compile(r"[a-zA-Z0-9][a-zA-Z0-9._-]*")
REQUIREMENT = re.compile(NAME.pattern + r"(?:\s*\[[^\]]*\])?")
EXTRA_MARKER = re.compile(r"\bextra\s*==")


@dataclass(frozen=True)
class Dependency:
    name: str
    version_spec: str
    requirement: str


@dataclass(frozen=True)
class Package:
    version: str
    dependencies: tuple


def normalize_name(name):
    if not isinstance(name, str) or not NAME.fullmatch(name):
        raise ValueError(f"Некорректное имя пакета: {name}")
    return re.sub(r"[-_.]+", "-", name).lower()


def parse_dependency(requirement):
    match = REQUIREMENT.match(requirement.lstrip())
    if not match:
        raise ValueError(f"Некорректная зависимость: {requirement}")
    name = NAME.match(match.group()).group()
    tail = requirement.lstrip()[match.end():].strip()
    if tail.startswith("@"):
        _, _, marker = tail.partition(" ;")
        version_spec = ""
    else:
        spec, _, marker = tail.partition(";")
        version_spec = spec.strip(" ()")
    if EXTRA_MARKER.search(marker):
        return None
    return Dependency(normalize_name(name), version_spec, requirement)


def read_package(metadata):
    info = package_info(metadata)
    version = info.get("version")
    if not isinstance(version, str) or not version:
        raise ValueError("В ответе отсутствует версия пакета")
    dependencies = []
    for requirement in read_requirements(info):
        dependency = parse_dependency(requirement)
        if dependency is not None:
            dependencies.append(dependency)
    return Package(version, tuple(dependencies))


def add_package(name, fetch, graph, active, stack):
    package = read_package(fetch(name))
    graph[name] = package
    active.add(name)
    stack.append((name, iter(package.dependencies)))


def build_graph(root, fetch):
    graph = {}
    cycles = []
    active = set()
    stack = []
    add_package(normalize_name(root), fetch, graph, active, stack)
    while stack:
        name, dependencies = stack[-1]
        dependency = next(dependencies, None)
        if dependency is None:
            stack.pop()
            active.remove(name)
            continue
        target = dependency.name
        if target in active:
            cycles.append((name, target))
        elif target not in graph:
            add_package(target, fetch, graph, active, stack)
    return graph, cycles