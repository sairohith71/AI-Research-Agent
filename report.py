from io import BytesIO
import re
from xml.sax.saxutils import escape
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_CENTER
from reportlab.lib.units import mm
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer

def create_pdf(markdown_text: str, title: str = "Research Report") -> bytes:
    output = BytesIO()
    doc = SimpleDocTemplate(
        output, pagesize=A4, rightMargin=18*mm, leftMargin=18*mm,
        topMargin=18*mm, bottomMargin=18*mm
    )
    styles = getSampleStyleSheet()
    styles.add(ParagraphStyle(
        name="MainReportTitle", parent=styles["Title"],
        alignment=TA_CENTER, spaceAfter=18
    ))
    story = [Paragraph(escape(title), styles["MainReportTitle"]), Spacer(1, 8)]

    for raw_line in markdown_text.splitlines():
        line = raw_line.strip()
        if not line:
            story.append(Spacer(1, 5))
            continue
        if line.startswith("# "):
            story.append(Paragraph(escape(line[2:]), styles["Heading1"]))
        elif line.startswith("## "):
            story.append(Paragraph(escape(line[3:]), styles["Heading2"]))
        elif line.startswith("### "):
            story.append(Paragraph(escape(line[4:]), styles["Heading3"]))
        else:
            if line.startswith(("- ", "* ")):
                line = "• " + line[2:]
            safe = escape(line)
            safe = re.sub(r"\*\*(.+?)\*\*", r"<b>\1</b>", safe)
            safe = re.sub(r"\*(.+?)\*", r"<i>\1</i>", safe)
            story.append(Paragraph(safe, styles["BodyText"]))
            story.append(Spacer(1, 3))

    doc.build(story)
    return output.getvalue()
