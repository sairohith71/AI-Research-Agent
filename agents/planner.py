import json
import re

from agents.llm import get_llm
from langchain_core.messages import HumanMessage


def _llm():
    return get_llm(temperature=0)


def extract_json(raw):
    """Extract valid JSON from an LLM response."""

    if not raw:
        raise ValueError("The AI model returned an empty response.")

    raw = raw.strip()

    # Remove Markdown code fences
    raw = re.sub(r"^```(?:json)?\s*", "", raw, flags=re.IGNORECASE)
    raw = re.sub(r"\s*```$", "", raw)

    # First attempt: parse the complete response
    try:
        return json.loads(raw)
    except json.JSONDecodeError:
        pass

    # Second attempt: extract the JSON object
    match = re.search(r"\{.*\}", raw, re.DOTALL)

    if match:
        return json.loads(match.group())

    raise ValueError("No valid JSON object found in model response.")


def planner_node(state):

    topic = state["topic"]
    has_pdf = bool(state.get("pdf_bytes"))

    prompt = f"""
You are a research planning assistant.

Create a research plan for:
{topic}

PDF available: {has_pdf}

Return ONLY a valid JSON object.
Do not include explanations or Markdown.

Use exactly this structure:

{{
    "intent": "Research objective",
    "research_questions": [
        "Question 1",
        "Question 2",
        "Question 3"
    ],
    "subtasks": [
        "Background research",
        "Evidence collection",
        "Analysis"
    ],
    "search_queries": [
        "Search query 1",
        "Search query 2",
        "Search query 3"
    ],
    "use_web": true,
    "use_calculator": false,
    "calculation_tasks": [],
    "use_pdf": {str(has_pdf).lower()}
}}

Rules:
- Use web research for factual or external information.
- Use calculator only when numerical calculations are needed.
- Use PDF only if a PDF is available.
- Never invent numerical inputs.
- Return valid JSON only.
"""

    try:

        response = _llm().invoke(
            [HumanMessage(content=prompt)]
        )

        raw = response.content

        plan = extract_json(raw)

        # Validate and complete required fields
        plan.setdefault("intent", topic)
        plan.setdefault("research_questions", [topic])
        plan.setdefault("subtasks", ["Background", "Research", "Analysis"])
        plan.setdefault("search_queries", [topic])
        plan.setdefault("use_web", True)
        plan.setdefault("use_calculator", False)
        plan.setdefault("calculation_tasks", [])
        plan.setdefault("use_pdf", has_pdf)

        return {"plan": plan}

    except Exception as exc:

        # Fallback plan if the model response is invalid
        fallback_plan = {
            "intent": "General research on " + topic,
            "research_questions": [
                topic,
                "What are the important findings?",
                "What are the benefits and limitations?"
            ],
            "subtasks": [
                "Background research",
                "Collect relevant evidence",
                "Analyze findings",
                "Prepare conclusions"
            ],
            "search_queries": [
                topic,
                topic + " latest research",
                topic + " benefits and challenges"
            ],
            "use_web": True,
            "use_calculator": False,
            "calculation_tasks": [],
            "use_pdf": has_pdf
        }

        return {
            "plan": fallback_plan,
            "errors": state.get("errors", []) + [
                f"Planning error; fallback plan used: {exc}"
            ]
        }