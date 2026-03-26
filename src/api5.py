import os
from pathlib import Path
from openai import OpenAI

# Ensure you have OPENAI_API_KEY set in your environment variables
client = OpenAI()

# 🔥 Updated to the current strongest model
MODEL = "gpt-5"

# -------- CONFIG --------
MAX_FILE_CHARS = 30000  # truncate huge files to save context/money

# Critical: Ignore virtual environments and caches so you don't summarize third-party libraries
EXCLUDE_DIRS = {".venv", "venv", "env", "__pycache__", ".git", ".tox"}

SUMMARY_PROMPT = """You are analyzing a Python code file.

Return a structured summary with:
1. Purpose of the file
2. Key classes/functions (with brief descriptions)
3. Important logic or algorithms
4. Notable dependencies or patterns

Be concise but information-dense.
"""

FINAL_PROMPT = """You are given summaries of many Python files in a codebase.

Produce a structured, high-level overview:

1. What the project does
2. Core modules/components
3. How components interact
4. Architectural patterns
5. Any notable design decisions or issues

Be clear, organized, and insightful.
"""


# -------- HELPERS --------
def get_python_files(root="."):
    """Recursively finds .py files while explicitly ignoring specified directories."""
    valid_files = []
    for p in Path(root).rglob("*.py"):
        if p.is_file() and not any(part in EXCLUDE_DIRS for part in p.parts) and "api" not in p.__str__():
            valid_files.append(p)
    return valid_files


def read_file(path):
    try:
        text = path.read_text(encoding="utf-8", errors="ignore")
        return text[:MAX_FILE_CHARS]
    except Exception as e:
        return f"ERROR READING FILE: {e}"


def call_llm(prompt, content):
    try:
        response = client.responses.create(
            model=MODEL,  # Assuming MODEL is defined (e.g., "gpt-5")
            input=[
                {"role": "system", "content": prompt},
                {"role": "user", "content": content},
            ],
            reasoning={"effort": "high"},
            text={"verbosity": "high"},  # Options: "low", "medium", "high"
        )
        return response.output_text.strip()
    except Exception as e:
        print(f"\n[!] API Error: {e}")
        return f"API ERROR: {e}"


def suggest_edits(files, context_files):
    sug = {}

    for i, file in enumerate(files):
        print(f"[{i+1}/{len(files)}] Suggesting Edits {file}...")

        content = read_file(file)
        for j, con in enumerate(context_files):
            content += read_file(con)

        suggest_edits = call_llm(
            SUMMARY_PROMPT,
            f"File: {file}\n\n{content}"
        )

        sug[str(file)] = suggest_edits

    return sug

# -------- MAP STEP --------
def summarize_files(files):
    summaries = {}

    for i, file in enumerate(files):
        print(f"[{i+1}/{len(files)}] Summarizing {file}...")

        content = read_file(file)

        summary = call_llm(
            SUMMARY_PROMPT,
            f"File: {file}\n\n{content}"
        )

        summaries[str(file)] = summary

    return summaries


# -------- REDUCE STEP --------
def summarize_all(summaries):
    combined = ""

    for file, summary in summaries.items():
        combined += f"\n=== {file} ===\n{summary}\n"

    print("\n[Reducing summaries into final overview...]\n")

    final = call_llm(FINAL_PROMPT, combined)
    return final


# -------- MAIN --------
def main():
    files = get_python_files()

    if not files:
        print("No Python files found.")
        return

    print(f"Found {len(files)} Python files to summarize.\n")

    # summaries = summarize_files(files)
    # final_summary = summarize_all(summaries)
    # # Save outputs
    # with open("file_summaries.txt", "a", encoding="utf-8") as f:
    #     for file, summary in summaries.items():
    #         f.write(f"=== {file} ===\n{summary}\n\n")
    #
    # with open("final_summary.txt", "w", encoding="utf-8") as f:
    #     f.write(final_summary)

    context_files = [ "/home/sybil/Documents/BotCT/src/file_summaries.txt", "/home/sybil/Documents/BotCT/src/final_summary.txt.txt", ]
    sug = suggest_edits(files, context_files)

    print(f"Found {len(files)} Python files to suggest edits.\n")
    with open("suggest_edits.txt", "a", encoding="utf-8") as f:
        for file, summary in sug.items():
            f.write(f"=== {file} ===\n{summary}\n\n")

    print("\nDone!")
    print("Saved:")
    print(" - file_summaries.txt")
    print(" - final_summary.txt")


if __name__ == "__main__":
    main()
