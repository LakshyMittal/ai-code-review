# main.py
import os
import json
from review_engine import review_code
from report_builder import build_pdf
import config

def read_input_code():
    print("Enter path of code file to review (example: sample.py):")
    file_path = input("👉 File path: ").strip()

    if not os.path.exists(file_path):
        print("❌ File not found. Please try again.")
        return None

    with open(file_path, "r", encoding="utf-8") as f:
        return f.read(), file_path

def ask_for_name():
    name = input("Enter author name to include in the report (leave blank to use 'Unknown'): ").strip()
    return name if name else "Unknown"

def main():
    print("\n🚀 SAAR — Smart AI Automated Reviewer")
    print("=====================================")

    author_name = ask_for_name()

    code_data = read_input_code()
    if code_data is None:
        return
    
    code, file_path = code_data

    print("\n📡 Sending code to GPT for review...")
    review = review_code(code)

    if "error" in review:
        print("❌ Error:", review["error"])
        return

    # Ensure meta
    meta = review.get("meta", {}) if isinstance(review.get("meta", {}), dict) else {}
    meta["name"] = author_name
    meta["project"] = meta.get("project", os.path.basename(file_path))
    review["meta"] = meta

    print("\n✅ Review successful! Generating PDF...")

    # DEBUG PRINT (this MUST stay inside main())
    print("\nDEBUG RAW REVIEW:\n", json.dumps(review, indent=4))

    # PDF path
    output_pdf = os.path.join(
        config.TEMP_DIR,
        f"code_review_{os.path.splitext(os.path.basename(file_path))[0]}.pdf"
    )

    # Build PDF
    build_pdf(review, code, output_pdf)

    print("\n🎉 PDF generated successfully!")
    print(f"📄 Output saved at: {output_pdf}\n")

if __name__ == "__main__":
    main()
