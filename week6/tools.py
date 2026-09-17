#!/usr/bin/env python3
"""Tools the LLM can call. Each tool = one Python function."""

import ast
import operator
from datetime import datetime, timezone
from pathlib import Path


def get_current_time() -> str:
    """Return the current UTC time as a string."""
    return datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC")


_SAFE_OPS = {
    ast.Add: operator.add,
    ast.Sub: operator.sub,
    ast.Mult: operator.mul,
    ast.Div: operator.truediv,
    ast.Pow: operator.pow,
    ast.USub: operator.neg,
}


def _eval_node(node):
    if isinstance(node, ast.Constant):
        return node.value
    if isinstance(node, ast.BinOp):
        return _SAFE_OPS[type(node.op)](_eval_node(node.left), _eval_node(node.right))
    if isinstance(node, ast.UnaryOp):
        return _SAFE_OPS[type(node.op)](_eval_node(node.operand))
    raise ValueError(f"Unsupported expression: {node}")


def calculate(expression: str) -> str:
    """Safely evaluate a math expression like '2 + 3 * 4'."""
    tree = ast.parse(expression, mode="eval")
    result = _eval_node(tree.body)
    return f"{expression} = {result}"


REPO_ROOT = Path(__file__).resolve().parent.parent


def read_file(path: str) -> str:
    """Read a file from the repository (relative to automation-lab/)."""
    target = (REPO_ROOT / path).resolve()
    if not str(target).startswith(str(REPO_ROOT)):
        raise ValueError("Access denied: outside repo")
    if not target.exists():
        return f"File not found: {path}"
    if not target.is_file():
        return f"Not a file: {path}"
    content = target.read_text()
    if len(content) > 2000:
        content = content[:2000] + f"\n... [truncated, {len(content)} chars total]"
    return content


TOOL_REGISTRY = {
    "get_current_time": {
        "function": get_current_time,
        "description": "Returns the current UTC date and time.",
        "parameters": {},
    },
    "calculate": {
        "function": calculate,
        "description": "Evaluates a math expression. Supports +, -, *, /, **.",
        "parameters": {
            "expression": {
                "type": "string",
                "description": "Math expression to evaluate.",
            },
        },
    },
    "read_file": {
        "function": read_file,
        "description": "Reads a text file from the automation-lab repository.",
        "parameters": {
            "path": {
                "type": "string",
                "description": "Path relative to the repo root.",
            },
        },
    },
}


def get_tools_for_llm() -> list[dict]:
    """Convert the registry to Ollama's tool format."""
    tools = []
    for name, spec in TOOL_REGISTRY.items():
        tools.append({
            "type": "function",
            "function": {
                "name": name,
                "description": spec["description"],
                "parameters": {
                    "type": "object",
                    "properties": spec["parameters"],
                    "required": list(spec["parameters"].keys()),
                },
            },
        })
    return tools


def call_tool(name: str, args: dict) -> str:
    """Execute a tool by name with given arguments."""
    if name not in TOOL_REGISTRY:
        return f"Unknown tool: {name}"
    try:
        return TOOL_REGISTRY[name]["function"](**args)
    except Exception as e:
        return f"Tool error: {e}"


if __name__ == "__main__":
    print(get_current_time())
    print(calculate("2 + 3 * 4"))
    print(read_file("README.md")[:100])
