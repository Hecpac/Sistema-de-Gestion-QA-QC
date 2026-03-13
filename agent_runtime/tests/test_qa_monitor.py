"""Tests para qa_monitor — pipeline deterministico de compliance."""
from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path

import yaml
import pytest

from sgc_agents.tools import qa_monitor


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

_CLEAN_CHECK_YAML = yaml.safe_dump(
    {"skill": "stub", "valido": True, "hallazgos": []},
    sort_keys=False,
)

_DIRTY_CHECK_YAML = yaml.safe_dump(
    {
        "skill": "stub",
        "valido": False,
        "hallazgos": [{"codigo": "PR-SGC-01", "error": "Contiene TODO"}],
    },
    sort_keys=False,
)


def _stub_checks(monkeypatch, *, dirty_indices: set[int] | None = None):
    """Replace CHECKS list with stubs. Indices in *dirty_indices* return 1 hallazgo."""
    dirty = dirty_indices or set()
    stubs = []
    for i in range(len(qa_monitor.CHECKS)):
        payload = _DIRTY_CHECK_YAML if i in dirty else _CLEAN_CHECK_YAML
        stubs.append(lambda _y=payload: _y)
    monkeypatch.setattr(qa_monitor, "CHECKS", stubs)
    monkeypatch.setattr(
        qa_monitor,
        "generar_reporte_qa_compliance",
        lambda *a, **kw: "OK: stub report",
    )


def _all_clean(monkeypatch):
    _stub_checks(monkeypatch)


def _one_dirty(monkeypatch, *, index: int = 0):
    _stub_checks(monkeypatch, dirty_indices={index})


def _multi_dirty(monkeypatch, *, dirty_indices: list[int]):
    _stub_checks(monkeypatch, dirty_indices=set(dirty_indices))


# ===================================================================
# run_checks
# ===================================================================


class TestRunChecks:
    def test_zero_hallazgos(self, monkeypatch):
        _all_clean(monkeypatch)
        total, results = qa_monitor.run_checks()
        assert total == 0
        assert len(results) == 8
        for r in results:
            assert r["valido"] is True

    def test_one_hallazgo(self, monkeypatch):
        _one_dirty(monkeypatch, index=0)
        total, results = qa_monitor.run_checks()
        assert total == 1

    def test_multiple_hallazgos_across_checks(self, monkeypatch):
        _multi_dirty(monkeypatch, dirty_indices=[0, 2, 5])
        total, _ = qa_monitor.run_checks()
        assert total == 3

    def test_all_dirty(self, monkeypatch):
        _stub_checks(monkeypatch, dirty_indices=set(range(8)))
        total, _ = qa_monitor.run_checks()
        assert total == 8

    def test_returns_parsed_dicts(self, monkeypatch):
        _all_clean(monkeypatch)
        _, results = qa_monitor.run_checks()
        for r in results:
            assert isinstance(r, dict)
            assert "hallazgos" in r

    def test_handles_empty_hallazgos_key(self, monkeypatch):
        """A check that returns hallazgos: null should count as 0."""
        null_yaml = yaml.safe_dump(
            {"skill": "stub", "valido": True, "hallazgos": None},
            sort_keys=False,
        )
        monkeypatch.setattr(
            qa_monitor, "CHECKS", [lambda _y=null_yaml: _y] * 8
        )
        total, _ = qa_monitor.run_checks()
        assert total == 0


# ===================================================================
# append_history
# ===================================================================


class TestAppendHistory:
    def test_creates_new_file(self, tmp_path):
        hist = tmp_path / "history.yml"
        now = datetime(2026, 3, 2, 12, 0, 0, tzinfo=timezone.utc)
        payload = qa_monitor.append_history(hist, 0, now=now, source="test")

        assert hist.exists()
        runs = payload["runs"]
        assert len(runs) == 1
        assert runs[0]["hallazgos"] == 0
        assert runs[0]["source"] == "test"
        assert runs[0]["date"] == "2026-03-02"

    def test_appends_to_existing(self, tmp_path):
        hist = tmp_path / "history.yml"
        t1 = datetime(2026, 3, 1, 10, 0, 0, tzinfo=timezone.utc)
        t2 = datetime(2026, 3, 2, 10, 0, 0, tzinfo=timezone.utc)

        qa_monitor.append_history(hist, 0, now=t1, source="test")
        payload = qa_monitor.append_history(hist, 3, now=t2, source="test")

        runs = payload["runs"]
        assert len(runs) == 2
        assert runs[0]["hallazgos"] == 0
        assert runs[1]["hallazgos"] == 3

    def test_sorted_by_timestamp(self, tmp_path):
        hist = tmp_path / "history.yml"
        t_late = datetime(2026, 3, 5, 10, 0, 0, tzinfo=timezone.utc)
        t_early = datetime(2026, 3, 1, 10, 0, 0, tzinfo=timezone.utc)

        qa_monitor.append_history(hist, 0, now=t_late, source="test")
        payload = qa_monitor.append_history(hist, 1, now=t_early, source="test")

        runs = payload["runs"]
        assert runs[0]["date"] == "2026-03-01"
        assert runs[1]["date"] == "2026-03-05"

    def test_max_runs_rotation(self, tmp_path):
        hist = tmp_path / "history.yml"
        for i in range(65):
            day = 1 + (i // 24)
            hour = i % 24
            t = datetime(2026, 1, day, hour, 0, 0, tzinfo=timezone.utc)
            payload = qa_monitor.append_history(
                hist, i, now=t, source="test", max_runs=60
            )

        runs = payload["runs"]
        assert len(runs) == 60
        # The oldest 5 should have been trimmed
        assert runs[0]["hallazgos"] == 5

    def test_handles_corrupt_yaml(self, tmp_path):
        hist = tmp_path / "history.yml"
        hist.write_text("not: valid: yaml: [[[", encoding="utf-8")

        payload = qa_monitor.append_history(hist, 0, source="test")
        assert len(payload["runs"]) == 1

    def test_handles_non_dict_payload(self, tmp_path):
        hist = tmp_path / "history.yml"
        hist.write_text("- just a list\n- item\n", encoding="utf-8")

        payload = qa_monitor.append_history(hist, 2, source="test")
        assert len(payload["runs"]) == 1
        assert payload["runs"][0]["hallazgos"] == 2

    def test_handles_runs_not_list(self, tmp_path):
        hist = tmp_path / "history.yml"
        hist.write_text("runs: 'not a list'\n", encoding="utf-8")

        payload = qa_monitor.append_history(hist, 0, source="test")
        assert len(payload["runs"]) == 1

    def test_creates_parent_dirs(self, tmp_path):
        hist = tmp_path / "deep" / "nested" / "history.yml"
        qa_monitor.append_history(hist, 0, source="test")
        assert hist.exists()

    def test_file_has_header(self, tmp_path):
        hist = tmp_path / "history.yml"
        qa_monitor.append_history(hist, 0, source="test")

        content = hist.read_text(encoding="utf-8")
        assert content.startswith("# Historial de monitor QA del SGC")
        assert "No editar manualmente" in content

    def test_github_actions_source(self, tmp_path, monkeypatch):
        hist = tmp_path / "history.yml"
        monkeypatch.setenv("GITHUB_ACTIONS", "true")
        payload = qa_monitor.append_history(hist, 0, source=None)
        assert payload["runs"][0]["source"] == "github-actions"

    def test_local_source_default(self, tmp_path, monkeypatch):
        hist = tmp_path / "history.yml"
        monkeypatch.delenv("GITHUB_ACTIONS", raising=False)
        payload = qa_monitor.append_history(hist, 0, source=None)
        assert payload["runs"][0]["source"] == "local"

    def test_idempotent_content_format(self, tmp_path):
        """Running twice produces valid parseable YAML."""
        hist = tmp_path / "history.yml"
        qa_monitor.append_history(hist, 0, source="test")
        qa_monitor.append_history(hist, 1, source="test")

        content = hist.read_text(encoding="utf-8")
        lines = [l for l in content.splitlines() if not l.startswith("#")]
        data = yaml.safe_load("\n".join(lines))
        assert isinstance(data, dict)
        assert len(data["runs"]) == 2

    def test_filters_non_dict_runs(self, tmp_path):
        """Existing runs that aren't dicts get filtered out."""
        hist = tmp_path / "history.yml"
        hist.write_text(
            yaml.safe_dump({
                "runs": [
                    "bad",
                    42,
                    None,
                    {
                        "timestamp": "2026-01-01T00:00:00Z",
                        "date": "2026-01-01",
                        "hallazgos": 0,
                        "source": "test",
                    },
                ]
            }),
            encoding="utf-8",
        )
        payload = qa_monitor.append_history(hist, 1, source="test")
        assert len(payload["runs"]) == 2
        for r in payload["runs"]:
            assert isinstance(r, dict)

    def test_hallazgos_stored_as_int(self, tmp_path):
        hist = tmp_path / "history.yml"
        qa_monitor.append_history(hist, 7, source="test")
        payload = yaml.safe_load(
            "\n".join(
                l for l in hist.read_text("utf-8").splitlines()
                if not l.startswith("#")
            )
        )
        assert payload["runs"][0]["hallazgos"] == 7
        assert isinstance(payload["runs"][0]["hallazgos"], int)


# ===================================================================
# run_pipeline
# ===================================================================


class TestRunPipeline:
    def test_returns_zero_on_clean(self, monkeypatch, tmp_path):
        _all_clean(monkeypatch)
        hist = tmp_path / "history.yml"
        rc = qa_monitor.run_pipeline(history_path=hist, generate_report=False)
        assert rc == 0

    def test_returns_one_on_hallazgo(self, monkeypatch, tmp_path):
        _one_dirty(monkeypatch, index=0)
        hist = tmp_path / "history.yml"
        rc = qa_monitor.run_pipeline(history_path=hist, generate_report=False)
        assert rc == 1

    def test_writes_history(self, monkeypatch, tmp_path):
        _all_clean(monkeypatch)
        hist = tmp_path / "history.yml"
        qa_monitor.run_pipeline(history_path=hist, generate_report=False)
        assert hist.exists()
        data = yaml.safe_load(
            "\n".join(
                l
                for l in hist.read_text(encoding="utf-8").splitlines()
                if not l.startswith("#")
            )
        )
        assert len(data["runs"]) == 1

    def test_no_history_when_path_none(self, monkeypatch):
        _all_clean(monkeypatch)
        rc = qa_monitor.run_pipeline(history_path=None, generate_report=False)
        assert rc == 0

    def test_calls_report_when_enabled(self, monkeypatch, tmp_path, capsys):
        _all_clean(monkeypatch)
        qa_monitor.run_pipeline(
            history_path=tmp_path / "h.yml", generate_report=True
        )
        captured = capsys.readouterr()
        assert "OK: stub report" in captured.out

    def test_skips_report_when_disabled(self, monkeypatch, tmp_path, capsys):
        _all_clean(monkeypatch)
        qa_monitor.run_pipeline(
            history_path=tmp_path / "h.yml", generate_report=False
        )
        captured = capsys.readouterr()
        assert "stub report" not in captured.out

    def test_prints_hallazgos_count(self, monkeypatch, tmp_path, capsys):
        _multi_dirty(monkeypatch, dirty_indices=[1, 3])
        qa_monitor.run_pipeline(
            history_path=tmp_path / "h.yml", generate_report=False
        )
        captured = capsys.readouterr()
        assert "hallazgos_totales=2" in captured.out

    def test_history_records_hallazgo_count(self, monkeypatch, tmp_path):
        _multi_dirty(monkeypatch, dirty_indices=[0, 1, 2])
        hist = tmp_path / "h.yml"
        qa_monitor.run_pipeline(history_path=hist, generate_report=False)
        data = yaml.safe_load(
            "\n".join(
                l for l in hist.read_text("utf-8").splitlines()
                if not l.startswith("#")
            )
        )
        assert data["runs"][0]["hallazgos"] == 3


# ===================================================================
# main (CLI)
# ===================================================================


class TestMain:
    def test_cli_clean_exit_zero(self, monkeypatch, tmp_path):
        _all_clean(monkeypatch)
        hist = tmp_path / "history.yml"
        rc = qa_monitor.main([
            "--repo-root", str(tmp_path),
            "--history-file", str(hist),
            "--no-report",
        ])
        assert rc == 0

    def test_cli_dirty_exit_one(self, monkeypatch, tmp_path):
        _one_dirty(monkeypatch)
        hist = tmp_path / "history.yml"
        rc = qa_monitor.main([
            "--repo-root", str(tmp_path),
            "--history-file", str(hist),
            "--no-report",
        ])
        assert rc == 1

    def test_cli_sets_sgc_repo_root_env(self, monkeypatch, tmp_path):
        _all_clean(monkeypatch)
        hist = tmp_path / "history.yml"
        qa_monitor.main([
            "--repo-root", str(tmp_path),
            "--history-file", str(hist),
            "--no-report",
        ])
        import os
        assert os.environ["SGC_REPO_ROOT"] == str(tmp_path)

    def test_cli_relative_history(self, monkeypatch, tmp_path):
        _all_clean(monkeypatch)
        (tmp_path / "docs" / "_control").mkdir(parents=True)

        rc = qa_monitor.main([
            "--repo-root", str(tmp_path),
            "--history-file", "docs/_control/qa_monitor_history.yml",
            "--no-report",
        ])
        assert rc == 0
        assert (tmp_path / "docs/_control/qa_monitor_history.yml").exists()

    def test_cli_defaults_from_env(self, monkeypatch, tmp_path):
        _all_clean(monkeypatch)
        hist = tmp_path / "h.yml"

        monkeypatch.setenv("SGC_REPO_ROOT", str(tmp_path))
        monkeypatch.setenv("HISTORY_FILE", str(hist))

        rc = qa_monitor.main(["--no-report"])
        assert rc == 0
        assert hist.exists()


# ===================================================================
# Constants & module structure
# ===================================================================


class TestModuleStructure:
    def test_checks_list_has_8_entries(self):
        assert len(qa_monitor.CHECKS) == 8

    def test_max_history_runs_is_60(self):
        assert qa_monitor.MAX_HISTORY_RUNS == 60

    def test_header_mentions_autogenerado(self):
        assert "autogenerado" in qa_monitor.HISTORY_HEADER

    def test_all_checks_are_callable(self):
        for fn in qa_monitor.CHECKS:
            assert callable(fn)
