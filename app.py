import streamlit as st
import pandas as pd
import plotly.express as px

# =====================================================
# PAGE CONFIG
# =====================================================

st.set_page_config(
    page_title="Nassau Candy Profitability Dashboard",
    page_icon="🍫",
    layout="wide"
)

# =====================================================
# LOAD DATA
# =====================================================

@st.cache_data
def load_data():
    df = pd.read_csv("clean_nassau.csv")

    if "Order Date" in df.columns:
        df["Order Date"] = pd.to_datetime(df["Order Date"])

    return df

df = load_data()

# =====================================================
# TITLE
# =====================================================

st.title("🍫 Nassau Candy Product Profitability Dashboard")

st.markdown("""
### Business Objective

This dashboard helps identify:

- High-profit products
- High-margin products
- Margin-risk products
- Division profitability
- Cost inefficiencies
- Profit concentration risks
""")

# =====================================================
# SIDEBAR FILTERS
# =====================================================

st.sidebar.header("Dashboard Filters")

# Date Filter

start_date = st.sidebar.date_input(
    "Start Date",
    df["Order Date"].min()
)

end_date = st.sidebar.date_input(
    "End Date",
    df["Order Date"].max()
)

# Division Filter

division = st.sidebar.selectbox(
    "Division",
    ["All"] + sorted(df["Division"].unique())
)

# Margin Filter

margin_threshold = st.sidebar.slider(
    "Minimum Margin %",
    0,
    100,
    0
)

# Product Search

product_search = st.sidebar.text_input(
    "Search Product"
)

# =====================================================
# FILTER DATA
# =====================================================

filtered_df = df.copy()

filtered_df = filtered_df[
    (filtered_df["Order Date"] >= pd.to_datetime(start_date))
    &
    (filtered_df["Order Date"] <= pd.to_datetime(end_date))
]

if division != "All":
    filtered_df = filtered_df[
        filtered_df["Division"] == division
    ]

if product_search:
    filtered_df = filtered_df[
        filtered_df["Product Name"]
        .str.contains(
            product_search,
            case=False,
            na=False
        )
    ]

filtered_df = filtered_df[
    filtered_df["Gross Margin %"] >= margin_threshold
]

# =====================================================
# KPI SECTION
# =====================================================

st.subheader("Key Performance Indicators")

c1, c2, c3, c4 = st.columns(4)

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

c4.metric(
    "Products",
    filtered_df["Product Name"].nunique()
)

# =====================================================
# TABS
# =====================================================

tab1, tab2, tab3, tab4 = st.tabs([
    "📈 Product Analysis",
    "🏢 Division Analysis",
    "⚙️ Cost Diagnostics",
    "📊 Pareto Analysis"
])

# =====================================================
# TAB 1 - PRODUCT ANALYSIS
# =====================================================

with tab1:

    st.subheader("Top 10 Products by Gross Profit")

    product_profit = (
        filtered_df.groupby("Product Name")
        ["Gross Profit"]
        .sum()
        .reset_index()
        .sort_values(
            "Gross Profit",
            ascending=False
        )
        .head(10)
    )

    fig = px.bar(
        product_profit,
        x="Gross Profit",
        y="Product Name",
        orientation="h",
        title="Top Products by Profit"
    )

    st.plotly_chart(
        fig,
        use_container_width=True
    )

    st.subheader("Margin Leaderboard")

    margin_table = (
        filtered_df.groupby("Product Name")
        ["Gross Margin %"]
        .mean()
        .reset_index()
        .sort_values(
            "Gross Margin %",
            ascending=False
        )
    )

    st.dataframe(
        margin_table,
        use_container_width=True
    )

    st.subheader("Top Profit Contributors")

    contributors = (
        filtered_df.groupby("Product Name")
        ["Profit Contribution %"]
        .mean()
        .reset_index()
        .sort_values(
            "Profit Contribution %",
            ascending=False
        )
        .head(10)
    )

    fig = px.bar(
        contributors,
        x="Profit Contribution %",
        y="Product Name",
        orientation="h"
    )

    st.plotly_chart(
        fig,
        use_container_width=True
    )

# =====================================================
# TAB 2 - DIVISION ANALYSIS
# =====================================================

with tab2:

    st.subheader("Revenue vs Profit by Division")

    division_data = (
        filtered_df.groupby("Division")
        [["Sales", "Gross Profit"]]
        .sum()
        .reset_index()
    )

    fig = px.bar(
        division_data,
        x="Division",
        y=["Sales", "Gross Profit"],
        barmode="group"
    )

    st.plotly_chart(
        fig,
        use_container_width=True
    )

    st.subheader("Average Margin by Division")

    division_margin = (
        filtered_df.groupby("Division")
        ["Gross Margin %"]
        .mean()
        .reset_index()
    )

    fig = px.pie(
        division_margin,
        names="Division",
        values="Gross Margin %"
    )

    st.plotly_chart(
        fig,
        use_container_width=True
    )

# =====================================================
# TAB 3 - COST DIAGNOSTICS
# =====================================================

with tab3:

    st.subheader("Cost vs Sales Analysis")

    fig = px.scatter(
        filtered_df,
        x="Cost",
        y="Sales",
        color="Division",
        hover_name="Product Name",
        size="Gross Profit"
    )

    st.plotly_chart(
        fig,
        use_container_width=True
    )

    st.subheader("Margin Risk Products")

    risk_products = filtered_df[
        filtered_df["Gross Margin %"] < 20
    ][[
        "Product Name",
        "Division",
        "Sales",
        "Gross Profit",
        "Gross Margin %"
    ]]

    st.dataframe(
        risk_products,
        use_container_width=True
    )

# =====================================================
# TAB 4 - PARETO ANALYSIS
# =====================================================

with tab4:

    st.subheader("Profit Concentration Analysis")

    pareto = (
        filtered_df.groupby("Product Name")
        ["Gross Profit"]
        .sum()
        .reset_index()
        .sort_values(
            "Gross Profit",
            ascending=False
        )
    )

    pareto["Cum Profit"] = (
        pareto["Gross Profit"]
        .cumsum()
    )

    pareto["Cum %"] = (
        pareto["Cum Profit"]
        /
        pareto["Gross Profit"].sum()
    ) * 100

    fig = px.line(
        pareto,
        y="Cum %",
        title="Pareto Analysis"
    )

    fig.add_hline(
        y=80,
        line_dash="dash"
    )

    st.plotly_chart(
        fig,
        use_container_width=True
    )

    products_80 = (
        pareto[
            pareto["Cum %"] <= 80
        ]["Product Name"]
        .nunique()
    )

    st.success(
        f"{products_80} products contribute approximately 80% of total profit."
    )

# =====================================================
# DOWNLOAD BUTTON
# =====================================================

st.download_button(
    label="⬇ Download Filtered Data",
    data=filtered_df.to_csv(index=False),
    file_name="filtered_nassau_data.csv",
    mime="text/csv"
)

# =====================================================
# FOOTER
# =====================================================

st.markdown("---")
st.markdown(
    "Developed for Nassau Candy Product Profitability & Margin Performance Analysis"
)
