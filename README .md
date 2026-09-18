# HAIR-ORCHESTRA

**An adaptive, hardware-integrated multi-agent system for hair image analysis**, where specialized agents dynamically collaborate, evaluate evidence, detect uncertainty, and request additional information or image recapture when required.

This is **not** Multi-Agent Reinforcement Learning (MARL). It is a **Multi-Agent System (MAS)** using rule-and-LLM-based agent orchestration, built with [LangGraph](https://github.com/langchain-ai/langgraph).

---

## Tech stack

| Layer | Tools |
|---|---|
| Orchestration | LangGraph, LangChain |
| Reasoning / routing | Ollama + llama3.2 (local LLM), langchain-ollama |
| Computer vision | OpenCV (Laplacian variance, grayscale brightness, resolution) |
| State & validation | Pydantic |
| Knowledge base | JSON (RAG upgrade planned) |
| Environment | Python 3.10, venv, VS Code, Git |

**Planned:** Streamlit (UI) · FAISS/Chroma embeddings (RAG) · ESP32-CAM over Wi-Fi/HTTP (hardware capture loop)

---

## Architecture

```
User
  │
  ▼
Planner Agent  ──► selects which agents are actually needed
  │
  ├─► Vision Agent      (OpenCV: blur, brightness, resolution)
  ├─► Context Agent     (personal history: heat styling, chemical treatment, recent changes)
  └─► Knowledge Agent   (hair-care knowledge base lookup)
        │
        ▼
   Decision Agent  ──► averages confidence, checks image quality
        │
        ├─ reliable  ──► Final Result
        └─ unreliable ─► Review Agent
                            ├─ REQUEST_NEW_IMAGE
                            ├─ REQUEST_MORE_CONTEXT
                            └─ CONTINUE_WITH_LIMITATION
```

**Planned (not yet built):** ESP32-CAM → Wi-Fi/HTTP → Python backend → Acquisition Agent → MAS, closing the loop so a poor-quality capture can trigger a `RECAPTURE` / `INCREASE_LIGHT` command back to the camera.

---

## Why adaptive routing?

Most of the "work" a multi-agent system can do isn't always needed. If a user only asks *"Is this image clear?"*, there's no reason to run a knowledge-base lookup or ask about their styling history. The **Planner Agent** decides, per request, which of Vision / Context / Knowledge actually need to run — instead of running everything, every time.

To prove this actually helps (rather than just assuming it), the project includes an **evaluation harness** (`evaluate.py`) that runs the same test cases through:

- the **adaptive** graph (Planner decides which agents run), and
- a **baseline** graph (`baseline_workflow.py`, all agents always run),

and compares total agent calls, false Review activations, and execution time.

---

## Evaluation results

| Metric | Adaptive | Baseline |
|---|---|---|
| Total agent calls | 7 | 9 |
| Review activations | 0 | 1 |
| Agent calls saved | **22%** (2 of 9) | — |

The baseline's single Review activation is a genuine finding, not a bug: on a pure image-quality question, baseline runs Context and Knowledge anyway, producing low-confidence "findings" that dilute the average confidence enough to falsely flag the result for review. Adaptive routing avoids this by simply not running agents that have nothing to contribute.

---

## The Planner: three iterations, and what each one taught me

The Planner went through three real designs, each with a measured trade-off — documented here because the *process* is arguably the most interesting part of this project.

### 1. Keyword matching (baseline design)

Simple `if "why" in question` style rules selecting each agent. Fast (near-zero cost), but brittle: an early evaluation run caught a real bug where the Context-selection keyword list didn't include "recommend"/"suggest" (while Knowledge's list did), so recommendation-only questions ran Knowledge without Context, starving it of supporting information and triggering an unnecessary Review. Fixed by syncing the keyword lists — after the fix, the "agent calls saved" figure dropped from an initially-reported 33% to the honest **22%**, since the earlier number was partly inflated by the bug's under-selection.

### 2. LLM-based routing (Ollama / llama3.2, local)

To fix keyword matching's fundamental brittleness to paraphrasing, the Planner was rebuilt to ask a local LLM (via `langchain-ollama`) a yes/no question per candidate agent. This surfaced two real issues worth documenting:

- **Non-determinism**: identical prompts returned different answers across separate process runs (though consistent *within* a run), even at `temperature=0` — a known quirk of local/quantized model serving. Fixed with an explicit `seed`.
- **Prompt precision**: the LLM initially reproduced the same false-positive pattern found in the keyword version (a pure image-quality question triggered an unnecessary Knowledge Agent call). Fixed with few-shot examples in the prompt, including an explicit negative example.

Once fixed, the LLM Planner matched the keyword version's correctness exactly (7 calls, 0 false reviews, 22% saved) — but at a real cost: **~55x slower** (4.77s vs. 0.087s total, since each request now required multiple LLM calls).

### 3. Hybrid Planner (current, final design)

Rather than accept either extreme, the final Planner tries the keyword check first for each agent (near-zero cost) and only escalates to a single LLM call when keywords don't match — catching paraphrases without paying the LLM cost on every request. Result: **identical correctness** to both prior versions, at **~3.2x the speed of the pure-LLM version**. Cost now scales with actual question ambiguity, not with every request.

| Planner version | Agent calls | False reviews | Total time |
|---|---|---|---|
| Keyword-only | 7 | 0 | 0.087s |
| Pure LLM | 7 | 0 | 4.77s |
| **Hybrid (current)** | **7** | **0** | **1.48s** |

---

## Project structure

```
hair-orchestra/
├── agents/
│   ├── planner.py           # hybrid keyword + LLM router
│   ├── vision.py            # OpenCV blur/brightness/resolution analysis
│   ├── context.py           # personal-history reasoning
│   ├── knowledge.py         # hair-care knowledge base lookup
│   ├── decision.py          # reliability scoring
│   └── review.py            # recapture / more-info / limitation decisions
├── graph/
│   ├── state.py
│   ├── workflow.py          # adaptive graph
│   └── baseline_workflow.py # baseline graph (always runs everything)
├── data/
│   └── hair_knowledge.json
├── images/
├── evaluate.py
└── main.py
```

---

## Setup

```bash
python -m venv venv
venv\Scripts\Activate.ps1      # Windows PowerShell
pip install langgraph langchain langchain-ollama opencv-python pydantic
```

The Planner's fallback path needs a local LLM — install [Ollama](https://ollama.com/download), then:

```bash
ollama pull llama3.2
```

Run it:

```bash
python main.py
python evaluate.py   # adaptive vs. baseline comparison
```

---

## Roadmap

- [ ] **RAG-based Knowledge Agent** — replace JSON keyword matching with embeddings + vector search
- [ ] **User interface** (Streamlit)
- [ ] **Hardware integration** — ESP32-CAM capture loop with recapture/lighting feedback

---

## Author

Built by **Vallabhajosyula Sai Gayatri** as a first Multi-Agent System project, with a focus on measuring real trade-offs (correctness vs. speed, keyword vs. LLM routing) rather than assuming any single design is best.
