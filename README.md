# Fashion Retail Pricing, Demand & Brand Growth Studio

An end-to-end retail analytics decision-support system built with **Python, SQLite/SQL, Pandas, Matplotlib, and Streamlit** to analyze catalog assortment, discount elasticity, demand velocity, and sponsored ad monetization opportunities across fashion retail SKUs.

## Key Business Modules
1. **Data Pipeline & Quality Engine (`data_pipeline.py`)**:
   - Deduplicates raw scraped catalog records (52,120 raw rows refined to 35,073 unique SKUs) and normalizes brand and product fields.
   - Recalculates accurate discount percentages from MRP and selling price while handling scraping anomalies.
   - Engineers business features: **Price Tiers**, **Discount Bands**, **Estimated Revenue Proxy**, and **Ad Pitch Targets** (high-rating SKUs with lower visibility).
   - Persists clean outputs to `data/cleaned_retail_data.csv` and SQLite database `data/retail_analytics.db`.

2. **Business SQL Layer (`sql/business_queries.sql`)**:
   - Brand & category revenue/assortment rankings.
   - Discount band demand velocity analysis.
   - Price tier distribution and ad-monetization candidate identification.

3. **Interactive Analytics & Strategy Copilot (`app.py`)**:
   - Filter by **Price Tier**, **Discount Band**, and **Minimum Rating**.
   - Explore **Category & Brand Growth**, **Discount & Demand Elasticity**, **Ad Monetization Targets**, and data-backed recommendations in the **AI Strategy Copilot**.

## How to Run Locally
```bash
pip install -r requirements.txt
py data_pipeline.py
py -m streamlit run app.py