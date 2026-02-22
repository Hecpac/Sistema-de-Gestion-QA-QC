from __future__ import annotations

import argparse
import os
import sys

from agents import Runner

from .config import repo_root
from .multiagent import run_multiagent_task_sync
from .orchestrator import build_orchestrator
from .tools.build_indexes import build_indexes


def main() -> None:
    parser = argparse.ArgumentParser(description="Runtime de agentes SGC")
    parser.add_argument("--task", required=True, help="Tarea a ejecutar por el orquestador")
    parser.add_argument(
        "--mode",
        choices=["multi", "orchestrator"],
        default=os.getenv("SGC_AGENT_MODE", "multi"),
        help="Ejecucion multiagente (paralela) o via orquestador con handoffs.",
    )
    parser.add_argument(
        "--max-turns",
        type=int,
        default=int(os.getenv("SGC_AGENT_MAX_TURNS", "10")),
        help="Maximo de turnos por agente (cuando aplique).",
    )
    parser.add_argument(
        "--no-llm",
        action="store_true",
        help="Ejecuta solo el pipeline deterministico (sin llamadas LLM).",
    )
    args = parser.parse_args()

    if args.mode in ("multi", "orchestrator") and not args.no_llm and not os.getenv("OPENAI_API_KEY"):
        print("ERROR: OPENAI_API_KEY no configurada (o usa --no-llm).", file=sys.stderr)
        sys.exit(2)

    if args.mode == "multi":
        result = run_multiagent_task_sync(
            args.task,
            include_llm=not args.no_llm,
            max_turns=args.max_turns,
        )
        print(result.render_text())
        print(f"\n[control] Indices regenerados automaticamente. {result.compliance.indexes.as_text()}")
        return

    agent = build_orchestrator()
    result = Runner.run_sync(agent, args.task, max_turns=args.max_turns)

    summary = build_indexes(repo_root())

    print(result.final_output)
    print(f"\n[control] Indices regenerados automaticamente. {summary.as_text()}")


if __name__ == "__main__":
    main()
