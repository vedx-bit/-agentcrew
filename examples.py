"""
AgentCrew — Usage Examples
===========================

Run any example with:
    python examples.py crew_basic
    python examples.py crew_hierarchical
    python examples.py flow_basic
    python examples.py flow_routing
    python examples.py custom_tool

Set your API key first:
    export ANTHROPIC_API_KEY="sk-ant-..."
"""

import sys
import os

# Allow running from the repo root without installing
sys.path.insert(0, os.path.dirname(__file__))

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from agentcrew import (
    Agent, Task, Crew, Process,
    Flow, start, step, router,
    Tool, tool, WebSearchTool, FileReadTool, FileWriteTool,
)


# ════════════════════════════════════════════════════════════════════
# Example 1 — Basic sequential Crew
# ════════════════════════════════════════════════════════════════════

def example_crew_basic():
    """A researcher and a writer collaborate to produce a market report."""

    researcher = Agent(
        role="Senior Market Researcher",
        goal="Find accurate, up-to-date market data and competitive intelligence.",
        backstory=(
            "You have 10 years of experience analysing tech markets. "
            "You are known for rigorous sourcing and clear summaries."
        ),
        verbose=True,
    )

    writer = Agent(
        role="Tech Content Writer",
        goal="Turn raw research into polished, publication-ready reports.",
        backstory=(
            "You write for a business audience. Your reports are concise, "
            "well-structured, and backed by data."
        ),
        verbose=True,
    )

    research_task = Task(
        description=(
            "Research the current state of the {topic} market. "
            "Cover: market size, top 3 players, recent trends, growth forecast."
        ),
        agent=researcher,
        expected_output=(
            "A structured summary with sections: Market Size, Key Players, "
            "Trends, Growth Forecast."
        ),
    )

    writing_task = Task(
        description=(
            "Using the research provided, write a 400-word executive summary "
            "of the {topic} market suitable for a board presentation."
        ),
        agent=writer,
        expected_output="A polished 400-word executive summary with an intro, body, and conclusion.",
        context=[research_task],   # <-- explicit dependency
    )

    crew = Crew(
        agents=[researcher, writer],
        tasks=[research_task, writing_task],
        process=Process.SEQUENTIAL,
        verbose=True,
    )

    result = crew.kickoff(inputs={"topic": "generative AI"})
    print("\n" + "="*60)
    print("FINAL REPORT")
    print("="*60)
    print(result)
    print(f"\n⏱  Completed in {result.execution_time}s | Tasks: {result.tasks_completed}")


# ════════════════════════════════════════════════════════════════════
# Example 2 — Hierarchical Crew with a manager
# ════════════════════════════════════════════════════════════════════

def example_crew_hierarchical():
    """A manager synthesises outputs from a researcher and a data analyst."""

    manager = Agent(
        role="Project Manager",
        goal="Coordinate the team and deliver a single, coherent final report.",
        backstory="You are a seasoned PM who synthesises diverse inputs into clear deliverables.",
    )

    researcher = Agent(
        role="Business Researcher",
        goal="Gather qualitative insights about the target market.",
    )

    analyst = Agent(
        role="Data Analyst",
        goal="Provide quantitative analysis and statistics.",
    )

    task1 = Task(
        description="Identify the top 5 challenges facing small e-commerce businesses in 2025.",
        agent=researcher,
        expected_output="A numbered list of 5 challenges with brief explanations.",
    )

    task2 = Task(
        description="Provide key statistics on e-commerce growth, cart abandonment rate, and mobile commerce share.",
        agent=analyst,
        expected_output="A table or bullet list of statistics with sources cited where possible.",
    )

    crew = Crew(
        agents=[researcher, analyst],
        tasks=[task1, task2],
        process=Process.HIERARCHICAL,
        manager_agent=manager,
        verbose=True,
    )

    result = crew.kickoff()
    print("\n" + "="*60)
    print("SYNTHESISED REPORT (by manager)")
    print("="*60)
    print(result)


# ════════════════════════════════════════════════════════════════════
# Example 3 — Basic Flow
# ════════════════════════════════════════════════════════════════════

def example_flow_basic():
    """A two-step flow: gather brief research → produce a haiku about it."""

    researcher = Agent(
        role="Poet-Researcher",
        goal="Find one surprising fact about a topic.",
    )

    poet = Agent(
        role="Haiku Poet",
        goal="Distil facts into haiku.",
    )

    class ResearchToHaikuFlow(Flow):

        @start
        def do_research(self):
            task = Task(
                description=f"Find one surprising fact about {self.state['topic']}.",
                agent=researcher,
                expected_output="One sentence.",
            )
            self.state["fact"] = self.run_task(task)
            return "write_haiku"

        @step
        def write_haiku(self):
            task = Task(
                description=f"Write a haiku inspired by: {self.state['fact']}",
                agent=poet,
                expected_output="A 5-7-5 haiku.",
            )
            self.state["final"] = self.run_task(task)

    flow = ResearchToHaikuFlow()
    output = flow.kickoff(inputs={"topic": "black holes"})

    print("\n" + "="*60)
    print("HAIKU")
    print("="*60)
    print(output.final)
    print(f"\nSteps executed: {output.steps_executed}")


# ════════════════════════════════════════════════════════════════════
# Example 4 — Flow with routing
# ════════════════════════════════════════════════════════════════════

def example_flow_routing():
    """Demonstrates conditional routing: length of content decides next step."""

    writer = Agent(
        role="Content Writer",
        goal="Write content to spec.",
    )

    editor = Agent(
        role="Editor",
        goal="Tighten and polish prose.",
    )

    class ContentFlow(Flow):

        @start
        def draft(self):
            task = Task(
                description="Write a 3-sentence summary of the importance of sleep.",
                agent=writer,
            )
            draft = self.run_task(task)
            self.state["draft"] = draft
            # Route based on word count
            words = len(draft.split())
            print(f"  [router] draft word count = {words}")
            return "edit" if words > 30 else "publish_short"

        @step
        def edit(self):
            task = Task(
                description=f"Tighten this draft to under 30 words:\n{self.state['draft']}",
                agent=editor,
            )
            self.state["final"] = self.run_task(task)
            # No return → flow ends

        @step
        def publish_short(self):
            self.state["final"] = self.state["draft"]
            print("  [publish_short] Draft is already concise — publishing as-is.")

    flow = ContentFlow()
    output = flow.kickoff()
    print("\n" + "="*60)
    print("FINAL CONTENT")
    print("="*60)
    print(output.final)
    print(f"\nPath taken: {' → '.join(output.steps_executed)}")


# ════════════════════════════════════════════════════════════════════
# Example 5 — Custom tool
# ════════════════════════════════════════════════════════════════════

def example_custom_tool():
    """Shows how to build and attach a custom tool to an agent."""

    # Option A: decorator style
    @tool(
        name="word_count",
        description="Count words in a piece of text. Input: a plain string.",
    )
    def word_count_tool(input):
        return f"{len(str(input).split())} words"

    # Option B: class style
    class UpperCaseTool(Tool):
        name = "to_uppercase"
        description = "Convert text to uppercase. Input: a plain string."

        def run(self, input):
            return str(input).upper()

    agent = Agent(
        role="Text Processor",
        goal="Analyse and transform text snippets.",
        tools=[word_count_tool, UpperCaseTool()],
        verbose=True,
    )

    task = Task(
        description=(
            "Take the sentence 'The quick brown fox jumps over the lazy dog.' "
            "First count its words, then convert it to uppercase."
        ),
        agent=agent,
        expected_output="Word count and the uppercase version of the sentence.",
    )

    crew = Crew(agents=[agent], tasks=[task])
    result = crew.kickoff()
    print("\n" + "="*60)
    print("RESULT")
    print("="*60)
    print(result)


# ════════════════════════════════════════════════════════════════════
# Dispatcher
# ════════════════════════════════════════════════════════════════════
def example_gym_schedule():
    """A fitness expert and a scheduler create a personalized gym plan."""

    fitness_expert = Agent(
        role="Professional Fitness Expert",
        goal="Create the most effective workout plan based on the person's goals.",
        backstory=(
            "You are a certified personal trainer with 10 years of experience. "
            "You know exactly which exercises work best for different goals."
        ),
        verbose=True,
    )

    scheduler = Agent(
        role="Schedule Planner",
        goal="Create a practical weekly schedule that is easy to follow.",
        backstory=(
            "You create simple, realistic schedules that people can actually stick to. "
            "You consider rest days and recovery time."
        ),
        verbose=True,
    )

    research_task = Task(
        description=(
            "Create a detailed workout plan for someone who wants to {goal}. "
            "Their fitness level is {level}. "
            "They can go to gym {days} days per week. "
            "Include: exercises, sets, reps, and which muscle groups to target each day."
        ),
        agent=fitness_expert,
        expected_output="A detailed workout plan with exercises, sets and reps.",
    )

    schedule_task = Task(
        description=(
            "Take the workout plan and create a clean weekly schedule. "
            "Make it easy to read and follow. "
            "Add rest days, diet tips, and motivation tips."
        ),
        agent=scheduler,
        expected_output="A complete weekly gym schedule that is easy to follow.",
        context=[research_task],
    )

    crew = Crew(
        agents=[fitness_expert, scheduler],
        tasks=[research_task, schedule_task],
        process=Process.SEQUENTIAL,
        verbose=True,
    )

    result = crew.kickoff(inputs={
        "goal": "muscle gain",      # <-- yahan apna goal likho
        "level": "beginner",        # <-- beginner / intermediate / advanced
        "days": "4",                # <-- kitne din gym jaoge
    })

    print("\n" + "="*60)
    print("TERA GYM SCHEDULE")
    print("="*60)
    print(result)
EXAMPLES = {
    "crew_basic": example_crew_basic,
    "crew_hierarchical": example_crew_hierarchical,
    "flow_basic": example_flow_basic,
    "flow_routing": example_flow_routing,
    "custom_tool": example_custom_tool,
    "gym_schedule": example_gym_schedule,
}

if __name__ == "__main__":
    name = sys.argv[1] if len(sys.argv) > 1 else "crew_basic"
    fn = EXAMPLES.get(name)
    if fn is None:
        print(f"Unknown example '{name}'. Choose from: {list(EXAMPLES)}")
        sys.exit(1)
    print(f"\n▶  Running example: {name}\n")
    fn()
