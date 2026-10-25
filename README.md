# NEXUS-ANALYTICS 🚀

<div align="center">

[![Python](https://img.shields.io/badge/Python-3.10%20%7C%203.11%20%7C%203.12-3776AB?style=for-the-badge&logo=python&logoColor=white)](https://www.python.org/)
[![DuckDB](https://img.shields.io/badge/DuckDB-In--Memory%20OLAP-FFF000?style=for-the-badge&logo=duckdb&logoColor=black)](https://duckdb.org/)
[![Streamlit](https://img.shields.io/badge/Streamlit-Cockpit%20UI-FF4B4B?style=for-the-badge&logo=streamlit&logoColor=white)](https://streamlit.io/)
[![Docker](https://img.shields.io/badge/Docker-Multi--Stage%20Ready-2496ED?style=for-the-badge&logo=docker&logoColor=white)](https://www.docker.com/)
[![CI/CD](https://img.shields.io/badge/CI%2FCD-GitHub%20Actions-2088FF?style=for-the-badge&logo=githubactions&logoColor=white)](https://github.com/Rohittt619/NEXUS-ANALYTICS/actions)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg?style=for-the-badge)](https://opensource.org/licenses/MIT)

**Enterprise Customer Intelligence, Churn Causality, CLV & Campaign ROI Optimization Engine**

*Built by [Rohit (@Rohittt619)](https://github.com/Rohittt619) &bull; [rrathod1101@gmail.com](mailto:rrathod1101@gmail.com)*

---

</div>

## 📌 Executive Overview

**NEXUS-ANALYTICS** is a high-performance customer intelligence and marketing optimization system engineered for data-driven enterprises. Traditional customer analytics platforms suffer from slow disk-based joins, black-box churn models that lack actionable intervention paths, and naive campaign blasting that squanders marketing budget on customers who would have purchased organically.

NEXUS solves this through an embedded in-memory **DuckDB star-schema analytical warehouse**, an automated **algorithmic RFM segmentation engine**, an interpretable **Machine Learning Churn Scorer** with behavioral feature attribution, a **Two-Model Causal Uplift Estimator**, and a **Discounted Retention Customer Lifetime Value (CLV)** forecaster.

Every run produces a deterministic **SHA-256 cryptographic audit digest**, providing an immutable ledger for enterprise compliance.

---

## ⚡ Core Capabilities & Architecture

```
                                  NEXUS-ANALYTICS ARCHITECTURE
                                  
+-------------------------------------------------------------------------------------------------+
|                                 1. SYNTHETIC GENERATOR & ETL                                    |
|   - Deterministic Faker & NumPy Pareto Distributions                                            |
|   - Zero-Secret Compliance: 100% Synthetic Customer, Transaction & Campaign Touchpoint Streams |
+-------------------------------------------------------------------------------------------------+
                                                 │
                                                 ▼
+-------------------------------------------------------------------------------------------------+
|                                2. DUCKDB STAR-SCHEMA WAREHOUSE                                  |
|   - Dimension Tables: dim_customers, dim_loyalty_tiers                                          |
|   - Fact Tables: fact_transactions, fact_campaign_touchpoints                                   |
|   - Analytical SQL Engines: Cohort Retention Matrices, Customer Velocity & Category Affinity    |
+-------------------------------------------------------------------------------------------------+
                                                 │
                                                 ▼
+-------------------------------------------------------------------------------------------------+
|                                    3. ANALYTICAL ENGINES                                        |
|   ├── Algorithmic RFM: 5x5x5 Quintile Scoring & 10 Behavioral Action Archetypes                 |
|   ├── Churn Risk ML: Random Forest Classifier + Behavioral Feature Importance Attributions      |
|   ├── Causal Uplift: Two-Model Uplift (Treatment vs Control) with 4 Causal Archetypes          |
|   └── CLV Forecaster: 36-Month Discounted Retention Cash-Flow Valuation                        |
+-------------------------------------------------------------------------------------------------+
                                                 │
                                                 ▼
+-------------------------------------------------------------------------------------------------+
|                             4. ORCHESTRATION & AUDIT PROVENANCE                                 |
|   - Customer 360 Unified View Generation                                                        |
|   - Cryptographic SHA-256 Audit Digest Fingerprinting                                           |
+-------------------------------------------------------------------------------------------------+
                                                 │
                        ┌────────────────────────┴────────────────────────┐
                        ▼                                                 ▼
+-----------------------------------------------+ +-----------------------------------------------+
|       STREAMLIT EXECUTIVE DECISION COCKPIT    | |             TYPER / RICH TERMINAL CLI         |
|  - Glassmorphism Dark UI with Plotly Analytics| |  - Headless CI/CD Pipeline Execution         |
|  - Interactive Uplift ROI Strategy Simulator  | |  - Rich Formatted Metric Summary Tables       |
|  - Real-Time Customer 360 Explorer & Audit Log| |  - Fast Subsystem Diagnostics & Auditing      |
+-----------------------------------------------+ +-----------------------------------------------+
```

---

## 🔬 Mathematical Formulations

### 1. Algorithmic RFM Segmentation
Customers are scored along three dimensions:
- **Recency ($R$)**: Days since last transaction.
- **Frequency ($F$)**: Total count of completed orders.
- **Monetary ($M$)**: Cumulative gross spend.

Scores are computed via quintile partitioning ($\text{Score} \in [1, 5]$) using rank preservation:
$$\text{Rank}_i = \text{Rank}(X_i, \text{method}='first')$$
$$\text{Score}_i = \lceil \frac{\text{Rank}_i}{N / 5} \rceil$$

Scores are mapped into 10 actionable tiers including **Champions** ($R\ge 4, F\ge 4, M\ge 4$), **Loyal Customers**, **Potential Loyalists**, **At Risk (High Value)**, and **Hibernating**.

### 2. Causal Uplift (Individual Treatment Effect)
Standard marketing models predict $P(\text{Conversion} \mid \text{Targeted})$, creating false attribution for organic buyers. NEXUS implements a **Two-Model Uplift Strategy**:

$$\tau_i = P(Y_i=1 \mid T_i=1, X_i) - P(Y_i=1 \mid T_i=0, X_i)$$

Where:
- $T_i=1$: Marketing Touchpoint Exposed (Treatment).
- $T_i=0$: Baseline Unexposed (Control).
- $\tau_i$: Incremental Lift Score.

Customers are classified into four distinct causal archetypes:
1. **Persuadables ($\tau_i > 0$, High Incremental Lift)**: The *only* segment targeted for campaign spend.
2. **Sure Things ($\tau_i \approx 0$, High Baseline)**: Organic converters; coupons squander profit.
3. **Lost Causes ($\tau_i \le 0$, Low Baseline)**: Will not convert regardless of spend.
4. **Sleeping Dogs ($\tau_i < 0$)**: Marketing triggers churn or opt-out; suppressed from outreach.

### 3. Discounted Retention Customer Lifetime Value (CLV)
CLV is projected over a 3-year (36-month) horizon using discrete discounted cash flows:

$$\text{CLV}_i = \sum_{t=1}^{3} \frac{\bar{m}_i \cdot (1 - P(\text{churn}_i))^t}{(1 + d)^t}$$

Where $\bar{m}_i$ is the annualized gross margin, $P(\text{churn}_i)$ is predicted by the ML churn engine, and $d$ is the corporate discount rate ($10\%$).

---

## 🛠️ Quickstart Installation

### Option A: Local Virtual Environment

```bash
# Clone repository
git clone https://github.com/Rohittt619/NEXUS-ANALYTICS.git
cd NEXUS-ANALYTICS

# Create and activate Python virtual environment
python -m venv .venv
# On Windows:
.venv\Scripts\activate
# On Linux/macOS:
source .venv/bin/activate

# Install in editable mode with development & UI dependencies
pip install -e ".[dev,ui]"
```

---

## 💻 Usage

### 1. Launching the Streamlit Executive Cockpit

```bash
streamlit run src/nexus/ui/app.py
```
Open your browser at `http://localhost:8501` to access:
- **Executive KPI Cards**: Real-time revenue, AOV, repeat purchase rates, and total portfolio valuation.
- **RFM Segmentation Matrix**: Scatter plots of Recency vs. Monetary value with segment distribution bars.
- **Churn Intelligence**: Probability histograms and top behavioral risk driver attributions.
- **Causal Uplift & ROI Simulator**: Interactive sliders for campaign reach, coupon cost, and conversion revenue comparing **Targeted (Persuadables)** vs. **Blast** marketing.
- **Customer 360 Explorer**: Filterable directory with live CSV exports.

### 2. Command-Line Interface (CLI)

NEXUS includes an enterprise Typer CLI for headless execution, automated batch pipelines, and reporting:

```bash
# Run the complete end-to-end intelligence pipeline
nexus run --customers 500 --transactions 2500 --campaigns 1200

# View analytical DuckDB warehouse KPIs
nexus kpis --customers 300

# Audit RFM customer segmentation tiers
nexus rfm --customers 300

# Audit customer churn probability distributions
nexus churn --customers 300

# Run causal uplift campaign ROI simulation
nexus uplift --customers 300
```

---

## 🐳 Docker Deployment

A production-grade, multi-stage Docker build is included with dedicated non-root security:

```bash
# Build and run the Streamlit UI cockpit using Docker Compose
docker compose up nexus-ui -d

# Execute the headless CLI pipeline inside Docker
docker compose run --rm nexus-cli
```

---

## 🧪 Comprehensive Verification Suite

Run the full pytest suite containing **27 unit and end-to-end integration tests**:

```bash
# Run all tests
pytest tests/ -v

# Run with test durations and summary
pytest tests/ -v --durations=5
```

---

## 🔒 Security & Zero-Secret Guarantee

- **Zero API Keys or Cloud Secrets**: All data pipelines utilize a deterministic, synthetic data generation engine backed by Faker and NumPy Pareto distributions.
- **Zero Disk Leakage**: Default operational storage runs purely in `:memory:` via DuckDB with no transient artifacts written to disk unless explicitly commanded.
- **SHA-256 Audit Integrity**: Every execution run stamps a cryptographic hash calculated across the normalized pipeline output, ensuring verifiable data lineage.

---

## 👤 Author & Maintainer

**Rohit**
- GitHub: [@Rohittt619](https://github.com/Rohittt619)
- Email: [rrathod1101@gmail.com](mailto:rrathod1101@gmail.com)

---

## 📄 License

This project is licensed under the terms of the [MIT License](LICENSE).
