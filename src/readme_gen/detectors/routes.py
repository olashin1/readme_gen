from __future__ import annotations

import ast
import re
from pathlib import Path

from readme_gen.detectors.path_filters import is_test_file
from readme_gen.models import ApiRoute


MAX_FILE_SIZE = 512_000
HTTP_METHODS = "get|post|put|patch|delete|options|head"


def detect_api_routes(
    root: Path,
    files: list[Path],
) -> list[ApiRoute]:
    routes: list[ApiRoute] = []

    for path in files:
        if is_test_file(root, path):
            continue
        if path.suffix.lower() == ".py":
            content = _read_small_text(path)
            if content is not None:
                routes.extend(_python_routes(root, path, content))
        elif path.suffix.lower() in {".js", ".jsx", ".ts", ".tsx"}:
            content = _read_small_text(path)
            if content is not None:
                routes.extend(_express_routes(root, path, content))

    unique: dict[tuple[str, str, str], ApiRoute] = {}
    for route in routes:
        unique[(route.method, route.path, route.source)] = route

    return sorted(
        unique.values(),
        key=lambda route: (route.path, route.method, route.source),
    )


def _python_routes(root: Path, path: Path, content: str) -> list[ApiRoute]:
    routes: list[ApiRoute] = []
    source = path.relative_to(root).as_posix()
    try:
        tree = ast.parse(content)
    except SyntaxError:
        return []

    router_prefix = ""
    for node in ast.walk(tree):
        if not isinstance(node, ast.Call) or _call_name(node.func) != "APIRouter":
            continue
        for keyword in node.keywords:
            if keyword.arg == "prefix" and isinstance(keyword.value, ast.Constant) and isinstance(keyword.value.value, str):
                router_prefix = keyword.value.value

    for node in ast.walk(tree):
        if not isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            continue
        for decorator in node.decorator_list:
            if not isinstance(decorator, ast.Call) or not isinstance(decorator.func, ast.Attribute):
                continue
            if not decorator.args or not isinstance(decorator.args[0], ast.Constant) or not isinstance(decorator.args[0].value, str):
                continue
            owner = _call_name(decorator.func.value).lower()
            method_name = decorator.func.attr.lower()
            route_path = decorator.args[0].value

            if method_name in HTTP_METHODS.split("|"):
                if owner == "router" and router_prefix:
                    route_path = _join_route_paths(router_prefix, route_path)
                methods = [method_name]
            elif method_name == "route":
                methods = _flask_methods(decorator)
            else:
                continue

            for method in methods:
                routes.append(
                    ApiRoute(
                        method=method.upper(),
                        path=route_path,
                        handler=node.name,
                        source=source,
                    )
                )
    return routes


def _flask_methods(decorator: ast.Call) -> list[str]:
    for keyword in decorator.keywords:
        if keyword.arg != "methods" or not isinstance(keyword.value, (ast.List, ast.Tuple)):
            continue
        methods = [
            item.value
            for item in keyword.value.elts
            if isinstance(item, ast.Constant) and isinstance(item.value, str)
        ]
        return methods or ["GET"]
    return ["GET"]


def _call_name(node: ast.expr) -> str:
    if isinstance(node, ast.Name):
        return node.id
    if isinstance(node, ast.Attribute):
        return node.attr
    return ""


def _express_routes(root: Path, path: Path, content: str) -> list[ApiRoute]:
    source = path.relative_to(root).as_posix()
    pattern = re.compile(
        rf"\b(?:app|router)\.(?P<method>{HTTP_METHODS})\(\s*['\"](?P<path>[^'\"]+)['\"]\s*,\s*(?P<handler>[A-Za-z_$][\w$]*)?",
        re.IGNORECASE,
    )
    return [
        ApiRoute(
            method=match.group("method").upper(),
            path=match.group("path"),
            handler=match.group("handler") or None,
            source=source,
        )
        for match in pattern.finditer(content)
    ]


def _join_route_paths(prefix: str, route: str) -> str:
    if route == "/":
        return prefix.rstrip("/") or "/"
    return f"{prefix.rstrip('/')}/{route.lstrip('/')}"


def _read_small_text(path: Path) -> str | None:
    try:
        if path.stat().st_size > MAX_FILE_SIZE:
            return None
        return path.read_text(encoding="utf-8", errors="replace")
    except OSError:
        return None
