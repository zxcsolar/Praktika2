import subprocess
from pathlib import Path


def dot_quote(text):
    escaped = text.replace("\\", "\\\\").replace('"', '\\"')
    escaped = escaped.replace("\r", "").replace("\n", "\\n")
    return f'"{escaped}"'


def package_label(name, package, test_mode):
    display_name = name.upper() if test_mode else name
    return f"{display_name} ({package.version})"


def build_dot(graph, test_mode):
    lines = ["digraph dependencies {", "  node [shape=box];"]
    for name, package in graph.items():
        source = dot_quote(name)
        label = dot_quote(package_label(name, package, test_mode))
        lines.append(f"  {source} [label={label}];")
        for dependency in package.dependencies:
            target = dot_quote(dependency.name)
            label = dot_quote(dependency.version_spec)
            lines.append(f"  {source} -> {target} [label={label}];")
    lines.append("}")
    return "\n".join(lines)


def save_svg(graph, output_file, test_mode):
    dot_source = build_dot(graph, test_mode).encode("utf-8")
    try:
        result = subprocess.run(
            ["dot", "-Tsvg"], input=dot_source, capture_output=True,
            check=True,
        )
    except FileNotFoundError as error:
        message = "Graphviz не найден: команда dot нужна в PATH"
        raise ValueError(message) from error
    except subprocess.CalledProcessError as error:
        details = error.stderr.decode("utf-8", errors="replace").strip()
        raise ValueError(f"Ошибка Graphviz: {details}") from error
    directory = Path(__file__).resolve().parents[1] / "images"
    directory.mkdir(exist_ok=True)
    path = directory / Path(output_file).name
    path.write_bytes(result.stdout)
    return path


def push_children(stack, package, prefix):
    for index in reversed(range(len(package.dependencies))):
        edge = package.dependencies[index]
        last = index == len(package.dependencies) - 1
        stack.append((edge.name, prefix, last))


def print_tree(graph, root, test_mode):
    print(package_label(root, graph[root], test_mode))
    expanded = {root}
    stack = []
    push_children(stack, graph[root], "")
    while stack:
        name, prefix, last = stack.pop()
        branch = "+-- " if last else "|-- "
        label = package_label(name, graph[name], test_mode)
        if name in expanded:
            print(prefix + branch + label + " [повтор]")
            continue
        print(prefix + branch + label)
        expanded.add(name)
        extension = "    " if last else "|   "
        push_children(stack, graph[name], prefix + extension)
