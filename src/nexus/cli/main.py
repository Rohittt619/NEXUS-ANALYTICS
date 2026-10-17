"""
NEXUS-ANALYTICS Command-Line Interface (CLI).

Automates execution of the customer intelligence pipeline,
RFM audits, churn risk reviews, and campaign ROI simulations.
"""
from __future__ import annotations

import typer
from rich.console import Console
from rich.table import Table
from rich.panel import Panel

from nexus.orchestrator.pipeline import CustomerIntelligencePipeline

app = typer.Typer(
    name="nexus",
    help="NEXUS-ANALYTICS: Enterprise Customer Intelligence & Campaign ROI Engine CLI",
    add_completion=False
)
console = Console()


@app.command()
def run(
    customers: int = typer.Option(200, "--customers", "-c", help="Customer population sample size"),
    transactions: int = typer.Option(1000, "--transactions", "-t", help="Transaction count"),
    campaigns: int = typer.Option(600, "--campaigns", "-m", help="Marketing touchpoints count"),
    seed: int = typer.Option(42, "--seed", "-s", help="Random seed for reproducibility")
) -> None:
    """Execute the full end-to-end Customer Intelligence Pipeline."""
    console.print(
        Panel(
            "[bold cyan]NEXUS-ANALYTICS: Master Pipeline Execution[/bold cyan]\n"
            "[dim]Executing DuckDB star-schema ETL, RFM, Churn ML, Uplift & CLV models...[/dim]",
            expand=False
        )
    )

    pipeline = CustomerIntelligencePipeline(seed=seed)
    res = pipeline.run_full_pipeline(
        num_customers=customers,
        num_transactions=transactions,
        num_campaigns=campaigns
    )
    pipeline.close()

    # Render Executive Table
    table = Table(title="Executive Pipeline Execution Summary", header_style="bold magenta")
    table.add_column("Metric", style="cyan")
    table.add_column("Value", style="bold green")

    table.add_row("Pipeline Run ID", res.run_id[:13] + "...")
    table.add_row("Total Customers Evaluated", str(res.kpis["total_customers"]))
    table.add_row("Total Gross Revenue", f"${res.kpis['total_gross_revenue']:,.2f}")
    table.add_row("Average Order Value (AOV)", f"${res.kpis['average_order_value']:,.2f}")
    table.add_row("Repeat Purchase Rate", f"{res.kpis['repeat_purchase_rate_pct']}%")
    table.add_row("Projected 3-Yr CLV Portfolio", f"${res.clv_result.enterprise_projected_portfolio_value:,.2f}")
    table.add_row("Execution Latency", f"{res.execution_duration_ms} ms")
    table.add_row("SHA-256 Audit Digest", res.sha256_audit_hash[:24] + "...")

    console.print(table)
    console.print("[bold green]Pipeline execution completed successfully![/bold green]\n")


@app.command()
def rfm(
    customers: int = typer.Option(200, "--customers", "-c", help="Customer population sample size")
) -> None:
    """Run algorithmic RFM customer segmentation analysis."""
    pipeline = CustomerIntelligencePipeline(seed=42)
    res = pipeline.run_full_pipeline(num_customers=customers, num_transactions=customers * 5, num_campaigns=customers * 3)
    pipeline.close()

    table = Table(title="Algorithmic RFM Customer Segmentation Matrix", header_style="bold cyan")
    table.add_column("Segment Tier", style="bold yellow")
    table.add_column("Customer Count", style="cyan")
    table.add_column("Customer Share", style="white")
    table.add_column("Total Revenue", style="green")
    table.add_column("Revenue Share", style="bold green")

    for _, row in res.rfm_result.segment_summary.iterrows():
        table.add_row(
            row["segment"],
            str(row["customer_count"]),
            f"{row['customer_share_pct']}%",
            f"${row['total_revenue']:,.2f}",
            f"{row['revenue_share_pct']}%"
        )

    console.print(table)


@app.command()
def churn(
    customers: int = typer.Option(200, "--customers", "-c", help="Customer population sample size")
) -> None:
    """Audit churn probability distributions and behavioral risk drivers."""
    pipeline = CustomerIntelligencePipeline(seed=42)
    res = pipeline.run_full_pipeline(num_customers=customers, num_transactions=customers * 5, num_campaigns=customers * 3)
    pipeline.close()

    table = Table(title="Customer Churn Risk Tier Distribution", header_style="bold red")
    table.add_column("Risk Tier", style="bold yellow")
    table.add_column("Customer Count", style="cyan")
    table.add_column("Customer Share", style="white")
    table.add_column("Avg Churn Prob", style="red")
    table.add_column("Spend At Risk", style="bold red")

    for _, row in res.churn_result.risk_tier_summary.iterrows():
        table.add_row(
            row["risk_tier"],
            str(row["customer_count"]),
            f"{row['customer_share_pct']}%",
            f"{row['avg_churn_prob']:.1%}",
            f"${row['total_spend_at_risk']:,.2f}"
        )

    console.print(table)


@app.command()
def uplift(
    customers: int = typer.Option(200, "--customers", "-c", help="Customer population sample size")
) -> None:
    """Evaluate causal uplift archetypes and campaign ROI simulation."""
    pipeline = CustomerIntelligencePipeline(seed=42)
    res = pipeline.run_full_pipeline(num_customers=customers, num_transactions=customers * 5, num_campaigns=customers * 3)
    pipeline.close()

    sim = res.uplift_result.simulated_roi_targeted_vs_blast

    table = Table(title="Causal Uplift Campaign Simulation (Targeted vs. Blast)", header_style="bold green")
    table.add_column("Strategy", style="bold cyan")
    table.add_column("Audience Size", style="white")
    table.add_column("Cost (USD)", style="yellow")
    table.add_column("Net Profit (USD)", style="bold green")
    table.add_column("ROI %", style="bold magenta")

    t = sim["targeted_strategy"]
    b = sim["blast_strategy"]

    table.add_row("Targeted (Persuadables Only)", str(t["customers_contacted"]), f"${t['campaign_cost_usd']:,.2f}", f"${t['net_profit_usd']:,.2f}", f"+{t['roi_percentage']}%")
    table.add_row("Blast (Entire Population)", str(b["customers_contacted"]), f"${b['campaign_cost_usd']:,.2f}", f"${b['net_profit_usd']:,.2f}", f"+{b['roi_percentage']}%")

    console.print(table)
    console.print(f"[bold cyan]Cost Efficiency Gain:[/bold cyan] Targeted campaign is [bold green]{sim['efficiency_gain_factor']}x[/bold green] more cost-effective!\n")


@app.command()
def kpis(
    customers: int = typer.Option(200, "--customers", "-c", help="Customer population sample size")
) -> None:
    """Display quick executive KPIs directly from DuckDB star-schema."""
    pipeline = CustomerIntelligencePipeline(seed=42)
    c, t, p = pipeline.generator.generate_dataset(num_customers=customers, num_transactions=customers * 5, num_campaign_touchpoints=customers * 3)
    pipeline.warehouse.load_dataframes(c, t, p)
    kpis = pipeline.warehouse.get_kpis()
    pipeline.close()

    table = Table(title="Warehouse Executive KPIs", header_style="bold blue")
    table.add_column("KPI", style="cyan")
    table.add_column("Metric Value", style="bold green")

    table.add_row("Total Customers", str(kpis["total_customers"]))
    table.add_row("Total Transactions", str(kpis["total_transactions"]))
    table.add_row("Gross Revenue", f"${kpis['total_gross_revenue']:,.2f}")
    table.add_row("Average Order Value", f"${kpis['average_order_value']:,.2f}")
    table.add_row("Repeat Purchase Rate", f"{kpis['repeat_purchase_rate_pct']}%")
    table.add_row("Total Marketing Spend", f"${kpis['total_campaign_spend']:,.2f}")

    console.print(table)


def main() -> None:
    """CLI Main Entry Point."""
    app()


if __name__ == "__main__":
    main()
