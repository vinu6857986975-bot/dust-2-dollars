# Problem Statement: The Retail Dead-Stock Blindspot

## 1. Background
Modern retailers hold between 15% and 30% of their total working capital in dormant inventory. Dead stock arises from forecasting errors, unpredictable seasonal shifts, changing consumer trends, and flawed supply chain visibility.

## 2. The Core Gap
Existing ERP and inventory management platforms answer **"What is remaining?"** but leave the critical question unanswered:
> **"What specific action must be taken right now to maximize capital recovery while preserving brand equity and complying with contractual supplier terms?"**

## 3. Concrete Scenario
- **Product:** Nordic Thermal Winter Parka
- **On-Hand Stock:** 42 units
- **Stock Age:** 145 days
- **Unit Cost Price:** ₹1,500
- **Current Retail Price:** ₹2,499
- **Locked Capital:** ₹63,000 (Cost) / ₹104,958 (Retail)
- **Supplier Clause:** Return allowed within 30 days of receipt
- **Problem:** Supplier return is legally closed; warehouse holding costs accrue at ₹25/unit/month. Storing it past spring will incur ₹10,500 in dead holding expenses and result in zero recovery.

## 4. Project Mandate
Build an autonomous decision-support system that synthesizes stock velocity, category decay rates, supplier contract terms, and margin bounds to output ranked, executable recovery strategies with auditable reasoning.
