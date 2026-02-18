#!/usr/bin/env python3
import sys
import os
import subprocess
import glob

def load_docs(repo_root):
    docs = []
    # Recursively find markdown files in docs/
    search_path = os.path.join(repo_root, "docs", "**", "*.md")
    for filepath in glob.glob(search_path, recursive=True):
        try:
            with open(filepath, 'r') as f:
                content = f.read()
                docs.append({
                    "path": filepath,
                    "content": content,
                    "name": os.path.basename(filepath)
                })
        except Exception:
            pass # Skip binary or unreadable
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
            ["gemini", prompt],
            capture_output=True,
            text=True,
            check=True
        )
        return result.stdout.strip()
    except Exception as e:
        return f"Error calling AI: {e}"

def main():
    if len(sys.argv) < 2:
        print("Usage: python sgc_ask.py \"Your question here\"")
        sys.exit(1)
        
    query = sys.argv[1]
    repo_root = "projects/Sistema-de-Gestion-QA-QC"
    
    # 1. Load
    docs = load_docs(repo_root)
    
    # 2. Retrieve
    relevant = retrieve_relevant_docs(query, docs)
    
    if not relevant:
        print("❌ No relevant documents found via keywords.")
        sys.exit(0)
        
    # 3. Generate
    answer = ask_gemini(query, relevant)
    
    print("\n🤖 SGC Copilot Answer:")
    print(answer)

if __name__ == "__main__":
    main()
