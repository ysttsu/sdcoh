# tests/test_cli.py
import json
from pathlib import Path

from click.testing import CliRunner

from sdcoh.cli import cli


def test_cli_init(tmp_path: Path) -> None:
    runner = CliRunner()
    result = runner.invoke(cli, ["init", "--name", "Test Novel"], catch_exceptions=False)
    assert result.exit_code == 0
    assert (Path.cwd() / "sdcoh.yml").exists() or "Created" in result.output


def test_cli_scan(sample_project: Path) -> None:
    runner = CliRunner()
    with runner.isolated_filesystem(temp_dir=sample_project) as td:
        # Copy files (CliRunner changes cwd)
        pass
    # Use mix_stderr=False and invoke with obj
    result = runner.invoke(
        cli, ["scan", "--path", str(sample_project)], catch_exceptions=False
    )
    assert result.exit_code == 0
    assert "nodes" in result.output.lower() or "graph" in result.output.lower()
    assert (sample_project / ".sdcoh" / "graph.json").exists()


def test_cli_impact(sample_project: Path) -> None:
    # First scan
    runner = CliRunner()
    runner.invoke(cli, ["scan", "--path", str(sample_project)], catch_exceptions=False)
    result = runner.invoke(
        cli,
        ["impact", "design/characters.md", "--path", str(sample_project)],
        catch_exceptions=False,
    )
    assert result.exit_code == 0
    assert "beat-sheet" in result.output


def test_cli_status(sample_project: Path) -> None:
    runner = CliRunner()
    runner.invoke(cli, ["scan", "--path", str(sample_project)], catch_exceptions=False)
    result = runner.invoke(
        cli, ["status", "--path", str(sample_project)], catch_exceptions=False
    )
    assert result.exit_code == 0


def test_cli_validate(sample_project: Path) -> None:
    runner = CliRunner()
    runner.invoke(cli, ["scan", "--path", str(sample_project)], catch_exceptions=False)
    result = runner.invoke(
        cli, ["validate", "--path", str(sample_project)], catch_exceptions=False
    )
    assert result.exit_code == 0


def test_cli_graph(sample_project: Path) -> None:
    runner = CliRunner()
    runner.invoke(cli, ["scan", "--path", str(sample_project)], catch_exceptions=False)
    result = runner.invoke(
        cli, ["graph", "--path", str(sample_project)], catch_exceptions=False
    )
    assert result.exit_code == 0
    assert "design:characters" in result.output
