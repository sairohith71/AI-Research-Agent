from agents.llm import get_llm
from langchain_core.messages import HumanMessage

def report_node(state):
    sources = state.get("sources", [])
    source_text = "\n".join(
        f"[S{i}] {s.get('title')} | {s.get('url')}"
        for i, s in enumerate(sources, start=1)
    ) or "No sources were retrieved."

    prompt = f"""
Create a polished research report for:
{state['topic']}

Use this analysis as the factual basis:
{state.get('analysis', '')}

Produce these sections in this order:
# Research Report
## Executive Summary
## Research Findings
## Key Insights
## Recommendations
## Conclusion
## Limitations
## Supporting Sources

Use [S1], [S2] citations in the body where appropriate. In Supporting Sources, preserve the
reference labels and URLs exactly as provided below. Do not invent or embellish references.
Clearly disclose if the evidence base is limited or conflicting.

Available sources:
{source_text}

Calculator results:
{state.get('calculations', [])}
"""
    try:
        llm = get_llm(temperature=0.2)
        report = llm.invoke([HumanMessage(content=prompt)]).content
        return {"report": report}
    except Exception as exc:
        fallback = (
            "# Research Report\n\n"
            "## Executive Summary\nReport generation failed; see limitations below.\n\n"
            "## Research Findings\n" + state.get("analysis", "No analysis available.") +
            "\n\n## Limitations\nThe report model request failed. Verify the evidence manually."
        )
        return {"report": fallback, "errors": state.get("errors", []) + [f"Report generation failed: {exc}"]}
