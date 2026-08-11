"""Repository guard: legacy scripts may read, but must never write the master."""

from __future__ import annotations

import ast
from pathlib import Path


MASTER_NAME = "tripadvisor_processed_master.csv"
ROOT = Path(__file__).resolve().parents[1]


def _constant_path(node: ast.AST):
    if isinstance(node, ast.Constant) and isinstance(node.value, str):
        return node.value
    if isinstance(node, ast.Call) and isinstance(node.func, ast.Attribute) and node.func.attr == "join":
        parts = [_constant_path(argument) for argument in node.args]
        if all(part is not None for part in parts):
            return "/".join(parts)
    return None


def test_no_python_script_writes_immutable_master():
    violations = []
    for path in sorted(ROOT.rglob("*.py")):
        if any(part in {".git", ".venv", "__pycache__"} for part in path.parts):
            continue
        tree = ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
        master_variables = set()
        for node in ast.walk(tree):
            if isinstance(node, (ast.Assign, ast.AnnAssign)):
                value = _constant_path(node.value)
                targets = node.targets if isinstance(node, ast.Assign) else [node.target]
                if value and value.replace("\\", "/").endswith(MASTER_NAME):
                    master_variables.update(target.id for target in targets if isinstance(target, ast.Name))
        for node in ast.walk(tree):
            if not isinstance(node, ast.Call) or not isinstance(node.func, ast.Attribute) or node.func.attr != "to_csv":
                continue
            if not node.args:
                continue
            target = node.args[0]
            target_value = _constant_path(target)
            if (isinstance(target, ast.Name) and target.id in master_variables) or (
                target_value and target_value.replace("\\", "/").endswith(MASTER_NAME)
            ):
                violations.append(f"{path.relative_to(ROOT)}:{node.lineno}")
    assert not violations, "Immutable master write(s): " + ", ".join(violations)
