"""
Unit tests for NEXUS-ANALYTICS Typer CLI interface.
"""
from typer.testing import CliRunner

from nexus.cli.main import app

runner = CliRunner()


def test_cli_help() -> None:
    """Verify that root CLI --help renders correctly."""
    result = runner.invoke(app, ["--help"])
    assert result.exit_code == 0
    assert "NEXUS-ANALYTICS" in result.output
    assert "run" in result.output
    assert "rfm" in result.output
    assert "churn" in result.output
    assert "uplift" in result.output
    assert "kpis" in result.output


def test_cli_kpis() -> None:
    """Verify that 'kpis' command executes and displays metrics table."""
    result = runner.invoke(app, ["kpis", "--customers", "25"])
    assert result.exit_code == 0
    assert "Warehouse Executive KPIs" in result.output
    assert "Total Customers" in result.output


def test_cli_rfm() -> None:
    """Verify that 'rfm' command executes and outputs segmentation summary."""
    result = runner.invoke(app, ["rfm", "--customers", "30"])
    assert result.exit_code == 0
    assert "Algorithmic RFM Customer Segmentation Matrix" in result.output


def test_cli_churn() -> None:
    """Verify that 'churn' command executes and outputs risk tier distribution."""
    result = runner.invoke(app, ["churn", "--customers", "30"])
    assert result.exit_code == 0
    assert "Customer Churn Risk Tier Distribution" in result.output


def test_cli_uplift() -> None:
    """Verify that 'uplift' command outputs causal ROI comparison."""
    result = runner.invoke(app, ["uplift", "--customers", "30"])
    assert result.exit_code == 0
    assert "Causal Uplift Campaign Simulation" in result.output
    assert "Cost Efficiency Gain" in result.output


def test_cli_run_full_pipeline() -> None:
    """Verify that master 'run' command executes end-to-end pipeline."""
    result = runner.invoke(app, ["run", "--customers", "25", "--transactions", "60", "--campaigns", "40", "--seed", "99"])
    assert result.exit_code == 0
    assert "Master Pipeline Execution" in result.output
    assert "Executive Pipeline Execution Summary" in result.output
    assert "Pipeline execution completed successfully" in result.output
