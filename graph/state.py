from typing import Any, TypedDict


class HairState(TypedDict, total=False):
    user_question: str
    image_path: str
    user_context: dict[str, Any]

    selected_agents: list[str]

    vision_result: dict[str, Any]
    context_result: dict[str, Any]
    knowledge_result: dict[str, Any]

    decision: dict[str, Any]
    review_result: dict[str, Any]

    final_answer: str