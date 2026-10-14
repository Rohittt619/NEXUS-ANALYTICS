"""
NEXUS-ANALYTICS Executive Decision Cockpit.

Streamlit web dashboard providing real-time visibility into customer intelligence:
1. Executive KPIs & Cohort Retention Matrices
2. Algorithmic RFM Customer Segmentation
3. Churn Risk Probability & Behavioral Attribution
4. Causal Uplift & Campaign ROI Simulator
5. 3-Year Customer Lifetime Value (CLV) Projections
6. Unified Customer 360 Explorer
7. Cryptographic SHA-256 Audit Report Exporter
"""
from __future__ import annotations

import json
import os
import sys
import streamlit as st
import pandas as pd

# Add src to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))

from nexus.ui.theme import inject_glass_theme
from nexus.orchestrator.pipeline import CustomerIntelligencePipeline, PipelineExecutionResult

# Page Config
st.set_page_config(
    page_title="NEXUS-ANALYTICS Executive Cockpit",
    page_icon="💎",
    layout="wide",
    initial_sidebar_state="expanded"
)

inject_glass_theme()

# Header Banner
st.markdown('<div class="nexus-title">💎 NEXUS-ANALYTICS</div>', unsafe_allow_html=True)
st.markdown(
    '<p style="color: #94A3B8; font-size: 1.1rem; font-weight: 500;">'
    'Enterprise Customer Intelligence, Churn Causality, CLV & Campaign ROI Optimization Cockpit'
    '</p>',
    unsafe_allow_html=True
)
st.markdown("---")

# Session State for Pipeline Cache
if "pipeline_result" not in st.session_state:
    st.session_state.pipeline_result = None

# Sidebar Controls
st.sidebar.markdown("### ⚙️ Pipeline Controls")
sample_size = st.sidebar.slider("Customer Population Size:", min_value=100, max_value=1000, value=300, step=50)

if st.sidebar.button("🚀 Run Full Analytics Pipeline", type="primary", use_container_width=True):
    with st.spinner("Executing DuckDB Star-Schema ETL, RFM, Churn ML & Causal Uplift..."):
        pipeline = CustomerIntelligencePipeline(seed=42)
        res = pipeline.run_full_pipeline(
            num_customers=sample_size,
            num_transactions=sample_size * 5,
            num_campaigns=sample_size * 3
        )
        st.session_state.pipeline_result = res
        pipeline.close()
        st.sidebar.success("✅ Analytics Pipeline Executed Successfully!")

# Auto-run with small sample if no result loaded yet
if st.session_state.pipeline_result is None:
    pipeline = CustomerIntelligencePipeline(seed=42)
    st.session_state.pipeline_result = pipeline.run_full_pipeline(
        num_customers=200,
        num_transactions=1000,
        num_campaigns=600
    )
    pipeline.close()

res: PipelineExecutionResult = st.session_state.pipeline_result

st.sidebar.markdown("---")
st.sidebar.markdown("### 🧭 Intelligence Views")
nav_choice = st.sidebar.radio(
    "Select View:",
    [
        "📊 Executive KPI & Cohort Retention",
        "🎯 RFM Behavioral Segmentation",
        "⚠️ Churn Risk & Behavioral Attribution",
        "📈 Causal Uplift & Campaign ROI Simulator",
        "💎 Customer Lifetime Value (CLV)",
        "🔍 Customer 360 Explorer",
        "🔒 Tamper-Proof Audit Exporter"
    ]
)

# -----------------------------------------------------------------------------
# VIEW 1: Executive KPI & Cohort Retention
# -----------------------------------------------------------------------------
if nav_choice == "📊 Executive KPI & Cohort Retention":
    st.markdown('<div class="glass-card">', unsafe_allow_html=True)
    st.subheader("📊 Executive Portfolio Summary")

    kpis = res.kpis
    c1, c2, c3, c4, c5 = st.columns(5)
    with c1:
        st.markdown(f'<div class="metric-box"><div class="metric-val">${kpis["total_gross_revenue"]:,.0f}</div><div class="metric-lbl">Gross Revenue</div></div>', unsafe_allow_html=True)
    with c2:
        st.markdown(f'<div class="metric-box"><div class="metric-val">{kpis["total_customers"]:,}</div><div class="metric-lbl">Total Customers</div></div>', unsafe_allow_html=True)
    with c3:
        st.markdown(f'<div class="metric-box"><div class="metric-val">${kpis["average_order_value"]:,.2f}</div><div class="metric-lbl">Avg Order Value</div></div>', unsafe_allow_html=True)
    with c4:
        st.markdown(f'<div class="metric-box"><div class="metric-val-green">{kpis["repeat_purchase_rate_pct"]}%</div><div class="metric-lbl">Repeat Purchase Rate</div></div>', unsafe_allow_html=True)
    with c5:
        clv_val = res.clv_result.enterprise_projected_portfolio_value
        st.markdown(f'<div class="metric-box"><div class="metric-val-gold">${clv_val:,.0f}</div><div class="metric-lbl">Projected 3-Yr CLV</div></div>', unsafe_allow_html=True)

    st.markdown('</div>', unsafe_allow_html=True)

    st.subheader("📅 Monthly Cohort Retention Matrix")
    st.write("Tracks customer return rates grouped by first purchase month across elapsed month offsets.")
    
    # Run cohort query
    pipe = CustomerIntelligencePipeline(seed=42)
    # Temporary reload for queries view
    df_cust, df_tx, df_camp = pipe.generator.generate_dataset(num_customers=200, num_transactions=1000, num_campaign_touchpoints=600)
    pipe.warehouse.load_dataframes(df_cust, df_tx, df_camp)
    df_cohort = pipe.queries.get_cohort_retention_matrix()
    pipe.close()

    if not df_cohort.empty:
        pivot_cohort = df_cohort.pivot(index="cohort", columns="month_offset", values="retention_rate_pct").fillna(0.0)
        st.dataframe(pivot_cohort.style.background_gradient(cmap="Blues", axis=None).format("{:.1f}%"), use_container_width=True)

# -----------------------------------------------------------------------------
# VIEW 2: RFM Behavioral Segmentation
# -----------------------------------------------------------------------------
elif nav_choice == "🎯 RFM Behavioral Segmentation":
    st.subheader("🎯 Algorithmic RFM Customer Segmentation Matrix")
    st.write("Customers categorized into actionable tiers based on Recency, Frequency, and Monetary quintile ranks.")

    rfm_summary = res.rfm_result.segment_summary
    st.dataframe(
        rfm_summary.style.format({
            "total_revenue": "${:,.2f}",
            "avg_monetary": "${:,.2f}",
            "revenue_share_pct": "{:.1f}%",
            "customer_share_pct": "{:.1f}%"
        }),
        use_container_width=True
    )

    st.markdown("### 💡 Marketing Action Strategy by Tier")
    for _, row in rfm_summary.iterrows():
        with st.expander(f"📌 {row['segment']} ({row['customer_count']} customers | {row['revenue_share_pct']}% of Revenue)"):
            c_scores = res.rfm_result.customer_scores
            strat = c_scores.loc[c_scores["segment"] == row["segment"], "action_strategy"].values[0]
            st.info(f"**Recommended Playbook:** {strat}")

# -----------------------------------------------------------------------------
# VIEW 3: Churn Risk & Behavioral Attribution
# -----------------------------------------------------------------------------
elif nav_choice == "⚠️ Churn Risk & Behavioral Attribution":
    st.subheader("⚠️ Predictive Churn Risk & Behavioral Attribution")
    st.write("RandomForest-calibrated churn probability model explaining why customers are at risk.")

    c1, c2 = st.columns([1, 1])
    with c1:
        st.markdown("#### 🚨 Risk Tier Breakdown")
        churn_summary = res.churn_result.risk_tier_summary
        st.dataframe(
            churn_summary.style.format({
                "avg_churn_prob": "{:.2%}",
                "total_spend_at_risk": "${:,.2f}",
                "customer_share_pct": "{:.1f}%"
            }),
            use_container_width=True
        )

    with c2:
        st.markdown("#### 🧠 Key Behavioral Churn Drivers (Feature Importance)")
        importances = pd.DataFrame(
            list(res.churn_result.feature_importances.items()),
            columns=["Behavioral Signal", "Importance Weight"]
        )
        st.dataframe(importances.style.format({"Importance Weight": "{:.3f}"}), use_container_width=True)

# -----------------------------------------------------------------------------
# VIEW 4: Causal Uplift & Campaign ROI Simulator
# -----------------------------------------------------------------------------
elif nav_choice == "📈 Causal Uplift & Campaign ROI Simulator":
    st.subheader("📈 Causal Uplift & Marketing Budget Allocation Simulator")
    st.write("Separates customers into Persuadables, Sure Things, Lost Causes, and Sleeping Dogs to maximize ROI.")

    st.markdown("#### 🎭 Customer Causal Archetypes")
    st.dataframe(
        res.uplift_result.archetype_summary.style.format({
            "avg_uplift_score": "{:+.3f}",
            "avg_control_conversion": "{:.1%}",
            "avg_treatment_conversion": "{:.1%}",
            "customer_share_pct": "{:.1f}%"
        }),
        use_container_width=True
    )

    st.markdown("---")
    st.subheader("💰 Simulation: Targeted Persuadables vs. Blast Everyone")
    sim = res.uplift_result.simulated_roi_targeted_vs_blast

    col_a, col_b = st.columns(2)
    with col_a:
        st.markdown('<div class="glass-card">', unsafe_allow_html=True)
        st.markdown("### 🎯 Targeted Campaign (Persuadables Only)")
        t_data = sim["targeted_strategy"]
        st.write(f"• **Customers Contacted:** `{t_data['customers_contacted']}`")
        st.write(f"• **Campaign Cost:** `${t_data['campaign_cost_usd']:,.2f}`")
        st.write(f"• **Incremental Conversions:** `+{t_data['incremental_conversions']}`")
        st.write(f"• **Net Profit:** `${t_data['net_profit_usd']:,.2f}`")
        st.markdown(f'<div class="metric-val-green">+{t_data["roi_percentage"]}% ROI</div>', unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)

    with col_b:
        st.markdown('<div class="glass-card">', unsafe_allow_html=True)
        st.markdown("### 📢 Blast Campaign (Everyone)")
        b_data = sim["blast_strategy"]
        st.write(f"• **Customers Contacted:** `{b_data['customers_contacted']}`")
        st.write(f"• **Campaign Cost:** `${b_data['campaign_cost_usd']:,.2f}`")
        st.write(f"• **Incremental Conversions:** `+{b_data['incremental_conversions']}`")
        st.write(f"• **Net Profit:** `${b_data['net_profit_usd']:,.2f}`")
        st.markdown(f'<div class="metric-val">{b_data["roi_percentage"]}% ROI</div>', unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)

    st.success(f"💡 **Efficiency Gain:** Targeted campaign is **{sim['efficiency_gain_factor']}x** more cost-effective per dollar spent!")

# -----------------------------------------------------------------------------
# VIEW 5: Customer Lifetime Value (CLV)
# -----------------------------------------------------------------------------
elif nav_choice == "💎 Customer Lifetime Value (CLV)":
    st.subheader("💎 3-Year Discounted Retention Customer Lifetime Value (CLV)")
    st.write("Predictive CLV forecasting lifetime equity across acquisition channels.")

    st.dataframe(
        res.clv_result.segment_clv_summary.style.format({
            "total_projected_clv": "${:,.2f}",
            "avg_customer_clv": "${:,.2f}",
            "avg_retention_rate": "{:.1%}",
            "clv_share_pct": "{:.1f}%"
        }),
        use_container_width=True
    )

# -----------------------------------------------------------------------------
# VIEW 6: Customer 360 Explorer
# -----------------------------------------------------------------------------
elif nav_choice == "🔍 Customer 360 Explorer":
    st.subheader("🔍 Unified Customer 360 Explorer")
    st.write("Drill down into any individual customer record to inspect RFM scores, churn risk, and CLV.")

    df_360 = res.customer_360

    search_id = st.text_input("Filter by Customer ID (or leave blank to view all):", value="")
    filter_segment = st.selectbox("Filter by RFM Segment:", ["All Segments"] + list(df_360["segment"].unique()))

    filtered = df_360
    if search_id.strip():
        filtered = filtered[filtered["customer_id"].str.contains(search_id.strip(), case=False)]
    if filter_segment != "All Segments":
        filtered = filtered[filtered["segment"] == filter_segment]

    st.dataframe(
        filtered[[
            "customer_id", "acquisition_channel", "region", "total_orders",
            "total_spend", "segment", "churn_probability", "risk_tier",
            "causal_archetype", "projected_3yr_clv"
        ]].style.format({
            "total_spend": "${:,.2f}",
            "churn_probability": "{:.1%}",
            "projected_3yr_clv": "${:,.2f}"
        }),
        use_container_width=True
    )

# -----------------------------------------------------------------------------
# VIEW 7: Tamper-Proof Audit Exporter
# -----------------------------------------------------------------------------
elif nav_choice == "🔒 Tamper-Proof Audit Exporter":
    st.subheader("🔒 Cryptographic SHA-256 Audit Report Exporter")
    st.write("Download complete execution telemetry certified by a SHA-256 digital fingerprint.")

    st.code(f"SHA-256 Digest: {res.sha256_audit_hash}", language="text")

    json_str = json.dumps(res.to_dict(), indent=2)
    st.download_button(
        label="💾 Download Audit Report JSON",
        data=json_str,
        file_name=f"nexus_audit_{res.run_id[:8]}.json",
        mime="application/json"
    )

st.markdown("---")
st.markdown(
    '<p style="text-align: center; color: #64748B; font-size: 0.85rem;">'
    'NEXUS-ANALYTICS v1.0 • Enterprise Customer Intelligence Engine • Maintained by Rohit (@Rohittt619)'
    '</p>',
    unsafe_allow_html=True
)
