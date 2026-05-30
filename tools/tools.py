"""
Tools — reusable capabilities that agents can call during execution.

Built-in tools
--------------
- ``WebSearchTool``   Perform a web search (stub; wire to a real search API).
- ``FileReadTool``    Read a local text file.
- ``FileWriteTool``   Write content to a local file.
- ``CodeExecutionTool``  Execute a Python snippet and return stdout.

Creating custom tools
---------------------
Subclass :class:`Tool` and implement ``run``::

    class MyTool(Tool):
        name = "my_tool"
        description = "Does something useful. Input: a plain string query."

        def run(self, input: Any) -> str:
            ...
            return "result"

Or use the :func:`tool` decorator for quick one-liners::

    @tool(name="add_numbers", description="Adds two numbers. Input: {\"a\": 1, \"b\": 2}")
    def add(input):
        return input["a"] + input["b"]
"""

from __future__ import annotations

import subprocess
import sys
from abc import ABC, abstractmethod
from pathlib import Path
from typing import Any, Callable


# ------------------------------------------------------------------ #
# Base                                                                 #
# ------------------------------------------------------------------ #

class Tool(ABC):
    """Abstract base class for all tools."""

    name: str = ""
    description: str = ""

    @abstractmethod
    def run(self, input: Any) -> str:
        """Execute the tool and return a string result."""

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}(name={self.name!r})"


# ------------------------------------------------------------------ #
# Decorator helper                                                     #
# ------------------------------------------------------------------ #

def tool(name: str, description: str) -> Callable:
    """Wrap a plain function as a Tool.

    Example::

        @tool(name="reverse", description="Reverse a string. Input: a plain string.")
        def reverse_tool(input):
            return str(input)[::-1]
    """
    def decorator(fn: Callable) -> Tool:
        _fn = fn  # capture in closure

        class _FuncTool(Tool):
            def run(self, input: Any) -> str:
                return str(_fn(input))

        _FuncTool.name = name
        _FuncTool.description = description
        return _FuncTool()
    return decorator


# ------------------------------------------------------------------ #
# Built-in tools                                                       #
# ------------------------------------------------------------------ #

class WebSearchTool(Tool):
    """Stub web-search tool.

    Replace ``_search`` with a real implementation (e.g. Serper, Tavily,
    DuckDuckGo) by subclassing or monkey-patching.
    """

    name = "web_search"
    description = (
        "Search the web for information. "
        "Input: a plain string search query."
    )

    def run(self, input: Any) -> str:
        query = str(input)
        # ---- swap this stub with a real API call ----
        return (
            f"[WebSearchTool] Stub result for query: '{query}'. "
            "Integrate a real search API (Serper, Tavily, DuckDuckGo) "
            "by subclassing WebSearchTool and overriding run()."
        )


class FileReadTool(Tool):
    """Read the contents of a local text file."""

    name = "file_read"
    description = (
        "Read a local file and return its contents. "
        'Input: {"path": "<absolute or relative file path>"}'
    )

    def run(self, input: Any) -> str:
        if isinstance(input, dict):
            path = input.get("path", "")
        else:
            path = str(input)
        try:
            return Path(path).read_text(encoding="utf-8")
        except Exception as exc:
            return f"FileReadTool error: {exc}"


class FileWriteTool(Tool):
    """Write content to a local file, creating directories as needed."""

    name = "file_write"
    description = (
        "Write content to a local file. "
        'Input: {"path": "<file path>", "content": "<text to write>"}'
    )

    def run(self, input: Any) -> str:
        if not isinstance(input, dict):
            return "FileWriteTool error: input must be a JSON object with 'path' and 'content'."
        path_str = input.get("path", "")
        content = input.get("content", "")
        try:
            p = Path(path_str)
            p.parent.mkdir(parents=True, exist_ok=True)
            p.write_text(content, encoding="utf-8")
            return f"Successfully wrote {len(content)} characters to '{path_str}'."
        except Exception as exc:
            return f"FileWriteTool error: {exc}"


class CodeExecutionTool(Tool):
    """Execute a Python snippet in a subprocess and return stdout."""

    name = "code_execution"
    description = (
        "Execute a Python code snippet and return stdout + stderr. "
        "Input: a string of valid Python code. USE WITH CAUTION."
    )

    def run(self, input: Any) -> str:
        code = str(input)
        try:
            result = subprocess.run(
                [sys.executable, "-c", code],
                capture_output=True,
                text=True,
                timeout=30,
            )
            output = result.stdout
            if result.stderr:
                output += f"\nSTDERR:\n{result.stderr}"
            return output or "(no output)"
        except subprocess.TimeoutExpired:
            return "CodeExecutionTool error: execution timed out (30s)."
        except Exception as exc:
            return f"CodeExecutionTool error: {exc}"
