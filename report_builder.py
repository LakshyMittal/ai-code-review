# report_builder.py (FINAL — WORKING PRO EDITION)

import os
import datetime
from typing import Dict, Any, List
from textwrap import wrap

from reportlab.lib.pagesizes import A4
from reportlab.lib.units import mm
from reportlab.lib import colors
from reportlab.pdfgen import canvas
import matplotlib.pyplot as plt

from config import TEMP_DIR


# ---------- Visual constants ----------
PAGE_SIZE = A4
PAGE_WIDTH, PAGE_HEIGHT = PAGE_SIZE
MARGIN = 18 * mm

STRENGTH_BG = colors.HexColor("#e9f7ef")
FLAW_BG = colors.HexColor("#fff1f0")
SUMMARY_BG = colors.HexColor("#f3f4f6")
BORDER_COLOR = colors.HexColor("#d6d6d6")
TEXT_COLOR = colors.HexColor("#111111")

H1 = 16
H2 = 12
P = 10
SMALL = 8


# ---------- Helpers ----------
def _make_pie_chart(score: int, outpath: str):
    correct = max(0, min(100, score))
    issues = 100 - correct

    sizes = [correct, issues]
    labels = ["Correct", "Issues"]

    fig, ax = plt.subplots(figsize=(2.2, 2.2), dpi=150)

    wedges, _ = ax.pie(
        sizes,
        startangle=90,
        wedgeprops=dict(width=0.48, edgecolor="w")
    )

    ax.text(0, 0, f"{correct}%", ha="center", va="center",
            fontsize=14, weight="bold", color="#0b5f3a")

    ax.legend(
        wedges,
        labels,
        loc="center left",
        bbox_to_anchor=(1, 0, 0.5, 1),
        frameon=False
    )

    ax.axis("equal")
    plt.tight_layout()
    fig.savefig(outpath, bbox_inches="tight", pad_inches=0.05)
    plt.close(fig)


def _wrap_lines(text: str, width_chars: int) -> List[str]:
    lines = []
    for p in str(text).split("\n"):
        if p.strip():
            lines.extend(wrap(p, width_chars))
        else:
            lines.append("")
    return lines


def _risk_badge_properties(risk_level: str):
    rl = (risk_level or "").lower()
    if rl == "low":
        return ("LOW RISK", colors.HexColor("#0b6b3a"))
    if rl == "high":
        return ("HIGH RISK", colors.HexColor("#c53030"))
    return ("MEDIUM RISK", colors.HexColor("#d69e2e"))


# ---------- PDF generator ----------
def build_pdf(report_json: Dict[str, Any], code_snippet: str, pdf_path: str):
    os.makedirs(os.path.dirname(pdf_path) or ".", exist_ok=True)

    score = int(report_json.get("score", 0))
    chart_path = os.path.join(TEMP_DIR, f"chart_{os.path.basename(pdf_path)}.png")
    _make_pie_chart(score, chart_path)

    c = canvas.Canvas(pdf_path, pagesize=PAGE_SIZE)
    width, height = PAGE_WIDTH, PAGE_HEIGHT

    # ---------- HEADER ----------
    c.setFont("Helvetica-Bold", H1)
    c.setFillColor(TEXT_COLOR)
    c.drawString(MARGIN, height - MARGIN - 4, "CODE REVIEW REPORT")

    c.setFont("Helvetica", SMALL)
    gen = datetime.datetime.now().strftime("%Y-%m-%d %H:%M")
    c.drawRightString(width - MARGIN, height - MARGIN - 2, f"Generated: {gen}")

    name = report_json.get("meta", {}).get("name", "Unknown")
    project = report_json.get("meta", {}).get("project", "")

    meta_line = f"Author: {name}"
    if project:
        meta_line += f"   |   Project: {project}"

    c.setFont("Helvetica", P)
    c.drawString(MARGIN, height - MARGIN - 22, meta_line)

    c.setStrokeColor(BORDER_COLOR)
    c.line(MARGIN, height - MARGIN - 30, width - MARGIN, height - MARGIN - 30)

    # ---------- LAYOUT ----------
    gutter = 12 * mm
    right_col_w = 82 * mm
    left_col_w = width - 2 * MARGIN - gutter - right_col_w

    left_x = MARGIN
    right_x = MARGIN + left_col_w + gutter
    top_y = height - MARGIN - 40

    # ---------- RIGHT COLUMN ----------
    chart_w = right_col_w
    chart_h = chart_w
    chart_x = right_x
    chart_y = top_y - chart_h + 20

    try:
        c.drawImage(chart_path, chart_x, chart_y, chart_w, chart_h,
                    preserveAspectRatio=True, mask="auto")
    except:
        pass

    c.setFont("Helvetica-Bold", 22)
    score_text_y = chart_y - 22
    c.drawString(right_x, score_text_y, f"Score: {score}/100")

    rl_label, rl_color = _risk_badge_properties(report_json.get("risk_level"))
    badge_y = score_text_y - 26

    c.setFillColor(rl_color)
    c.roundRect(right_x, badge_y, 84, 18, 4, fill=1, stroke=0)
    c.setFillColor(colors.white)
    c.setFont("Helvetica-Bold", 9)
    c.drawCentredString(right_x + 42, badge_y + 4, rl_label)

    # Summary
    summary = report_json.get("summary", "")
    summary_lines = _wrap_lines(summary, 46)
    summary_h = 80
    summary_y = badge_y - 10 - summary_h

    c.setFillColor(SUMMARY_BG)
    c.roundRect(right_x, summary_y, right_col_w, summary_h, 4, fill=1, stroke=0)

    c.setFillColor(TEXT_COLOR)
    c.setFont("Helvetica-Bold", 11)
    c.drawString(right_x + 6, summary_y + summary_h - 16, "Executive Summary")

    c.setFont("Helvetica", 9)
    sy = summary_y + summary_h - 32
    for ln in summary_lines[:5]:
        c.drawString(right_x + 6, sy, ln)
        sy -= 12

    # ---------- LEFT COLUMN ----------
    cursor_y = top_y

    # ---------- Strengths ----------
    strengths = report_json.get("strengths", [])

    c.setFont("Helvetica-Bold", H2)
    c.drawString(left_x, cursor_y, "Strengths")
    cursor_y -= 14

    if strengths:
        wrapped = []
        for s in strengths:
            wrapped += _wrap_lines(s, 70)

        box_h = max(44, len(wrapped)*12 + 12)
        box_y = cursor_y - box_h + 6

        c.setFillColor(STRENGTH_BG)
        c.roundRect(left_x, box_y, left_col_w, box_h, 4, fill=1, stroke=0)

        c.setStrokeColor(BORDER_COLOR)
        c.roundRect(left_x, box_y, left_col_w, box_h, 4, fill=0)

        c.setFillColor(TEXT_COLOR)
        c.setFont("Helvetica", P)

        ty = box_y + box_h - 14
        for s in strengths:
            lines = _wrap_lines(s, 70)
            c.drawString(left_x + 8, ty, "✓ " + lines[0])
            ty -= 12
            for extra in lines[1:]:
                c.drawString(left_x + 16, ty, extra)
                ty -= 12

        cursor_y = box_y - 18

    # ---------- Flaws ----------
    issues = report_json.get("flaws", [])

    c.setFont("Helvetica-Bold", H2)
    c.drawString(left_x, cursor_y, "Flaws / Issues")
    cursor_y -= 14

    if issues:
        wrapped = []

        for issue in issues:
            sev = issue.get("severity","").upper()
            line = issue.get("line")
            msg = issue.get("issue","")
            text = f"[{sev}] {msg}" + (f" (line {line})" if line else "")
            wrapped += _wrap_lines(text,70)

        box_h = max(60, len(wrapped)*12 + 12)
        box_y = cursor_y - box_h + 6

        c.setFillColor(FLAW_BG)
        c.roundRect(left_x, box_y, left_col_w, box_h, 4, fill=1, stroke=0)

        c.setStrokeColor(BORDER_COLOR)
        c.roundRect(left_x, box_y, left_col_w, box_h, 4, fill=0)

        c.setFillColor(TEXT_COLOR)
        c.setFont("Helvetica", P)

        ty = box_y + box_h - 14
        for issue in issues:
            sev = issue.get("severity","").upper()
            line = issue.get("line")
            msg = issue.get("issue","")
            text = f"[{sev}] {msg}" + (f" (line {line})" if line else "")

            lines = _wrap_lines(text,70)
            c.drawString(left_x+8, ty, "✗ "+lines[0])
            ty -= 12
            for extra in lines[1:]:
                c.drawString(left_x+16, ty, extra)
                ty -= 12

        cursor_y = box_y - 18

    # ---------- FOOTER ----------
    footer_h = 70
    footer_y = MARGIN + 14

    c.setStrokeColor(BORDER_COLOR)
    c.roundRect(MARGIN, footer_y,
                width - 2*MARGIN,
                footer_h, 4, fill=0)

    c.setFont("Helvetica-Bold",10)
    c.setFillColor(TEXT_COLOR)
    c.drawString(MARGIN+6, footer_y + footer_h - 14,
                 "Code snippet preview:")

    c.setFont("Courier",9)
    snippet = "\n".join(str(code_snippet).splitlines()[:6])
    lines = _wrap_lines(snippet,120)

    cy = footer_y + footer_h - 30
    for ln in lines:
        c.drawString(MARGIN+8, cy, ln)
        cy -= 12

    c.setFont("Helvetica", SMALL)
    c.setFillColor(colors.HexColor("#666666"))
    c.drawRightString(width - MARGIN,
                      footer_y + 6,
                      "AI Code Review — Generated by SAAR")

    c.showPage()
    c.save()

    try:
        os.remove(chart_path)
    except:
        pass
