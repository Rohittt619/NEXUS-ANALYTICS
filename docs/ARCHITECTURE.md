# NEXUS-ANALYTICS: System Architecture & Engineering Specifications

## 1. Executive System Overview

`NEXUS-ANALYTICS` is an enterprise customer intelligence, churn causality, and campaign ROI optimization engine designed for high-throughput transactional ecosystems. The system couples an embedded columnar analytical warehouse (**DuckDB**) with machine learning classification (**Random Forest / Gradient Boosting**), statistical causal inference (**Uplift 2-Model Modeling**), and discounted cash-flow valuation (**Customer Lifetime Value**).

Every pipeline execution is deterministically reproducible and sealed with a cryptographic **SHA-256 audit digest** ensuring zero data tampering across execution cycles.

```
+---------------------------------------------------------------------------------------+
|                                  NEXUS-ANALYTICS                                      |
+---------------------------------------------------------------------------------------+
                                           |
    +--------------------------------------+--------------------------------------+
    |                                      |                                      |
    v                                      v                                      v
[Synthetic Generator]            [DuckDB Star-Warehouse]           [Analytical SQL Engine]
(Faker + Numpy Pareto)           - dim_customers                   - Cohort Retention Matrix
                                 - dim_loyalty_tiers               - Customer Velocity Dynamics
                                 - fact_transactions               - Category Affinity Index
                                 - fact_campaign_touchpoints
                                           |
    +--------------------------------------+--------------------------------------+
    |                                      |                                      |
    v                                      v                                      v
[Algorithmic RFM]                 [Churn Risk ML]                  [Causal Uplift & CLV]
- Quintile Binning (1-5)         - Random Forest Classifier        - Two-Model Uplift (T vs C)
- 10 Behavioral Segments         - Inactivity Scoring              - 4 Causal Archetypes
- Segment-level Strategies       - Feature Attributions            - 3-Yr Discounted Retention
                                           |
                                           v
                       +---------------------------------------+
                       | Master Customer Intelligence Pipeline |
                       | - Unified Customer 360 View           |
                       | - SHA-256 Audit Digest Fingerprint    |
                       +---------------------------------------+
                                           |
                 +-------------------------+-------------------------+
                 |                                                   |
                 v                                                   v
   [Streamlit Executive Cockpit]                           [Typer / Rich CLI]
   - Glassmorphism Dark UI                                 - Headless CI/CD Automation
   - Interactive Causal Simulator                          - Metric & RFM Reporting
```

---

## 2. Warehouse Schema & Data Model

The analytical storage utilizes **DuckDB** in an OLAP star-schema, minimizing redundant dimension lookups and maximizing vectorized query execution speed.

### Entity-Relationship Diagram

```
+---------------------------+             +-------------------------------+
|       dim_customers       | 1         * |       fact_transactions       |
+---------------------------+-------------+-------------------------------+
| customer_id (PK)          |             | transaction_id (PK)           |
| signup_date (TIMESTAMP)   |             | customer_id (FK)              |
| acquisition_channel (STR) |             | timestamp (TIMESTAMP)         |
| region (STR)              |             | order_amount (DECIMAL)        |
| initial_loyalty_score(INT)|             | discount_applied (DECIMAL)    |
| is_opted_in_marketing(BOL)|             | category (STR)                |
+---------------------------+             | payment_method (STR)          |
             |                            | items_count (INT)             |
             | 1                          +-------------------------------+
             |
             | *
+-------------------------------+         +-------------------------------+
|   fact_campaign_touchpoints   |         |       dim_loyalty_tiers       |
+-------------------------------+         +-------------------------------+
| event_id (PK)                 |         | tier_id (PK)                  |
| customer_id (FK)              |         | tier_name (STR)               |
| campaign_name (STR)           |         | min_spend (DECIMAL)           |
| channel (STR)                 |         | cashback_percent (DECIMAL)    |
| cost_usd (DECIMAL)            |         | priority_support (BOOLEAN)    |
| converted (BOOLEAN)           |         +-------------------------------+
| conversion_revenue (DECIMAL)  |
| timestamp (TIMESTAMP)         |
+-------------------------------+
```

---

## 3. Algorithmic Modeling Engines

### 3.1. Algorithmic RFM Segmentation
Customers are categorized using quintile-based scoring across Recency, Frequency, and Monetary attributes:
$$\text{Score} \in \{1, 2, 3, 4, 5\}$$

Tie-handling utilizes `rank(method='first')` before binning to ensure continuous distribution integrity. Customers are mapped into 10 industry tiers:
- **Champions**: $R \ge 4, F \ge 4, M \ge 4$ (VIP early-access & exclusive previews)
- **Loyal Customers**: $R \ge 3, F \ge 3$ (Upsell & loyalty rewards)
- **Potential Loyalists**: $R \ge 4, F \le 2$ (Cross-sell & second-purchase incentives)
- **Promising New**: $R \ge 3, F = 1$ (Onboarding drip sequences)
- **Needs Attention**: $R = 3, F = 2$ (Category-specific reactivations)
- **At Risk (High Value)**: $R \le 2, F \ge 3, M \ge 3$ (Urgent win-back & direct outreach)
- **Can't Lose Them**: $R = 1, F \ge 4$ (Dedicated account manager intervention)
- **About to Sleep**: $R \le 2, F \le 2, M \ge 3$ (Frictionless re-engagement)
- **Hibernating**: $R \le 2, F \le 2$ (Low-cost discount drip emails)
- **Lost Customers**: Remaining population (Exit survey or deprioritize)

### 3.2. Machine Learning Churn Risk Scorer
- **Target Variable**: Inactivity window exceeding 90 days.
- **Model**: Ensembled Random Forest Classifier with balanced class weighting.
- **Features Extracted**:
  - `recency_days`: Days elapsed since last completed purchase.
  - `total_orders`: Cumulative transaction volume.
  - `total_spend`: Lifetime spend to date.
  - `avg_order_value`: Historical basket sizing.
  - `campaign_engagement_rate`: Ratio of marketing interactions converted.
  - `discount_sensitivity`: Average discount claimed per order.
- **Risk Tiers**:
  - *Low Risk*: $P(\text{churn}) < 0.25$
  - *Moderate Risk*: $0.25 \le P(\text{churn}) < 0.50$
  - *High Risk*: $0.50 \le P(\text{churn}) < 0.75$
  - *Critical Risk*: $P(\text{churn}) \ge 0.75$

### 3.3. Causal Uplift & Incremental ROI
Standard marketing response models suffer from confounding: targeting customers who would have purchased regardless (*Sure Things*) wastes budget, while contacting customers who churn when provoked (*Sleeping Dogs*) actively destroys revenue.

`NEXUS-ANALYTICS` implements the **Two-Model Uplift Approach**:
$$\tau_i = P(Y_i=1 \mid T_i=1, X_i) - P(Y_i=1 \mid T_i=0, X_i)$$

Where:
- $T_i=1$: Customer was targeted with campaign.
- $T_i=0$: Customer was in the unexposed control group.
- $\tau_i$: Individual Treatment Effect (ITE) / Incremental Uplift.

**The Four Causal Archetypes**:
1. **Persuadables ($\tau_i > 0$, High Incremental Lift)**: The only segment that justifies paid ad spend.
2. **Sure Things ($\tau_i \approx 0$, High Baseline)**: Buy organically; do not offer discounts.
3. **Lost Causes ($\tau_i \le 0$, Low Baseline)**: Will not convert regardless of marketing; cease contact.
4. **Sleeping Dogs ($\tau_i < 0$, Negative Lift)**: Marketing triggers opt-outs or refunds; suppress.

### 3.4. Discounted Retention Customer Lifetime Value (CLV)
CLV is projected across a 36-month horizon using a continuous retention discount cash-flow framework:
$$\text{CLV}_i = \sum_{t=1}^{3} \frac{\bar{m}_i \cdot r_i^t}{(1 + d)^t}$$

Where:
- $\bar{m}_i$: Annualized historical customer gross margin ($Spend_i \times \text{Margin Rate}$).
- $r_i$: Individual retention probability derived from inverse churn probability ($1 - P(\text{churn}_i)$).
- $d$: Annual corporate discount rate (configured at $10\%$).

---

## 4. Cryptographic Audit Hasher

To ensure auditability across compliance regimes (e.g. SOC2, internal finance audits), the pipeline constructs a normalized JSON summary of KPIs, segment sizes, churn risk quantiles, and CLV portfolio values.

The hash is generated via:
$$\text{Digest} = \text{SHA256}(\text{CanonicalJSON}(\text{PipelineSummary}))$$

Any deviation in customer records or financial KPIs alters the 64-character hexadecimal digest, providing an immutable audit trail.
