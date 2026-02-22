#!/usr/bin/env python3
from __future__ import annotations

import argparse
import os
import subprocess
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable

DEFAULT_TIMEOUT_S = 90


@dataclass(frozen=True)
class LoadedDoc:
    path: Path
    name: str
    content: str


def repo_root() -> Path:
    raw = os.getenv("SGC_REPO_ROOT", "")
    if raw:
        return Path(raw).resolve()
    return Path(__file__).resolve().parents[1]


def iter_markdown_files(docs_root: Path) -> Iterable[Path]:
    yield from sorted(docs_root.rglob("*.md"))


def load_docs(docs_root: Path) -> list[LoadedDoc]:
    docs: list[LoadedDoc] = []
    for filepath in iter_markdown_files(docs_root):
        try:
            content = filepath.read_text(encoding="utf-8")
        except (OSError, UnicodeDecodeError) as exc:
            print(f"WARN: no se pudo leer {filepath}: {exc}", file=sys.stderr)
            continue
        docs.append(LoadedDoc(path=filepath, content=content, name=filepath.name))
    return docs

def retrieve_relevant_docs(query, docs, top_k=3):
    # Simple Keyword Scoring (TF-IDF style but dumber/faster)
    terms = query.lower().split()
    scored = []
    
    for doc in docs:
        score = 0
        content_lower = doc["content"].lower()
        path_lower = doc["path"].lower()
        
        for term in terms:
            # Title/Path match is worth more
            if term in path_lower:
                score += 10
            # Content match
            score += content_lower.count(term)
            
        if score > 0:
            scored.append((score, doc))
            
    # Sort by score desc
    scored.sort(key=lambda x: x[0], reverse=True)
    return [item[1] for item in scored[:top_k]]

def ask_gemini(query, context_docs):
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
        # Debug: print which docs were selected
        print(f"📚 Sources selected for context:")
        for doc in context_docs:
            print(f" - {doc['name']}")
        print("-" * 40)

        result = subprocess.run(
            ["gemini"],
            input=prompt,
            capture_output=True,
            text=True,
            check=True,
            timeout=DEFAULT_TIMEOUT_S,
        )
        return result.stdout.strip()
    except FileNotFoundError:
        return "Error: 'gemini' CLI not found. Please install it."
    except subprocess.TimeoutExpired:
        return f"Error: gemini timeout after {DEFAULT_TIMEOUT_S}s."
    except Exception as e:
        return f"Error calling AI: {e}"

def main():
    parser = argparse.ArgumentParser(description="Consulta SGC (keyword RAG + Gemini CLI)")
    parser.add_argument("query", help="Pregunta en lenguaje natural")
    parser.add_argument("--repo-root", default=os.getenv("SGC_REPO_ROOT", ""), help="Ruta raiz del repo SGC")
    parser.add_argument("--docs-root", default="docs", help="Carpeta docs relativa al repo-root")
    parser.add_argument("--top-k", type=int, default=3, help="Numero de documentos a usar como contexto")
    args = parser.parse_args()

    root = Path(args.repo_root).resolve() if args.repo_root else repo_root()
    docs_root = (root / args.docs_root).resolve()
    if not docs_root.exists():
        print(f"ERROR: docs_root no existe: {docs_root}", file=sys.stderr)
        sys.exit(2)

    query = args.query

    # 1. Load
    docs = load_docs(docs_root)
    
    # 2. Retrieve
    raw_docs = [{"path": str(d.path), "content": d.content, "name": d.name} for d in docs]
    relevant = retrieve_relevant_docs(query, raw_docs, top_k=args.top_k)
    
    if not relevant:
        print("❌ No relevant documents found via keywords.")
        sys.exit(0)
        
    # 3. Generate
    answer = ask_gemini(query, relevant)
    
    print("\n🤖 SGC Copilot Answer:")
    print(answer)

if __name__ == "__main__":
    main()
