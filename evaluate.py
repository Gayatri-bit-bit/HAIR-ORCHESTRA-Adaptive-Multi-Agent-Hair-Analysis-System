import time

from graph.workflow import build_workflow
from graph.baseline_workflow import build_baseline_workflow


TEST_CASES = [
    {
        "user_question": "Why does my hair look dry?",
        "image_path": "images/hair.jpg",
        "user_context": {"heat_styling": "frequent", "chemical_treatment": "no"}
    },
    {
        "user_question": "Is this image clear?",
        "image_path": "images/hair.jpg",
        "user_context": {}
    },
    {
        "user_question": "What do you recommend for frizz?",
        "image_path": "images/hair.jpg",
        "user_context": {"chemical_treatment": "yes"}
    },
]


def count_agent_calls(result):
    calls = 0
    for key in ("vision_result", "context_result", "knowledge_result"):
        if result.get(key):
            calls += 1
    return calls


def run_eval(app, label):
    print(f"\n=== {label} ===")
    total_calls = 0
    total_time = 0.0
    review_activations = 0

    for i, case in enumerate(TEST_CASES, start=1):
        start = time.time()
        result = app.invoke(case)
        elapsed = time.time() - start

        calls = count_agent_calls(result)
        reviewed = "review_result" in result

        total_calls += calls
        total_time += elapsed
        if reviewed:
            review_activations += 1

        print(f"Case {i}: agents_ran={calls}, reviewed={reviewed}, time={elapsed:.4f}s")

    print(f"Total agent calls: {total_calls}")
    print(f"Total review activations: {review_activations}")
    print(f"Total time: {total_time:.4f}s")

    return {
        "total_calls": total_calls,
        "review_activations": review_activations,
        "total_time": total_time
    }


if __name__ == "__main__":
    adaptive_app = build_workflow()
    baseline_app = build_baseline_workflow()

    adaptive_stats = run_eval(adaptive_app, "Adaptive MAS")
    baseline_stats = run_eval(baseline_app, "Baseline (all agents always run)")

    print("\n=== Comparison ===")
    saved_calls = baseline_stats["total_calls"] - adaptive_stats["total_calls"]
    print(f"Agent calls saved by adaptive routing: {saved_calls}")