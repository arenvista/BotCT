import os
from pathlib import Path
from openai import OpenAI

# Initialize client
client = OpenAI()

MODEL = "gpt-4.1-mini"  # fast + cheap, change if needed

# -------- CONFIG --------
MAX_FILE_CHARS = 20000   # truncate large files
SUMMARY_PROMPT = """Summarize the following Python file.
Focus on:
- Purpose
- Key functions/classes
- Important logic
Keep it concise but informative.
"""

FINAL_PROMPT = """You are given summaries of many Python files in a codebase.

Produce a high-level overview of the entire codebase:
- What the project does
- Main components/modules
- How pieces interact
- Any patterns or architecture

Be clear and structured.
"""


# -------- HELPERS --------
def get_python_files(root="."):
    return [p for p in Path(root).rglob("*.py") if p.is_file()]


def read_file(path):
    try:
        text = path.read_text(encoding="utf-8", errors="ignore")
        return text[:MAX_FILE_CHARS]
    except Exception as e:
        return f"ERROR READING FILE: {e}"


def call_llm(prompt, content):
    response = client.chat.completions.create(
        model=MODEL,
        messages=[
            {"role": "system", "content": prompt},
            {"role": "user", "content": content},
        ],
        temperature=0.3,
    )
    return response.choices[0].message.content.strip()


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
    print(files)

    if not files:
        print("No Python files found.")
        return

    print(f"Found {len(files)} Python files.\n")

    summaries = summarize_files(files)

    final_summary = summarize_all(summaries)

    # Save outputs
    with open("file_summaries.txt", "w") as f:
        for file, summary in summaries.items():
            f.write(f"=== {file} ===\n{summary}\n\n")

    with open("final_summary.txt", "w") as f:
        f.write(final_summary)

    print("\nDone!")
    print("Saved:")
    print(" - file_summaries.txt")
    print(" - final_summary.txt")


if __name__ == "__main__":
    main()
