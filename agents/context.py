def context_agent(state):
    if "context" not in state.get("selected_agents", []):
        return {}

    user_context = state.get("user_context", {})

    if not user_context:
        return {
            "context_result": {
                "finding": "No additional context provided",
                "confidence": 0.3
            }
        }

    findings = []

    if user_context.get("heat_styling") == "frequent":
        findings.append("Frequent heat exposure reported")

    if user_context.get("chemical_treatment") == "yes":
        findings.append("Chemical treatment reported")

    if user_context.get("recent_changes"):
        findings.append(f"Recent change noted: {user_context['recent_changes']}")

    if not findings:
        return {
            "context_result": {
                "finding": "No significant risk factors reported",
                "confidence": 0.5
            }
        }

    return {
        "context_result": {
            "finding": "; ".join(findings),
            "confidence": 0.9
        }
    }