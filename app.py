from pathlib import Path

import streamlit as st
from dotenv import load_dotenv

from config import get_tavily_api_key
from workflow.graph import build_research_graph
from report import create_pdf
from auth import show_login_page


# ==========================================
# APPLICATION CONFIGURATION
# ==========================================

BASE_DIR = Path(__file__).resolve().parent

load_dotenv(
    dotenv_path=BASE_DIR / ".env",
    override=True
)

st.set_page_config(
    page_title="AI Research Agent",
    page_icon="🔎",
    layout="wide"
)


# ==========================================
# AUTHENTICATION
# ==========================================

if not st.session_state.get("authenticated", False):
    show_login_page()
    st.stop()


# ==========================================
# SIDEBAR - USER LOGIN
# ==========================================

with st.sidebar:

    st.markdown(
        f"**Signed in as:** "
        f"{st.session_state.get('username', 'User')}"
    )

    if st.button("Log out", use_container_width=True):

        st.session_state.pop("authenticated", None)
        st.session_state.pop("username", None)
        st.session_state.pop("research_result", None)

        st.rerun()

    st.divider()


# ==========================================
# MAIN APPLICATION HEADER
# ==========================================

st.title("🔎 AI-Powered Research Agent")

st.write(
    "Enter a research objective. The agent plans the work, "
    "selects relevant tools, analyzes evidence, and creates "
    "a downloadable report."
)


# ==========================================
# SIDEBAR - AVAILABLE TOOLS
# ==========================================

with st.sidebar:

    st.header("Available tools")

    st.write("- Tavily web search")
    st.write("- Safe arithmetic calculator")
    st.write("- Uploaded PDF reader")
    st.write("- PDF report export")

    st.divider()


# ==========================================
# SIDEBAR - CONTACT DEVELOPER
# ==========================================

with st.sidebar:

    st.subheader("👨‍💻 Contact Developer")

    st.markdown("**Sai Rohith Royal**")

    st.caption(
        "AI/ML Developer | Computer Science Engineer"
    )

    st.write(
        "Have suggestions, questions, or feedback? "
        "Feel free to connect with me!"
    )

    st.markdown(
        "🐙 [GitHub](https://github.com/sairohith71)"
    )

    st.markdown(
        "💼 [LinkedIn](https://www.linkedin.com/in/sai-rohith-royal/)"
    )

    st.markdown(
        "📧 [Email ](sairohithroyal01@gmail.com)"
    )

    st.divider()

    st.caption(
        "Tavily key is read from .env. Planning, analysis, "
        "and report writing use local Ollama."
    )


# ==========================================
# API CONFIGURATION
# ==========================================

missing = []

if not get_tavily_api_key():
    missing.append("TAVILY_API_KEY")

if missing:

    st.warning(
        "Missing configuration: "
        + ", ".join(missing)
        + ". Configure the Tavily API key in Streamlit Cloud Secrets."
    )


# ==========================================
# LLM INFORMATION
# ==========================================

st.info(
    "LLM mode: local Ollama model "
    "(no OpenAI API key or OpenAI credits required)."
)


# ==========================================
# RESEARCH INPUT
# ==========================================

topic = st.text_area(
    "Research topic or objective",
    height=120,
    placeholder=(
        "Research current applications of Generative AI "
        "in healthcare and identify five emerging opportunities."
    )
)

uploaded_pdf = st.file_uploader(
    "Optional: upload a PDF to include in the research",
    type=["pdf"]
)


# ==========================================
# START RESEARCH
# ==========================================

if st.button(
    "Start research",
    type="primary",
    disabled=not topic.strip()
):

    if missing:

        st.error(
            "Add the required API keys before starting research."
        )

    else:

        pdf_bytes = (
            uploaded_pdf.getvalue()
            if uploaded_pdf
            else b""
        )

        progress = st.status(
            "Research agent is working...",
            expanded=True
        )

        try:

            progress.write(
                "Planning the research and selecting tools..."
            )

            graph = build_research_graph()

            result = graph.invoke({

                "topic": topic.strip(),

                "pdf_bytes": pdf_bytes,

                "plan": {},

                "sources": [],

                "calculations": [],

                "errors": [],

                "analysis": "",

                "report": ""

            })

            progress.update(
                label="Research completed",
                state="complete",
                expanded=False
            )

            st.session_state["research_result"] = result

        except Exception as exc:

            progress.update(
                label="Research stopped",
                state="error",
                expanded=True
            )

            st.exception(exc)


# ==========================================
# DISPLAY RESEARCH RESULTS
# ==========================================

result = st.session_state.get("research_result")

if result:

    st.divider()

    st.success(
        "Research workflow completed. "
        "Review the evidence and report below."
    )


    # --------------------------------------
    # 1. RESEARCH PLAN
    # --------------------------------------

    with st.expander(
        "1. Research plan and tool selection",
        expanded=True
    ):

        st.json(
            result.get("plan", {})
        )


    # --------------------------------------
    # 2. RETRIEVED SOURCES
    # --------------------------------------

    with st.expander(
        "2. Retrieved sources",
        expanded=False
    ):

        sources = result.get("sources", [])

        if not sources:

            st.info(
                "No external or uploaded-document sources were available."
            )

        for idx, source in enumerate(sources, start=1):

            st.markdown(
                f"**[S{idx}] "
                f"{source.get('title', 'Untitled source')}**"
            )

            if source.get("url"):

                st.write(
                    source["url"]
                )

            st.write(
                source.get("content", "")[:3500]
            )


    # --------------------------------------
    # 3. CALCULATOR RESULTS
    # --------------------------------------

    with st.expander(
        "3. Calculator results",
        expanded=False
    ):

        calculations = result.get("calculations", [])

        if calculations:

            for item in calculations:

                st.write(
                    f"**Question:** {item.get('question')}"
                )

                st.code(
                    str(item.get("result"))
                )

        else:

            st.info(
                "The planner did not select the calculator."
            )


    # --------------------------------------
    # 4. ANALYSIS
    # --------------------------------------

    with st.expander(
        "4. Analysis",
        expanded=False
    ):

        st.markdown(
            result.get(
                "analysis",
                "No analysis was generated."
            )
        )


    # --------------------------------------
    # 5. FINAL RESEARCH REPORT
    # --------------------------------------

    st.subheader(
        "5. Final research report"
    )

    st.markdown(
        result.get(
            "report",
            "No report was generated."
        )
    )


    # --------------------------------------
    # PDF REPORT DOWNLOAD
    # --------------------------------------

    pdf_data = create_pdf(
        result.get("report", ""),
        result.get("topic", "Research Report")
    )

    st.download_button(
        "⬇️ Download research report (PDF)",
        data=pdf_data,
        file_name="AI_Research_Report.pdf",
        mime="application/pdf"
    )


    # --------------------------------------
    # EXECUTION WARNINGS
    # --------------------------------------

    errors = result.get("errors", [])

    if errors:

        with st.expander(
            "Execution warnings and limitations",
            expanded=True
        ):

            for err in errors:

                st.warning(err)