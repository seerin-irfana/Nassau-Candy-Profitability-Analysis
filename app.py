
import streamlit as st
import pandas as pd
import plotly.express as px

st.set_page_config(
    page_title="Nassau Candy Dashboard",
    layout="wide"
)

st.title("🍫 Nassau Candy Profitability Dashboard")

df = pd.read_csv("clean_nassau.csv")

# Sidebar Filters
st.sidebar.header("Filters")

division = st.sidebar.selectbox(
    "Division",
    ["All"] + list(df["Division"].unique())
)

margin = st.sidebar.number_input(
    "Minimum Margin %",
    min_value=0,
    max_value=100,
    value=0
)

product_search = st.sidebar.text_input(
    "Search Product"
)

filtered_df = df.copy()

if division != "All":
    filtered_df = filtered_df[
        filtered_df["Division"] == division
    ]

if product_search:
    filtered_df = filtered_df[
        filtered_df["Product Name"]
        .str.contains(product_search, case=False)
    ]

filtered_df = filtered_df[
    filtered_df["Gross Margin %"] >= margin
]

# KPI Cards
c1,c2,c3 = st.columns(3)

c1.metric(
    "Total Sales",
    f"${filtered_df['Sales'].sum():,.0f}"
)

c2.metric(
    "Total Profit",
    f"${filtered_df['Gross Profit'].sum():,.0f}"
)

c3.metric(
    "Average Margin",
    f"{filtered_df['Gross Margin %'].mean():.2f}%"
)

# Product Profitability
st.subheader("Top 10 Products by Profit")

product_profit = (
    filtered_df.groupby("Product Name")
    ["Gross Profit"]
    .sum()
    .reset_index()
)

product_profit = product_profit.sort_values(
    "Gross Profit",
    ascending=False
).head(10)

fig = px.bar(
    product_profit,
    x="Gross Profit",
    y="Product Name",
    orientation="h"
)

st.plotly_chart(fig, use_container_width=True)

# Division Analysis
st.subheader("Division Performance")

division_data = (
    filtered_df.groupby("Division")
    [["Sales","Gross Profit"]]
    .sum()
    .reset_index()
)

fig = px.bar(
    division_data,
    x="Division",
    y=["Sales","Gross Profit"],
    barmode="group"
)

st.plotly_chart(fig, use_container_width=True)

# Cost Diagnostics
st.subheader("Cost vs Sales")

fig = px.scatter(
    filtered_df,
    x="Cost",
    y="Sales",
    color="Division",
    hover_name="Product Name"
)

st.plotly_chart(fig, use_container_width=True)

# Pareto Analysis
st.subheader("Pareto Analysis")

pareto = (
    filtered_df.groupby("Product Name")
    ["Gross Profit"]
    .sum()
    .reset_index()
)

pareto = pareto.sort_values(
    "Gross Profit",
    ascending=False
)

pareto["Cum Profit"] = pareto["Gross Profit"].cumsum()

pareto["Cum %"] = (
    pareto["Cum Profit"]
    /
    pareto["Gross Profit"].sum()
) * 100

fig = px.line(
    pareto,
    y="Cum %",
    title="Cumulative Profit Contribution"
)

st.plotly_chart(fig, use_container_width=True)
