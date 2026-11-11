from langgraph.graph import StateGraph, END
from workflow.state import ResearchState
from agents.planner import planner_node
from agents.researcher import web_search_node, calculator_node, pdf_reader_node
from agents.analyzer import deduplicate_node, analysis_node
from agents.report_generator import report_node

def route_web(state):
    return "run" if state.get("plan", {}).get("use_web", True) else "skip"

def route_calculator(state):
    return "run" if state.get("plan", {}).get("use_calculator", False) else "skip"

def route_pdf(state):
    should_read = state.get("plan", {}).get("use_pdf", False) and bool(state.get("pdf_bytes"))
    return "run" if should_read else "skip"

def build_research_graph():
    graph = StateGraph(ResearchState)

    graph.add_node("planning", planner_node)
    graph.add_node("web_search", web_search_node)
    graph.add_node("skip_web", lambda state: {})
    graph.add_node("calculator_router", lambda state: {})
    graph.add_node("calculator", calculator_node)
    graph.add_node("skip_calculator", lambda state: {})
    graph.add_node("pdf_router", lambda state: {})
    graph.add_node("pdf_reader", pdf_reader_node)
    graph.add_node("skip_pdf", lambda state: {})
    graph.add_node("deduplicate", deduplicate_node)
    graph.add_node("analysis", analysis_node)
    graph.add_node("report", report_node)

    graph.set_entry_point("planning")

    graph.add_conditional_edges("planning", route_web, {
        "run": "web_search",
        "skip": "skip_web"
    })
    graph.add_edge("web_search", "calculator_router")
    graph.add_edge("skip_web", "calculator_router")

    graph.add_conditional_edges("calculator_router", route_calculator, {
        "run": "calculator",
        "skip": "skip_calculator"
    })
    graph.add_edge("calculator", "pdf_router")
    graph.add_edge("skip_calculator", "pdf_router")

    graph.add_conditional_edges("pdf_router", route_pdf, {
        "run": "pdf_reader",
        "skip": "skip_pdf"
    })
    graph.add_edge("pdf_reader", "deduplicate")
    graph.add_edge("skip_pdf", "deduplicate")

    graph.add_edge("deduplicate", "analysis")
    graph.add_edge("analysis", "report")
    graph.add_edge("report", END)

    return graph.compile()
