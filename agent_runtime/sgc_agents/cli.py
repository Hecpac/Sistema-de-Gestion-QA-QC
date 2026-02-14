from __future__ import annotations

import argparse
import os
import sys

from agents import Runner

from .config import repo_root
from .orchestrator import build_orchestrator
from .tools.build_indexes import build_indexes


def main() -> None:
    parser = argparse.ArgumentParser(description="Runtime de agentes SGC")
    parser.add_argument("--task", required=True, help="Tarea a ejecutar por el orquestador")
    args = parser.parse_args()

    if not os.getenv("OPENAI_API_KEY"):
        print("ERROR: OPENAI_API_KEY no configurada", file=sys.stderr)
        sys.exit(2)

    agent = build_orchestrator()
    result = Runner.run_sync(agent, args.task)

    summary = build_indexes(repo_root())

    print(result.final_output)
    print(f"\n[control] Indices regenerados automaticamente. {summary.as_text()}")


if __name__ == "__main__":
    main()
