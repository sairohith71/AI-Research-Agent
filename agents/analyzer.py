from difflib import SequenceMatcher
from agents.llm import get_llm
from langchain_core.messages import HumanMessage

def deduplicate_node(state):
    unique, fingerprints = [], []
    for source in state.get("sources", []):
        title = (source.get("title") or "").strip().lower()
        url = (source.get("url") or "").strip().lower().rstrip("/")
        content = " ".join((source.get("content") or "").lower().split())
        duplicate = False
        for old_title, old_url, old_content in fingerprints:
            if url and old_url and url == old_url:
                duplicate = True
                break
            if content and old_content and SequenceMatcher(None, content[:1500], old_content[:1500]).ratio() > 0.94:
                duplicate = True
                break
            if title and old_title and title == old_title and not content:
                duplicate = True
                break
        if not duplicate:
            unique.append(source)
            fingerprints.append((title, url, content))
    return {"sources": unique}

def analysis_node(state):
    sources = state.get("sources", [])
    evidence_parts = []
    for idx, source in enumerate(sources, start=1):
        evidence_parts.append(
            f"[S{idx}] TITLE: {source.get('title')}\n"
            f"URL: {source.get('url')}\n"
            f"CONTENT: {(source.get('content') or '')[:4500]}"
        )
    evidence = "\n\n".join(evidence_parts) or "No evidence was retrieved."
    calculations = state.get("calculations", [])
    prompt = f"""
Analyze the evidence for this research objective:
{state['topic']}

Research plan:
{state.get('plan', {})}

Evidence:
{evidence}

Calculator results:
{calculations}

Write a rigorous synthesis with:
1. Main findings, each supported by [S#] citations where evidence exists.
2. Key insights.
3. Conflicting claims or differing figures, identifying both sources.
4. Evidence gaps and limitations.
5. Recommendations grounded in the evidence.
6. A clear distinction between sourced facts and your interpretation.

Do not invent data, sources, dates, quotations, or citations. If evidence is absent or insufficient,
say so explicitly. Treat search snippets as preliminary evidence, not as independently verified facts.
"""
    try:
        llm = get_llm(temperature=0.2)
        analysis = llm.invoke([HumanMessage(content=prompt)]).content
        return {"analysis": analysis}
    except Exception as exc:
        return {
            "analysis": "Analysis could not be completed because the AI model request failed. "
                        "No unsupported conclusions have been generated.",
            "errors": state.get("errors", []) + [f"Analysis failed: {exc}"]
        }
