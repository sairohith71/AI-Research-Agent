from typing import TypedDict, List

class ResearchState(TypedDict, total=False):
    topic: str
    pdf_bytes: bytes
    plan: dict
    sources: List[dict]
    calculations: List[dict]
    errors: List[str]
    analysis: str
    report: str
