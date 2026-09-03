import json
from langchain_ollama import ChatOllama
from graph.state import HairState

llm = ChatOllama(model="llama3.2", temperature=0, seed=42)

# --- Fast path: keyword rules (same as the original Phase 1 planner) ---
KEYWORDS = {
    "context": ["why", "reason", "cause", "problem", "recommend", "suggest"],
    "knowledge": ["why", "cause", "recommend", "suggest"],
}

# --- Slow path: LLM fallback, only used when keywords don't match ---
AGENT_PROMPT = """You are answering a single yes/no question for a hair-analysis routing system.

User question: "{question}"

Question to answer: {condition}

Respond with ONLY valid JSON in this exact format, nothing else: {{"answer": true}} or {{"answer": false}}
"""

CONDITIONS = {
    "context": """Should the Context Agent run? It uses the user's personal history (heat styling, chemical treatments, recent changes) to explain a problem.
Answer yes if the user is asking why something is happening, what's causing an issue, or wants a recommendation/suggestion about their hair.
Answer no if the question is only about technical image quality (e.g. "Is this image clear?", "Is this photo blurry?") with no hair-care question involved.

Examples:
Q: "Why is my hair falling out?" -> yes
Q: "What do you recommend for frizz?" -> yes
Q: "Is this image clear?" -> no""",

    "knowledge": """Should the Knowledge Agent run? It looks up general hair-care knowledge to explain causes or give recommendations.
Answer yes if the user wants a hair-care explanation, cause, or recommendation/suggestion.
Answer no if the question is only about technical image quality (e.g. "Is this image clear?", "Is this photo blurry?") with no hair-care question involved.

Examples:
Q: "Why is my hair falling out?" -> yes
Q: "What do you recommend for frizz?" -> yes
Q: "Is this image clear?" -> no""",
}


def _keyword_match(question_lower: str, agent_name: str) -> bool:
    return any(word in question_lower for word in KEYWORDS[agent_name])


def _ask_llm_yes_no(question: str, agent_name: str) -> bool:
    try:
        response = llm.invoke([
            {"role": "user", "content": AGENT_PROMPT.format(question=question, condition=CONDITIONS[agent_name])},
        ])
        parsed = json.loads(response.content.strip())
        return bool(parsed.get("answer", False))
    except (json.JSONDecodeError, AttributeError, KeyError):
        return False


def planner_agent(state: HairState):
    question = state["user_question"]
    question_lower = question.lower()
    has_image = bool(state.get("image_path"))

    selected_agents = []

    if has_image:
        selected_agents.append("vision")

    for agent_name in CONDITIONS:
        if _keyword_match(question_lower, agent_name):
            # Fast path: confident keyword hit, no LLM call needed
            selected_agents.append(agent_name)
        elif _ask_llm_yes_no(question, agent_name):
            # Slow path: keyword missed, let the LLM catch paraphrases
            selected_agents.append(agent_name)

    return {
        "selected_agents": selected_agents
    }