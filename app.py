import os
import sqlite3
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import streamlit as st

st.set_page_config(
    page_title="Fashion Retail Pricing & Growth Studio",
    layout="wide"
)

DB_PATH = os.path.join("data", "retail_analytics.db")
CSV_PATH = os.path.join("data", "cleaned_retail_data.csv")


@st.cache_data
def load_data():
    if os.path.exists(DB_PATH):
        conn = sqlite3.connect(DB_PATH)
        df = pd.read_sql_query("SELECT * FROM products", conn)
        conn.close()
        return df
    elif os.path.exists(CSV_PATH):
        return pd.read_csv(CSV_PATH)
    else:
        st.error("Cleaned data not found. Please run `py data_pipeline.py` first.")
        st.stop()


df = load_data()

st.title("Fashion Retail Pricing, Demand & Brand Growth Studio")
st.caption(
    "Decision-support analytics for Assortment Strategy, Discount Elasticity, Demand Velocity & Ad Monetization"
)

# Sidebar Filters
st.sidebar.header("Filter Catalog")

all_tiers = ["All"] + sorted(df["price_tier"].dropna().astype(str).unique().tolist())
selected_tier = st.sidebar.selectbox("Price Tier", all_tiers)

all_bands = ["All"] + sorted(df["discount_band"].dropna().astype(str).unique().tolist())
selected_band = st.sidebar.selectbox("Discount Band", all_bands)

min_rating = st.sidebar.slider("Minimum Product Rating", 0.0, 5.0, 0.0, 0.1)

filtered_df = df.copy()
if selected_tier != "All":
    filtered_df = filtered_df[filtered_df["price_tier"].astype(str) == selected_tier]
if selected_band != "All":
    filtered_df = filtered_df[filtered_df["discount_band"].astype(str) == selected_band]
filtered_df = filtered_df[filtered_df["rating"] >= min_rating]

# Top KPI Cards
c1, c2, c3, c4, c5 = st.columns(5)
c1.metric("Active SKUs", f"{len(filtered_df):,}")
c2.metric("Unique Brands", f"{filtered_df['brand'].nunique():,}")
c3.metric("Avg Selling Price", f"₹{filtered_df['selling_price'].mean():,.0f}" if len(filtered_df) else "₹0")
c4.metric("Avg Discount", f"{filtered_df['discount_pct'].mean():.1f}%" if len(filtered_df) else "0.0%")
c5.metric(
    "Ad Pitch Candidates",
    f"{(filtered_df['ad_pitch_target'] == 'High Potential (Pitch Ads)').sum():,}"
)

st.divider()

# Tabs for Business Functions
tab1, tab2, tab3, tab4 = st.tabs([
    "Category & Brand Growth",
    "Discount & Demand Elasticity",
    "Ad Monetization Targets",
    "AI Strategy Copilot"
])

with tab1:
    st.subheader("Top Brands by Revenue Proxy & Assortment Size")
    brand_perf = (
        filtered_df.groupby("brand", as_index=False)
        .agg(
            skus=("selling_price", "count"),
            avg_price=("selling_price", "mean"),
            avg_discount=("discount_pct", "mean"),
            avg_rating=("rating", "mean"),
            revenue_proxy=("estimated_revenue_proxy", "sum"),
        )
        .sort_values("revenue_proxy", ascending=False)
        .head(15)
    )

    if len(brand_perf) > 0:
        fig, ax = plt.subplots(figsize=(10, 4.5))
        plot_df = brand_perf.sort_values("revenue_proxy", ascending=True)
        ax.barh(plot_df["brand"], plot_df["revenue_proxy"] / 1e6)
        ax.set_xlabel("Estimated Revenue Proxy (₹ Millions)")
        ax.set_ylabel("Brand")
        ax.set_title("Top 15 Brands by Estimated Revenue Proxy")
        plt.tight_layout()
        st.pyplot(fig)

    st.dataframe(
        brand_perf.assign(
            avg_price=lambda x: x["avg_price"].round(0),
            avg_discount=lambda x: x["avg_discount"].round(1),
            avg_rating=lambda x: x["avg_rating"].round(2),
            revenue_proxy=lambda x: x["revenue_proxy"].round(0),
        ),
        use_container_width=True,
    )

with tab2:
    st.subheader("How Discount Bands Impact Demand Velocity (Avg Ratings/Reviews)")
    band_perf = (
        filtered_df.groupby("discount_band", observed=False, as_index=False)
        .agg(
            sku_count=("selling_price", "count"),
            avg_selling_price=("selling_price", "mean"),
            avg_demand_velocity=("rating_count", "mean"),
            total_revenue_proxy=("estimated_revenue_proxy", "sum"),
        )
    )

    if len(band_perf) > 0:
        fig2, ax2 = plt.subplots(figsize=(9, 4))
        ax2.bar(band_perf["discount_band"].astype(str), band_perf["avg_demand_velocity"])
        ax2.set_xlabel("Discount Band")
        ax2.set_ylabel("Avg Rating Count (Demand Proxy)")
        ax2.set_title("Average Demand Velocity Across Discount Bands")
        plt.xticks(rotation=15)
        plt.tight_layout()
        st.pyplot(fig2)

    st.dataframe(
        band_perf.assign(
            avg_selling_price=lambda x: x["avg_selling_price"].round(0),
            avg_demand_velocity=lambda x: x["avg_demand_velocity"].round(1),
            total_revenue_proxy=lambda x: x["total_revenue_proxy"].round(0),
        ),
        use_container_width=True,
    )

with tab3:
    st.subheader("High-Rating, Low-Visibility SKUs (Prime Sponsored Ad Candidates)")
    st.write(
        "These SKUs have strong customer ratings (>= 4.2) but lower visibility/rating counts—making them strong candidates for sponsored product placement or visibility campaigns."
    )
    ad_df = filtered_df[filtered_df["ad_pitch_target"] == "High Potential (Pitch Ads)"]
    ad_summary = (
        ad_df.groupby("brand", as_index=False)
        .agg(
            candidate_skus=("selling_price", "count"),
            avg_rating=("rating", "mean"),
            avg_rating_count=("rating_count", "mean"),
            avg_price=("selling_price", "mean"),
        )
        .sort_values(["candidate_skus", "avg_rating"], ascending=[False, False])
    )
    st.dataframe(
        ad_summary.assign(
            avg_rating=lambda x: x["avg_rating"].round(2),
            avg_rating_count=lambda x: x["avg_rating_count"].round(1),
            avg_price=lambda x: x["avg_price"].round(0),
        ),
        use_container_width=True,
    )

with tab4:
    st.subheader("AI Strategy Copilot (Data-Grounded Recommendations)")
    question_preset = st.selectbox(
        "Choose a business question to analyze:",
        [
            "Which discount band drives the highest average demand velocity?",
            "Which top 5 brands lead in estimated revenue proxy?",
            "Where should growth/ad focus go right now?",
        ],
    )

    if st.button("Generate Data-Backed Recommendation"):
        if question_preset == "Which discount band drives the highest average demand velocity?":
            best_band = (
                filtered_df.groupby("discount_band", observed=False)["rating_count"]
                .mean()
                .sort_values(ascending=False)
            )
            if len(best_band) > 0:
                top_b = best_band.index[0]
                top_val = best_band.iloc[0]
                st.success(
                    f"**Recommendation:** The **{top_b}** band leads with an average demand proxy of **{top_val:.1f}** ratings per SKU. "
                    f"Test controlled promo windows around this discount range while monitoring margin impact before pushing deeper discounts."
                )
        elif question_preset == "Which top 5 brands lead in estimated revenue proxy?":
            top5 = (
                filtered_df.groupby("brand")["estimated_revenue_proxy"]
                .sum()
                .sort_values(ascending=False)
                .head(5)
            )
            if len(top5) > 0:
                summary_str = ", ".join([f"{b} (₹{v/1e6:.1f}M)" for b, v in top5.items()])
                st.success(
                    f"**Top 5 Revenue Proxy Brands:** {summary_str}. "
                    f"Prioritize stock availability, size-set depth, and promotional alignment on these core growth drivers."
                )
        else:
            ad_count = (filtered_df["ad_pitch_target"] == "High Potential (Pitch Ads)").sum()
            st.success(
                f"**Growth & Visibility Play:** There are **{ad_count:,}** high-rated (4.2+) SKUs with lower visibility counts in the current view. "
                f"Prioritizing discovery/ad campaigns on proven high-rating SKUs typically converts better than boosting low-rated catalog items."
            )