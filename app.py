import streamlit as st
import os
import sys
import importlib.util

# ── Path setup ────────────────────────────────────────────────────────
BASE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, BASE)

def load_module(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    mod = importlib.util.module_from_spec(spec)
    sys.modules[name] = mod
    spec.loader.exec_module(mod)
    return mod

logger_mod = load_module("logger",  os.path.join(BASE, "utils", "logger.py"))
llm_mod    = load_module("llm",     os.path.join(BASE, "utils", "llm.py"))
task_mod   = load_module("task",    os.path.join(BASE, "core",  "task.py"))
agent_mod  = load_module("agent",   os.path.join(BASE, "core",  "agent.py"))
crew_mod   = load_module("crew",    os.path.join(BASE, "core",  "crew.py"))

Agent   = agent_mod.Agent
Task    = task_mod.Task
Crew    = crew_mod.Crew
Process = crew_mod.Process

# ── Page config ───────────────────────────────────────────────────────
st.set_page_config(
    page_title="AgentCrew — AI Workforce",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ── CSS ───────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Space+Grotesk:wght@300;400;500;600;700&family=JetBrains+Mono:wght@400;600&display=swap');

* { font-family: 'Space Grotesk', sans-serif; }
html, body, [data-testid="stAppViewContainer"] { background-color: #0a0a0f; color: #e2e8f0; }
[data-testid="stAppViewContainer"] { background: radial-gradient(ellipse at 20% 50%, #0d0d1a 0%, #0a0a0f 60%); }
[data-testid="stSidebar"] { background: #0d0d1a !important; border-right: 1px solid #1e1e3f; }
[data-testid="stSidebar"] * { color: #e2e8f0 !important; }

.hero-title { font-size: 3.2rem; font-weight: 700; background: linear-gradient(135deg, #a78bfa, #60a5fa, #34d399); -webkit-background-clip: text; -webkit-text-fill-color: transparent; background-clip: text; line-height: 1.1; margin-bottom: 0.5rem; }
.hero-sub { font-size: 1.1rem; color: #64748b; font-weight: 400; letter-spacing: 0.02em; }
.badge { display: inline-block; background: #1e1e3f; border: 1px solid #a78bfa44; color: #a78bfa; font-size: 0.72rem; font-weight: 600; padding: 4px 12px; border-radius: 999px; letter-spacing: 0.1em; text-transform: uppercase; margin-bottom: 1rem; }

.agent-card { background: #0d0d1a; border: 1px solid #1e1e3f; border-radius: 16px; padding: 1.5rem; margin-bottom: 1rem; position: relative; overflow: hidden; }
.agent-card::before { content: ''; position: absolute; top: 0; left: 0; right: 0; height: 2px; background: linear-gradient(90deg, #a78bfa, #60a5fa); }
.agent-role { font-size: 0.7rem; font-weight: 600; color: #a78bfa; letter-spacing: 0.12em; text-transform: uppercase; margin-bottom: 0.3rem; }
.agent-name { font-size: 1rem; font-weight: 600; color: #e2e8f0; }

.stat-card { background: #0d0d1a; border: 1px solid #1e1e3f; border-radius: 12px; padding: 1.2rem 1.5rem; text-align: center; }
.stat-num { font-size: 2rem; font-weight: 700; color: #a78bfa; font-family: 'JetBrains Mono', monospace; }
.stat-label { font-size: 0.75rem; color: #475569; text-transform: uppercase; letter-spacing: 0.08em; margin-top: 0.2rem; }

.result-box { background: #0d0d1a; border: 1px solid #1e1e3f; border-left: 3px solid #a78bfa; border-radius: 12px; padding: 2rem; font-size: 0.95rem; line-height: 1.8; color: #cbd5e1; }
.section-title { font-size: 0.7rem; font-weight: 600; color: #475569; letter-spacing: 0.15em; text-transform: uppercase; margin-bottom: 1rem; padding-bottom: 0.5rem; border-bottom: 1px solid #1e1e3f; }

div[data-testid="stSelectbox"] > div, div[data-testid="stTextInput"] > div > div { background: #0d0d1a !important; border: 1px solid #1e1e3f !important; border-radius: 10px !important; color: #e2e8f0 !important; }
.stButton > button { background: linear-gradient(135deg, #7c3aed, #4f46e5) !important; color: white !important; border: none !important; border-radius: 10px !important; padding: 0.6rem 2rem !important; font-weight: 600 !important; font-size: 0.9rem !important; width: 100% !important; }
.stButton > button:hover { opacity: 0.85 !important; }
label { color: #94a3b8 !important; font-size: 0.82rem !important; font-weight: 500 !important; }
hr { border-color: #1e1e3f !important; }
</style>
""", unsafe_allow_html=True)


# ── Sidebar ───────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown('<div class="badge">⚡ AgentCrew v1.0</div>', unsafe_allow_html=True)
    st.markdown("### Control Panel")
    st.markdown('<div class="section-title">SELECT MODE</div>', unsafe_allow_html=True)

    mode = st.selectbox("Mission Type", [
        "🔬 Market Research",
        "💪 Gym Schedule",
        "📝 Content Writer",
        "🧠 Custom Mission"
    ], label_visibility="collapsed")

    st.markdown("---")
    st.markdown('<div class="section-title">ACTIVE AGENTS</div>', unsafe_allow_html=True)

    agents_info = {
        "🔬 Market Research": [("ANALYST", "Market Researcher"), ("WRITER", "Report Writer")],
        "💪 Gym Schedule":    [("TRAINER", "Fitness Expert"), ("PLANNER", "Schedule Planner")],
        "📝 Content Writer":  [("RESEARCHER", "Topic Researcher"), ("AUTHOR", "Content Author")],
        "🧠 Custom Mission":  [("AGENT 01", "Lead Executor"), ("AGENT 02", "Quality Reviewer")],
    }

    for role, name in agents_info[mode]:
        st.markdown(f'<div class="agent-card"><div class="agent-role">{role}</div><div class="agent-name">{name}</div></div>', unsafe_allow_html=True)

    st.markdown("---")
    st.markdown('<div class="section-title">SYSTEM STATS</div>', unsafe_allow_html=True)
    c1, c2 = st.columns(2)
    with c1:
        st.markdown('<div class="stat-card"><div class="stat-num">2</div><div class="stat-label">Agents</div></div>', unsafe_allow_html=True)
    with c2:
        st.markdown('<div class="stat-card"><div class="stat-num">∞</div><div class="stat-label">Tasks</div></div>', unsafe_allow_html=True)


# ── Main ──────────────────────────────────────────────────────────────
st.markdown('<div class="badge">Final Year Project — AI Systems</div>', unsafe_allow_html=True)
st.markdown('<div class="hero-title">AgentCrew</div>', unsafe_allow_html=True)
st.markdown('<div class="hero-sub">Autonomous AI agent workforce — deploy, orchestrate, execute.</div>', unsafe_allow_html=True)
st.markdown("<br>", unsafe_allow_html=True)


def run_crew(agents, tasks):
    crew = Crew(agents=agents, tasks=tasks, process=Process.SEQUENTIAL)
    return crew.kickoff()


# ── Market Research ───────────────────────────────────────────────────
if mode == "🔬 Market Research":
    st.markdown('<div class="section-title">MISSION PARAMETERS</div>', unsafe_allow_html=True)
    col1, col2 = st.columns([3, 1])
    with col1:
        topic = st.text_input("Target Market", placeholder="e.g. Electric Vehicles, AI SaaS...")
    with col2:
        depth = st.selectbox("Depth", ["Standard", "Deep Dive"])

    if st.button("⚡ Launch Research Mission"):
        if topic:
            with st.spinner("Agents deployed — executing mission..."):
                r = Agent(role="Senior Market Researcher", goal="Find accurate market data.", backstory="Elite market analyst with 10 years experience.")
                w = Agent(role="Strategic Report Writer", goal="Transform research into executive reports.", backstory="Former consultant who writes sharp market briefs.")
                t1 = Task(description=f"Research the {topic} market: size, top players, trends, forecast.", agent=r, expected_output="Comprehensive market intelligence.")
                t2 = Task(description=f"Write a professional executive summary on the {topic} market.", agent=w, expected_output="Polished executive report.", context=[t1])
                result = run_crew([r, w], [t1, t2])
            st.markdown("---")
            st.markdown('<div class="section-title">MISSION OUTPUT</div>', unsafe_allow_html=True)
            st.markdown(f'<div class="result-box">{str(result)}</div>', unsafe_allow_html=True)
            st.download_button("⬇ Download Report", str(result), file_name=f"{topic}_report.txt")
        else:
            st.warning("Enter a target market to begin.")


# ── Gym Schedule ──────────────────────────────────────────────────────
elif mode == "💪 Gym Schedule":
    st.markdown('<div class="section-title">MISSION PARAMETERS</div>', unsafe_allow_html=True)
    col1, col2, col3 = st.columns(3)
    with col1:
        goal = st.selectbox("Primary Goal", ["Muscle Gain", "Weight Loss", "Stay Fit", "Strength"])
    with col2:
        level = st.selectbox("Fitness Level", ["Beginner", "Intermediate", "Advanced"])
    with col3:
        days = st.slider("Days / Week", 2, 6, 4)
    extra = st.text_input("Injuries or preferences?", placeholder="e.g. bad knees, home workout...")

    if st.button("⚡ Generate My Schedule"):
        with st.spinner("Agents building your personalized plan..."):
            trainer = Agent(role="Elite Personal Trainer", goal="Design effective workout plans.", backstory="NSCA certified trainer with 500+ athletes coached.")
            planner = Agent(role="Wellness Schedule Architect", goal="Build practical weekly schedules.", backstory="Sports scientist specializing in recovery and habit design.")
            t1 = Task(description=f"Create a {goal.lower()} workout plan for {level.lower()}, {days} days/week. {('Consider: ' + extra) if extra else ''}", agent=trainer, expected_output="Complete workout plan with exercises, sets, reps.")
            t2 = Task(description="Create a clean 7-day schedule with warm-up, rest days, nutrition and sleep tips.", agent=planner, expected_output="Full weekly schedule.", context=[t1])
            result = run_crew([trainer, planner], [t1, t2])
        st.markdown("---")
        st.markdown('<div class="section-title">YOUR PERSONAL SCHEDULE</div>', unsafe_allow_html=True)
        st.markdown(f'<div class="result-box">{str(result)}</div>', unsafe_allow_html=True)
        st.download_button("⬇ Download Schedule", str(result), file_name="gym_schedule.txt")


# ── Content Writer ────────────────────────────────────────────────────
elif mode == "📝 Content Writer":
    st.markdown('<div class="section-title">MISSION PARAMETERS</div>', unsafe_allow_html=True)
    col1, col2 = st.columns(2)
    with col1:
        content_topic = st.text_input("Topic", placeholder="e.g. Future of AI, Crypto in 2025...")
    with col2:
        content_type = st.selectbox("Content Type", ["Blog Post", "LinkedIn Post", "Twitter Thread", "Essay"])
    tone = st.selectbox("Tone", ["Professional", "Casual", "Motivational", "Technical"])

    if st.button("⚡ Generate Content"):
        if content_topic:
            with st.spinner("Agents crafting your content..."):
                researcher = Agent(role="Content Researcher", goal="Find interesting angles and facts.", backstory="Journalist with 8 years in tech publications.")
                author = Agent(role="Elite Content Creator", goal="Write scroll-stopping content.", backstory="Viral content strategist with 10M+ views.")
                t1 = Task(description=f"Research key facts and angles about: {content_topic}.", agent=researcher, expected_output="Key research points.")
                t2 = Task(description=f"Write a {content_type} about {content_topic} in {tone.lower()} tone.", agent=author, expected_output=f"Complete {content_type}.", context=[t1])
                result = run_crew([researcher, author], [t1, t2])
            st.markdown("---")
            st.markdown('<div class="section-title">GENERATED CONTENT</div>', unsafe_allow_html=True)
            st.markdown(f'<div class="result-box">{str(result)}</div>', unsafe_allow_html=True)
            st.download_button("⬇ Download Content", str(result), file_name="content.txt")
        else:
            st.warning("Enter a topic to begin.")


# ── Custom Mission ────────────────────────────────────────────────────
elif mode == "🧠 Custom Mission":
    st.markdown('<div class="section-title">DEFINE YOUR MISSION</div>', unsafe_allow_html=True)
    a1_role = st.text_input("Agent 1 — Role", placeholder="e.g. Legal Researcher")
    a1_goal = st.text_input("Agent 1 — Goal", placeholder="e.g. Find relevant legal precedents")
    st.markdown("<br>", unsafe_allow_html=True)
    a2_role = st.text_input("Agent 2 — Role", placeholder="e.g. Legal Writer")
    a2_goal = st.text_input("Agent 2 — Goal", placeholder="e.g. Draft a legal brief")
    st.markdown("<br>", unsafe_allow_html=True)
    mission = st.text_area("Mission Brief", placeholder="Describe what you want the agents to accomplish...", height=120)

    if st.button("⚡ Deploy Custom Agents"):
        if all([a1_role, a1_goal, a2_role, a2_goal, mission]):
            with st.spinner("Custom agents deployed..."):
                a1 = Agent(role=a1_role, goal=a1_goal, backstory=f"Expert {a1_role}.")
                a2 = Agent(role=a2_role, goal=a2_goal, backstory=f"Expert {a2_role}.")
                t1 = Task(description=f"Phase 1: {mission}", agent=a1, expected_output="Detailed phase 1 output.")
                t2 = Task(description=f"Phase 2 — complete: {mission}", agent=a2, expected_output="Final output.", context=[t1])
                result = run_crew([a1, a2], [t1, t2])
            st.markdown("---")
            st.markdown('<div class="section-title">MISSION OUTPUT</div>', unsafe_allow_html=True)
            st.markdown(f'<div class="result-box">{str(result)}</div>', unsafe_allow_html=True)
            st.download_button("⬇ Download Output", str(result), file_name="mission_output.txt")
        else:
            st.warning("Fill all fields to deploy agents.")


# ── Footer ────────────────────────────────────────────────────────────
st.markdown("---")
st.markdown('<div style="text-align:center;padding:1rem 0;"><span style="font-size:0.75rem;color:#1e293b;font-family:monospace;letter-spacing:0.1em;">AGENTCREW © 2025 — AUTONOMOUS AI WORKFORCE PLATFORM</span></div>', unsafe_allow_html=True)
