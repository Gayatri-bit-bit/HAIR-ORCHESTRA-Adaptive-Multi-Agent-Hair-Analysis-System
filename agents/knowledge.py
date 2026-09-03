import json
import os


KNOWLEDGE_PATH = os.path.join("data", "hair_knowledge.json")


def load_knowledge():
    with open(KNOWLEDGE_PATH, "r") as f:
        return json.load(f)


def knowledge_agent(state):
    if "knowledge" not in state.get("selected_agents", []):
        return {}

    question = state.get("user_question", "").lower()
    context_finding = state.get("context_result", {}).get("finding", "").lower()

    search_text = f"{question} {context_finding}"

    knowledge_base = load_knowledge()

    matches = []

    for entry in knowledge_base:
        if any(keyword in search_text for keyword in entry["keywords"]):
            matches.append(entry["information"])

    if not matches:
        return {
            "knowledge_result": {
                "finding": "No relevant knowledge found",
                "confidence": 0.3
            }
        }

    return {
        "knowledge_result": {
            "finding": " ".join(matches),
            "confidence": 0.85
        }
    }