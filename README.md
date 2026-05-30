# AgentCrew

A lightweight Python framework for orchestrating teams of AI agents — supporting both fully-autonomous Crew execution and fine-grained Flow-based pipelines.

---

## Installation

```bash
pip install anthropic          # only dependency
export ANTHROPIC_API_KEY="sk-ant-..."
```

Clone or copy the `agentcrew/` package directory into your project.

---

## Core Concepts

| Concept   | What it is |
|-----------|-----------|
| **Agent** | An AI persona with a `role`, `goal`, optional `backstory`, and optional `tools`. |
| **Task**  | A discrete unit of work assigned to an Agent, with an optional `expected_output` and upstream `context` dependencies. |
| **Crew**  | Runs a list of Tasks using a chosen execution `Process` (sequential or hierarchical). |
| **Flow**  | A Python class where each `@step` method is an explicit stage; steps route to each other by returning a step name. |
| **Tool**  | A callable capability (web search, file I/O, code execution, …) an Agent may invoke during reasoning. |

---

## Quick Start

### 1 — Sequential Crew

```python
from agentcrew import Agent, Task, Crew, Process

researcher = Agent(
    role="Senior Market Researcher",
    goal="Find accurate market data and competitive intelligence.",
    backstory="10 years analysing tech markets.",
)

writer = Agent(
    role="Tech Content Writer",
    goal="Turn raw research into polished reports.",
)

research_task = Task(
    description="Research the {topic} market: size, players, trends, forecast.",
    agent=researcher,
    expected_output="Structured summary with four sections.",
)

writing_task = Task(
    description="Write a 400-word executive summary of the {topic} market.",
    agent=writer,
    expected_output="Polished 400-word summary.",
    context=[research_task],   # receives researcher's output automatically
)

crew = Crew(
    agents=[researcher, writer],
    tasks=[research_task, writing_task],
    process=Process.SEQUENTIAL,
)

result = crew.kickoff(inputs={"topic": "generative AI"})
print(result)                  # final task output
print(result.execution_time)   # seconds elapsed
```

### 2 — Hierarchical Crew

A `manager_agent` coordinates the team and synthesises a final answer:

```python
from agentcrew import Crew, Process

crew = Crew(
    agents=[researcher, analyst],
    tasks=[task1, task2],
    process=Process.HIERARCHICAL,
    manager_agent=manager,
)
result = crew.kickoff()
```

### 3 — Flow (step-by-step pipeline)

```python
from agentcrew import Flow, start, step

class ReportFlow(Flow):

    @start
    def gather_data(self):
        self.state["data"] = self.run_task(Task("Gather market data", agent=researcher))
        return "write_report"          # route to next step by name

    @step
    def write_report(self):
        self.state["final"] = self.run_task(
            Task(f"Write report from: {self.state['data']}", agent=writer)
        )
        # return None (implicit) → flow ends

flow = ReportFlow()
output = flow.kickoff(inputs={"topic": "AI"})
print(output.final)
print(output.steps_executed)   # ['gather_data', 'write_report']
```

#### Conditional routing

```python
@start
def classify(self):
    ...
    return "handle_urgent" if is_urgent else "handle_normal"
```

---

## Tools

### Built-in tools

```python
from agentcrew import WebSearchTool, FileReadTool, FileWriteTool, CodeExecutionTool

agent = Agent(
    role="Researcher",
    goal="...",
    tools=[WebSearchTool(), FileReadTool()],
)
```

### Custom tool — decorator style

```python
from agentcrew import tool

@tool(name="word_count", description="Count words. Input: a plain string.")
def word_count(input):
    return f"{len(str(input).split())} words"

agent = Agent(..., tools=[word_count])
```

### Custom tool — class style

```python
from agentcrew import Tool

class SentimentTool(Tool):
    name = "sentiment"
    description = "Return positive/negative/neutral. Input: a plain string."

    def run(self, input):
        # plug in your sentiment library here
        return "positive"

agent = Agent(..., tools=[SentimentTool()])
```

---

## Running the Examples

```bash
# Basic sequential crew
python agentcrew/examples.py crew_basic

# Hierarchical crew with manager synthesis
python agentcrew/examples.py crew_hierarchical

# Two-step flow (research → haiku)
python agentcrew/examples.py flow_basic

# Flow with conditional routing
python agentcrew/examples.py flow_routing

# Custom tool demonstration
python agentcrew/examples.py custom_tool
```

---

## API Reference

### `Agent`

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `role` | `str` | required | Short label (e.g. `"Senior Researcher"`) |
| `goal` | `str` | required | What the agent is trying to achieve |
| `backstory` | `str` | `""` | Context shaping the agent's reasoning style |
| `tools` | `list[Tool]` | `[]` | Tools the agent may call |
| `verbose` | `bool` | `False` | Log each reasoning iteration |
| `max_iterations` | `int` | `10` | Safety cap on the ReAct loop |
| `model` | `str` | `"claude-sonnet-4-20250514"` | LLM model string |

### `Task`

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `description` | `str` | required | Full description of the work |
| `agent` | `Agent` | required | Assigned agent |
| `expected_output` | `str` | `""` | Hint about desired output format |
| `context` | `list[Task]` | `[]` | Upstream tasks whose output feeds in |
| `callback` | `Callable` | `None` | Called with the output on completion |

### `Crew`

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `agents` | `list[Agent]` | required | All agents in the crew |
| `tasks` | `list[Task]` | required | Tasks to execute |
| `process` | `Process` | `SEQUENTIAL` | Execution strategy |
| `manager_agent` | `Agent` | `None` | Required for `HIERARCHICAL` |
| `verbose` | `bool` | `False` | Step-by-step logging |
| `memory` | `bool` | `True` | Pass accumulated context between tasks |

### `Flow`

Subclass `Flow` and decorate methods:

| Decorator | Meaning |
|-----------|---------|
| `@start`  | Entry point (exactly one per flow) |
| `@step`   | A routable step |
| `@router` | Alias for `@step`, signals a routing decision |

Inside any step:

```python
self.run_task(task, context="")   # execute a task, returns output string
self.state                         # shared dict across all steps
```

`kickoff(inputs={})` → `FlowOutput`

| Attribute | Description |
|-----------|-------------|
| `.final` | `state["final"]` if set, else the whole `state` dict |
| `.state` | Full shared state dict |
| `.steps_executed` | Ordered list of step names that ran |
| `.execution_time` | Wall-clock seconds |

---

## Project Structure

```
agentcrew/
├── __init__.py          # public surface
├── core/
│   ├── agent.py         # Agent + ReAct loop
│   ├── task.py          # Task dataclass
│   ├── crew.py          # Crew orchestrator
│   └── flow.py          # Flow engine + decorators
├── tools/
│   └── tools.py         # Tool base + built-ins
├── utils/
│   ├── llm.py           # Anthropic API wrapper
│   └── logger.py        # Logging setup
└── examples.py          # Runnable usage examples
```

---

## Extending AgentCrew

- **Swap the LLM**: edit `utils/llm.py` — replace the Anthropic call with any provider.
- **Add tools**: subclass `Tool` or use the `@tool` decorator.
- **Parallel execution**: in `crew.py`, swap the sequential loop with `concurrent.futures.ThreadPoolExecutor`.
- **Persistent memory**: hook into `task._mark_complete` to write outputs to a vector store.
