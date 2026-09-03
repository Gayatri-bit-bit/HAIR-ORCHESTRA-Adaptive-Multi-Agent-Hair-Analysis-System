def review_agent(state):
    decision = state.get("decision", {})

    if decision.get("reliable", True):
        return {
            "review_result": {
                "action": "NONE",
                "reason": "Decision was already reliable"
            }
        }

    vision = state.get("vision_result", {})
    context = state.get("context_result", {})

    vision_error = bool(vision.get("error"))
    image_quality = vision.get("image_quality", "good")
    has_context = bool(context.get("finding"))

    if vision_error or image_quality in ("blurry", "poor_lighting"):
        reason = vision.get("error") if vision_error else f"Image quality issue detected: {image_quality}"
        return {
            "review_result": {
                "action": "REQUEST_NEW_IMAGE",
                "reason": reason
            }
        }

    if not has_context:
        return {
            "review_result": {
                "action": "REQUEST_MORE_CONTEXT",
                "reason": "Insufficient context to reach a confident conclusion"
            }
        }

    return {
        "review_result": {
            "action": "CONTINUE_WITH_LIMITATION",
            "reason": "Evidence is inconclusive but no clear corrective action available"
        }
    }