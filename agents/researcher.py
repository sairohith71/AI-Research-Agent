from io import BytesIO
from pypdf import PdfReader
from langchain_community.tools.tavily_search import TavilySearchResults
from langchain_community.utilities.tavily_search import TavilySearchAPIWrapper
from tools.calculator import safe_calculate
from config import get_tavily_api_key

def web_search_node(state):
    api_key = get_tavily_api_key()
    if not api_key:
        return {"errors": state.get("errors", []) + ["Web search unavailable: TAVILY_API_KEY is missing."]}
    sources, errors = [], []
    try:
        search_tool = TavilySearchResults(
            max_results=5,
            api_wrapper=TavilySearchAPIWrapper(tavily_api_key=api_key),
        )
        queries = state.get("plan", {}).get("search_queries", [])[:5]
        for query in queries:
            try:
                results = search_tool.invoke({"query": query})
                for result in results or []:
                    sources.append({
                        "title": result.get("title") or "Web search result",
                        "url": result.get("url") or "",
                        "content": result.get("content") or "",
                        "kind": "web"
                    })
            except Exception as exc:
                errors.append(f"Search failed for '{query}': {exc}")
    except Exception as exc:
        errors.append(f"Tavily could not be initialized: {exc}")
    if not sources:
        errors.append("Web search returned no usable results. Findings may be incomplete.")
    return {
        "sources": state.get("sources", []) + sources,
        "errors": state.get("errors", []) + errors
    }

def calculator_node(state):
    tasks = state.get("plan", {}).get("calculation_tasks", [])
    results, errors = [], []
    for task in tasks[:5]:
        question = task.get("question", "Calculation")
        expression = task.get("expression", "")
        try:
            value = safe_calculate(expression)
            results.append({"question": question, "expression": expression, "result": value})
        except Exception as exc:
            errors.append(f"Calculator could not process '{question}': {exc}")
    return {
        "calculations": state.get("calculations", []) + results,
        "errors": state.get("errors", []) + errors
    }

def pdf_reader_node(state):
    pdf_bytes = state.get("pdf_bytes", b"")
    if not pdf_bytes:
        return {}
    try:
        reader = PdfReader(BytesIO(pdf_bytes))
        pages = []
        for page_num, page in enumerate(reader.pages, start=1):
            pages.append(f"[PDF page {page_num}] {page.extract_text() or ''}")
        text = "\n\n".join(pages).strip()
        if not text:
            return {"errors": state.get("errors", []) + ["PDF contains no extractable text. Scanned PDFs require OCR."]}
        source = {
            "title": "User-uploaded PDF",
            "url": "Uploaded document (page references included in content)",
            "content": text[:30000],
            "kind": "pdf"
        }
        return {"sources": state.get("sources", []) + [source]}
    except Exception as exc:
        return {"errors": state.get("errors", []) + [f"PDF reader failed: {exc}"]}
