"""Tests para sgc-init — scaffolding de proyectos SGC."""
from __future__ import annotations

from pathlib import Path

import yaml
import pytest

from sgc_agents.tools.scaffold import DOC_DIRS, main, scaffold


# ===================================================================
# scaffold()
# ===================================================================


class TestScaffold:
    def test_creates_all_doc_dirs(self, tmp_path):
        project = tmp_path / "my-sgc"
        scaffold(project, skip_git=True)

        for d in DOC_DIRS:
            assert (project / d).is_dir(), f"Missing dir: {d}"

    def test_creates_core_files(self, tmp_path):
        project = tmp_path / "my-sgc"
        scaffold(project, skip_git=True)

        expected_files = [
            ".gitignore",
            ".env.example",
            "README.md",
            "AGENTS.md",
            "docs/_control/lmd.yml",
            "docs/_control/matriz_registros.yml",
        ]
        for f in expected_files:
            assert (project / f).is_file(), f"Missing file: {f}"

    def test_readme_contains_company_name(self, tmp_path):
        project = tmp_path / "my-sgc"
        scaffold(project, company_name="Acme Corp", skip_git=True)

        readme = (project / "README.md").read_text(encoding="utf-8")
        assert "Acme Corp" in readme

    def test_agents_md_contains_company_name(self, tmp_path):
        project = tmp_path / "my-sgc"
        scaffold(project, company_name="Acme Corp", skip_git=True)

        agents = (project / "AGENTS.md").read_text(encoding="utf-8")
        assert "Acme Corp" in agents

    def test_lmd_is_valid_yaml(self, tmp_path):
        project = tmp_path / "my-sgc"
        scaffold(project, skip_git=True)

        data = yaml.safe_load(
            (project / "docs/_control/lmd.yml").read_text(encoding="utf-8")
        )
        assert isinstance(data, dict)
        assert "documentos" in data
        assert data["documentos"] == []

    def test_matrix_is_valid_yaml(self, tmp_path):
        project = tmp_path / "my-sgc"
        scaffold(project, skip_git=True)

        data = yaml.safe_load(
            (project / "docs/_control/matriz_registros.yml").read_text(encoding="utf-8")
        )
        assert isinstance(data, dict)
        assert "registros" in data
        assert data["registros"] == []

    def test_copies_templates_from_source(self, tmp_path):
        # Create fake templates source
        src = tmp_path / "templates_src"
        src.mkdir()
        (src / "TEMPLATE_Procedimiento.md").write_text("# PR template", encoding="utf-8")
        (src / "TEMPLATE_Formato.md").write_text("# FOR template", encoding="utf-8")
        (src / "NOT_A_TEMPLATE.md").write_text("ignored", encoding="utf-8")

        project = tmp_path / "my-sgc"
        result = scaffold(project, skip_git=True, templates_source=src)

        assert result["templates_copied"] == 2
        assert (project / "templates/TEMPLATE_Procedimiento.md").is_file()
        assert (project / "templates/TEMPLATE_Formato.md").is_file()
        assert not (project / "templates/NOT_A_TEMPLATE.md").exists()

    def test_no_templates_when_source_nonexistent(self, tmp_path):
        """Passing a nonexistent templates_source falls back to package dir."""
        project = tmp_path / "my-sgc"
        result = scaffold(
            project,
            skip_git=True,
            templates_source=tmp_path / "nonexistent",
        )
        # Falls back to package templates (which exist in dev)
        assert isinstance(result["templates_copied"], int)
        assert result["templates_copied"] >= 0

    def test_returns_summary_dict(self, tmp_path):
        project = tmp_path / "my-sgc"
        result = scaffold(project, company_name="Test Co", skip_git=True)

        assert result["project_path"] == str(project)
        assert result["company_name"] == "Test Co"
        assert result["dirs_created"] == len(DOC_DIRS)
        assert result["files_created"] == 6
        assert result["git_initialized"] is False

    def test_rejects_non_empty_directory(self, tmp_path):
        project = tmp_path / "my-sgc"
        project.mkdir()
        (project / "existing_file.txt").write_text("hello", encoding="utf-8")

        with pytest.raises(FileExistsError, match="ya existe"):
            scaffold(project)

    def test_allows_empty_existing_directory(self, tmp_path):
        project = tmp_path / "my-sgc"
        project.mkdir()
        # Empty dir should work
        result = scaffold(project, skip_git=True)
        assert result["dirs_created"] == len(DOC_DIRS)

    def test_creates_parent_dirs(self, tmp_path):
        project = tmp_path / "deep" / "nested" / "my-sgc"
        result = scaffold(project, skip_git=True)
        assert (project / "README.md").is_file()

    def test_skip_git(self, tmp_path):
        project = tmp_path / "my-sgc"
        result = scaffold(project, skip_git=True)
        assert result["git_initialized"] is False
        assert not (project / ".git").exists()

    def test_git_init(self, tmp_path):
        project = tmp_path / "my-sgc"
        result = scaffold(project, skip_git=False)
        assert result["git_initialized"] is True
        assert (project / ".git").exists()

    def test_gitignore_excludes_env(self, tmp_path):
        project = tmp_path / "my-sgc"
        scaffold(project, skip_git=True)

        content = (project / ".gitignore").read_text(encoding="utf-8")
        assert ".env" in content
        assert "__pycache__" in content

    def test_env_example_has_required_vars(self, tmp_path):
        project = tmp_path / "my-sgc"
        scaffold(project, skip_git=True)

        content = (project / ".env.example").read_text(encoding="utf-8")
        assert "OPENAI_API_KEY" in content
        assert "SGC_REPO_ROOT" in content

    def test_default_company_name(self, tmp_path):
        project = tmp_path / "my-sgc"
        result = scaffold(project, skip_git=True)
        assert result["company_name"] == "Mi Empresa"

        readme = (project / "README.md").read_text(encoding="utf-8")
        assert "Mi Empresa" in readme


# ===================================================================
# main() CLI
# ===================================================================


class TestMainCLI:
    def test_cli_creates_project(self, tmp_path, capsys):
        project = tmp_path / "cli-test"
        rc = main([str(project), "--skip-git"])
        assert rc == 0

        captured = capsys.readouterr()
        assert "SGC proyecto creado" in captured.out
        assert "Siguientes pasos" in captured.out

    def test_cli_with_company_name(self, tmp_path, capsys):
        project = tmp_path / "cli-test"
        rc = main([str(project), "--company-name", "ACME", "--skip-git"])
        assert rc == 0

        captured = capsys.readouterr()
        assert "ACME" in captured.out

    def test_cli_fails_on_non_empty(self, tmp_path, capsys):
        project = tmp_path / "cli-test"
        project.mkdir()
        (project / "blocker.txt").write_text("x", encoding="utf-8")

        rc = main([str(project), "--skip-git"])
        assert rc == 1

        captured = capsys.readouterr()
        assert "Error" in captured.err

    def test_cli_with_templates_source(self, tmp_path, capsys):
        src = tmp_path / "tmpl"
        src.mkdir()
        (src / "TEMPLATE_Test.md").write_text("# test", encoding="utf-8")

        project = tmp_path / "cli-test"
        rc = main([
            str(project),
            "--skip-git",
            "--templates-source", str(src),
        ])
        assert rc == 0
        assert (project / "templates/TEMPLATE_Test.md").is_file()

    def test_cli_prints_template_count(self, tmp_path, capsys):
        src = tmp_path / "tmpl"
        src.mkdir()
        (src / "TEMPLATE_A.md").write_text("a", encoding="utf-8")
        (src / "TEMPLATE_B.md").write_text("b", encoding="utf-8")

        project = tmp_path / "cli-test"
        main([str(project), "--skip-git", "--templates-source", str(src)])

        captured = capsys.readouterr()
        assert "Templates:   2" in captured.out


# ===================================================================
# DOC_DIRS constant
# ===================================================================


class TestDocDirs:
    def test_doc_dirs_is_not_empty(self):
        assert len(DOC_DIRS) > 0

    def test_all_dirs_start_with_docs_or_known_prefix(self):
        valid_prefixes = ("docs/", "templates", "playbooks")
        for d in DOC_DIRS:
            assert any(d.startswith(p) for p in valid_prefixes), f"Unexpected dir: {d}"

    def test_control_dir_included(self):
        assert any("_control" in d for d in DOC_DIRS)

    def test_registros_subdirs_included(self):
        reg_dirs = [d for d in DOC_DIRS if "06_registros" in d]
        assert len(reg_dirs) >= 5  # at least several subcategories
