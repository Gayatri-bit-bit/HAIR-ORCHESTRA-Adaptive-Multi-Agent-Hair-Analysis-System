def decision_agent(state):
    vision = state.get("vision_result", {})
    context = state.get("context_result", {})
    knowledge = state.get("knowledge_result", {})

    confidences = []
    reasons = []

    vision_error = bool(vision.get("error"))

    if vision:
        if vision_error:
            reasons.append(f"Vision error: {vision.get('error')}")
        else:
            confidences.append(vision.get("confidence", 0))
            if vision.get("image_quality") == "good":
                reasons.append("Image quality is good")
            else:
                reasons.append(f"Image quality flagged as {vision.get('image_quality')}")

    if context:
        confidences.append(context.get("confidence", 0))
        reasons.append(context.get("finding", ""))

    if knowledge:
        confidences.append(knowledge.get("confidence", 0))
        reasons.append(knowledge.get("finding", ""))

    if not confidences and not vision_error:
        return {
            "decision": {
                "reliable": False,
                "reason": "No agent results available",
                "average_confidence": 0.0
            }
        }

    average_confidence = sum(confidences) / len(confidences) if confidences else 0.0

    # A vision error is an automatic block on reliability
    vision_ok = (not vision_error) and (
        vision.get("image_quality", "good") == "good" if vision else True
    )

    reliable = average_confidence >= 0.7 and vision_ok

    return {
        "decision": {
            "reliable": reliable,
            "reason": " | ".join(r for r in reasons if r),
            "average_confidence": round(average_confidence, 2)
        }
    }