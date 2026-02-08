import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns

# -------------------------
# Page config
# -------------------------
st.set_page_config(
    page_title="Nassau Candy Profitability Analysis",
    layout="wide"
)

st.title("Product Line Profitability & Margin Performance Analysis")
st.caption("Nassau Candy Distributor")

# -------------------------
# Load data
# -------------------------
@st.cache_data
def load_data():
    df = pd.read_csv("Nassau Candy Distributor.csv")
    df["Order Date"] = pd.to_datetime(df["Order Date"], errors="coerce")
    df["Ship Date"] = pd.to_datetime(df["Ship Date"], errors="coerce")
    return df

df = load_data()

# -------------------------
# Derived metrics
# -------------------------
df["Gross Margin %"] = df["Gross Profit"] / df["Sales"]
df["Profit per Unit"] = df["Gross Profit"] / df["Units"]

# -------------------------
# Sidebar filters
# -------------------------
st.sidebar.header("Filters")

min_date = df["Order Date"].min()
max_date = df["Order Date"].max()

date_range = st.sidebar.date_input(
    "Order Date Range",
    value=(min_date, max_date)
)

divisions = st.sidebar.multiselect(
    "Select Division",
    options=df["Division"].unique(),
    default=df["Division"].unique()
)

margin_threshold = st.sidebar.slider(
    "Margin Threshold (%)",
    0, 100, 20
)

filtered_df = df[
    (df["Order Date"] >= pd.to_datetime(date_range[0])) &
    (df["Order Date"] <= pd.to_datetime(date_range[1])) &
    (df["Division"].isin(divisions))
]

# -------------------------
# Product Profitability Overview
# -------------------------
st.header("Product Profitability Overview")

product_summary = (
    filtered_df
    .groupby("Product Name", as_index=False)
    .agg({
        "Sales": "sum",
        "Gross Profit": "sum",
        "Units": "sum"
    })
)

product_summary["Gross Margin %"] = (
    product_summary["Gross Profit"] / product_summary["Sales"]
)
product_summary["Profit per Unit"] = (
    product_summary["Gross Profit"] / product_summary["Units"]
)

st.dataframe(
    product_summary.sort_values("Gross Profit", ascending=False),
    use_container_width=True
)

# -------------------------
# Division Performance Dashboard
# -------------------------
st.header("Division Performance Dashboard")

division_summary = (
    filtered_df
    .groupby("Division", as_index=False)
    .agg({
        "Sales": "sum",
        "Gross Profit": "sum"
    })
)

division_summary["Gross Margin %"] = (
    division_summary["Gross Profit"] / division_summary["Sales"]
)

fig, ax = plt.subplots()
sns.barplot(
    data=division_summary,
    x="Division",
    y="Gross Margin %",
    ax=ax
)
plt.xticks(rotation=45)
plt.title("Gross Margin by Division")
st.pyplot(fig)

# -------------------------
# Cost vs Margin Diagnostics
# -------------------------
st.header("Cost vs Margin Diagnostics")

cost_df = (
    filtered_df
    .groupby("Product Name", as_index=False)
    .agg({
        "Sales": "sum",
        "Cost": "sum",
        "Gross Profit": "sum"
    })
)

cost_df["Gross Margin %"] = cost_df["Gross Profit"] / cost_df["Sales"]

fig, ax = plt.subplots()
sns.scatterplot(
    data=cost_df,
    x="Sales",
    y="Cost",
    hue="Gross Margin %",
    ax=ax
)
plt.title("Cost vs Sales by Product")
st.pyplot(fig)

# -------------------------
# Profit Concentration (Pareto) Analysis
# -------------------------
st.header("Profit Concentration Analysis")

pareto_df = (
    product_summary[["Product Name", "Gross Profit"]]
    .sort_values("Gross Profit", ascending=False)
    .reset_index(drop=True)
)

pareto_df["Cumulative Profit"] = pareto_df["Gross Profit"].cumsum()
total_profit = pareto_df["Gross Profit"].sum()
pareto_df["Cumulative Profit %"] = pareto_df["Cumulative Profit"] / total_profit

fig, ax = plt.subplots(figsize=(10, 5))
ax.plot(
    pareto_df.index,
    pareto_df["Cumulative Profit %"]
)
ax.axhline(0.8, linestyle="--")
ax.set_title("Pareto Analysis – Profit Concentration")
ax.set_xlabel("Products (sorted by profit)")
ax.set_ylabel("Cumulative Profit %")

st.pyplot(fig)

# -------------------------
# Product Search
# -------------------------
st.sidebar.header("Product Search")

search_term = st.sidebar.text_input("Search Product")

if search_term:
    st.subheader("Search Results")
    st.dataframe(
        product_summary[
            product_summary["Product Name"]
            .str.contains(search_term, case=False, na=False)
        ],
        use_container_width=True
    )
