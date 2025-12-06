# test_pdf.py

from report_builder import build_pdf
import os

# Build a fake review JSON (no LLM needed)
fake_report = {
    "score": 76,
    "risk_level": "Medium",
    "issues": [
        {"severity": "HIGH", "desc": "Missing error handling", "line": 12},
        {"severity": "LOW", "desc": "Unused import 'os'", "line": 1},
    ],
    "suggestions": [
        "Good function naming.",
        "Logic is readable.",
        "Code structure is clean."
    ],
    "summary": "Overall code quality is decent but needs improvements in error handling and dependency hygiene.",
    "meta": {
        "name": "Lakshy",
        "project": "AI Code Reviewer"
    }
}

# Small fake code example for footer preview
fake_code_snippet = """
import os

def hello():
    print("hello")

hello()
"""

# Path to save PDF
pdf_path = os.path.join("tmp_reports", "test_output.pdf")

# Generate PDF
build_pdf(fake_report, fake_code_snippet, pdf_path)

print("PDF created at:", pdf_path)

