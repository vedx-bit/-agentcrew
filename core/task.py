from __future__ import annotations
from dataclasses import dataclass, field
from typing import Callable

@dataclass
class Task:
    description: str
    agent: any
    expected_output: str = ""
    context: list = field(default_factory=list)
    callback: Callable = None
    output: str = field(default="", init=False)

    def _get_context_string(self) -> str:
        if not self.context:
            return ""
        parts = []
        for ctx_task in self.context:
            if ctx_task.output:
                parts.append(f"[Output from '{ctx_task.description[:60]}']\n{ctx_task.output}")
        return "\n\n".join(parts)

    def _mark_complete(self, output: str) -> None:
        self.output = output
        if self.callback:
            self.callback(output)
