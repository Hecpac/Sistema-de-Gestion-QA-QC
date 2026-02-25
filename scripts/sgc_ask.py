#!/usr/bin/env python3
from __future__ import annotations

import os
import subprocess
import sys
import unicodedata
from pathlib import Path


def resolve_repo_root() -> Path:
    env_root = os.getenv("SGC_REPO_ROOT")
    if env_root:
        return Path(env_root).expanduser().resolve()
    return Path(__file__).resolve().parents[1]


def normalize(text: str) -> str:
    lowered = text.lower()
    decomposed = unicodedata.normalize("NFKD", lowered)
    return "".join(ch for ch in decomposed if not unicodedata.combining(ch))


def load_docs(repo_root: Path) -> list[dict[str, str]]:
    docs: list[dict[str, str]] = []
    for filepath in repo_root.joinpath("docs").rglob("*.md"):
        try:
            content = filepath.read_text(encoding="utf-8")
            docs.append(
                {
                    "path": str(filepath),
                    "content": content,
                    "name": filepath.name,
                }
            )
        except Exception:
            # Skip unreadable files.
            continue
    return docs


def retrieve_relevant_docs(query: str, docs: list[dict[str, str]], top_k: int = 4) -> list[dict[str, str]]:
    terms = [t for t in normalize(query).split() if t]
    scored: list[tuple[int, dict[str, str]]] = []

    for doc in docs:
        score = 0
        content_norm = normalize(doc["content"])
        path_norm = normalize(doc["path"])

        for term in terms:
            if term in path_norm:
                score += 10
            score += content_norm.count(term)

        if score > 0:
            scored.append((score, doc))

    scored.sort(key=lambda item: item[0], reverse=True)
    return [item[1] for item in scored[:top_k]]


def ask_gemini(query: str, context_docs: list[dict[str, str]]) -> str:
    context_text = ""
    for doc in context_docs:
        context_text += f"\n--- DOCUMENT: {doc['name']} ({doc['path']}) ---\n{doc['content']}\n"

    prompt = f"""
Act as a Construction Field Copilot (SGC-AI).
Answer the user's question using ONLY the provided context documents.
If the answer is found, quote the specific value and the Document Code/Section.
If the answer is NOT in the context, say "Data not found in SGC documents."

CONTEXT:
{context_text}

USER QUESTION:
{query}

ANSWER (Concise, for field personnel):
"""

    try:
        print("📚 Sources selected for context:")
        for doc in context_docs:
            print(f" - {doc['name']}")
        print("-" * 40)

        result = subprocess.run(
            ["gemini", prompt],
            capture_output=True,
            text=True,
            check=True,
        )
        return result.stdout.strip()
    except Exception as exc:  # noqa: BLE001
        return f"Error calling AI: {exc}"


def main() -> int:
    if len(sys.argv) < 2:
        print('Usage: python scripts/sgc_ask.py "Your question here"')
        return 1

    query = sys.argv[1]
    repo_root = resolve_repo_root()

    docs = load_docs(repo_root)
    relevant = retrieve_relevant_docs(query, docs)

    if not relevant:
        print("❌ No relevant documents found via keywords.")
        return 0

    answer = ask_gemini(query, relevant)
    print("\n🤖 SGC Copilot Answer:")
    print(answer)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
