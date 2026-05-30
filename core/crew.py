from __future__ import annotations
import time
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from dataclasses import dataclass, field
from enum import Enum
from typing import Any
from core.agent import Agent
from core.task import Task
from utils.logger import get_logger

logger = get_logger(__name__)

class Process(Enum):
    SEQUENTIAL = "sequential"
    HIERARCHICAL = "hierarchical"

@dataclass
class CrewOutput:
    raw: str
    task_outputs: list = field(default_factory=list)
    execution_time: float = 0.0
    tasks_completed: int = 0
    def __str__(self): return self.raw

@dataclass
class Crew:
    agents: list
    tasks: list
    process: Process = Process.SEQUENTIAL
    manager_agent: Any = None
    verbose: bool = False
    memory: bool = True

    def kickoff(self, inputs=None) -> CrewOutput:
        if inputs:
            self._interpolate_inputs(inputs)
        start = time.time()
        logger.info("=== Crew kickoff | process=%s | tasks=%d ===", self.process.value, len(self.tasks))
        output = self._run_sequential()
        elapsed = time.time() - start
        return CrewOutput(
            raw=output,
            task_outputs=[t.output for t in self.tasks],
            execution_time=round(elapsed, 2),
            tasks_completed=sum(1 for t in self.tasks if t.output),
        )

    def _run_sequential(self) -> str:
        accumulated_context = ""
        for i, task in enumerate(self.tasks, 1):
            logger.info("[%d/%d] Running task -> agent: %s", i, len(self.tasks), task.agent.role)
            context = task._get_context_string()
            if self.memory and accumulated_context:
                context = (context + "\n\n" + accumulated_context).strip()
            output = task.agent.execute_task(task, context=context)
            task._mark_complete(output)
            if self.memory:
                accumulated_context += f"\n\n[{task.agent.role}]: {output}"
        return self.tasks[-1].output if self.tasks else ""

    def _interpolate_inputs(self, inputs):
        for task in self.tasks:
            for key, value in inputs.items():
                task.description = task.description.replace(f"{{{key}}}", str(value))
                task.expected_output = task.expected_output.replace(f"{{{key}}}", str(value))
