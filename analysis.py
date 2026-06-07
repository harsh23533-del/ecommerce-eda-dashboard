import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots


# ── 1. LOAD & CACHE ──────────────────────────────────────────────────────────
def load_data(path="superstore.csv"):
    df = pd.read_csv(path, encoding="latin-1")
    df.columns = df.columns.str.strip()

    # Parse dates
    df["Order Date"] = pd.to_datetime(df["Order Date"], dayfirst=False, errors="coerce")
    df["Ship Date"]  = pd.to_datetime(df["Ship Date"],  dayfirst=False, errors="coerce")

    # Derived columns
    df["Year"]          = df["Order Date"].dt.year
    df["Month"]         = df["Order Date"].dt.to_period("M").astype(str)
    df["Quarter"]       = df["Order Date"].dt.to_period("Q").astype(str)
    df["Ship Days"]     = (df["Ship Date"] - df["Order Date"]).dt.days
    df["Profit Margin"] = (df["Profit"] / df["Sales"] * 100).round(2)

    return df


# ── 2. DATA QUALITY REPORT ───────────────────────────────────────────────────
def data_quality_report(df):
    report = pd.DataFrame({
        "Column":        df.columns,
        "Missing":       df.isnull().sum().values,
        "Missing %":     (df.isnull().mean() * 100).round(2).values,
        "Dtype":         df.dtypes.astype(str).values,
        "Unique Values": df.nunique().values,
    })
    return report[report["Missing"] > 0] if report["Missing"].sum() > 0 else report.head(10)


# ── 3. KPI SUMMARY ───────────────────────────────────────────────────────────
def get_kpis(df):
    return {
        "total_sales":    round(df["Sales"].sum(), 2),
        "total_profit":   round(df["Profit"].sum(), 2),
        "total_orders":   df["Order ID"].nunique(),
        "total_customers":df["Customer ID"].nunique(),
        "avg_discount":   round(df["Discount"].mean() * 100, 1),
        "avg_ship_days":  round(df["Ship Days"].mean(), 1),
        "profit_margin":  round(df["Profit"].sum() / df["Sales"].sum() * 100, 2),
        "avg_order_value":round(df.groupby("Order ID")["Sales"].sum().mean(), 2),
    }


# ── 4. CHARTS ────────────────────────────────────────────────────────────────

COLORS = {
    "blue":   "#378ADD",
    "teal":   "#1D9E75",
    "coral":  "#D85A30",
    "amber":  "#BA7517",
    "purple": "#7F77DD",
}

CHART_LAYOUT = dict(
    paper_bgcolor="rgba(0,0,0,0)",
    plot_bgcolor="rgba(0,0,0,0)",
    font=dict(family="sans-serif", size=13),
    margin=dict(l=20, r=20, t=40, b=20),
)


def chart_monthly_sales(df):
    monthly = (
        df.groupby("Month")[["Sales", "Profit"]]
        .sum()
        .reset_index()
        .sort_values("Month")
    )
    fig = make_subplots(specs=[[{"secondary_y": True}]])
    fig.add_trace(go.Bar(
        x=monthly["Month"], y=monthly["Sales"].round(0),
        name="Sales", marker_color=COLORS["blue"], opacity=0.85
    ), secondary_y=False)
    fig.add_trace(go.Scatter(
        x=monthly["Month"], y=monthly["Profit"].round(0),
        name="Profit", line=dict(color=COLORS["teal"], width=2.5), mode="lines+markers"
    ), secondary_y=True)
    fig.update_layout(title="Monthly sales & profit trend", **CHART_LAYOUT,
                      legend=dict(orientation="h", y=1.1))
    fig.update_xaxes(tickangle=45, showgrid=False)
    fig.update_yaxes(title_text="Sales ($)", secondary_y=False, showgrid=True, gridcolor="#f0f0f0")
    fig.update_yaxes(title_text="Profit ($)", secondary_y=True, showgrid=False)
    return fig


def chart_category_breakdown(df):
    cat = (
        df.groupby("Category")[["Sales", "Profit"]]
        .sum()
        .reset_index()
        .sort_values("Sales", ascending=False)
    )
    cat["Profit Margin %"] = (cat["Profit"] / cat["Sales"] * 100).round(1)
    fig = px.bar(
        cat, x="Category", y=["Sales", "Profit"],
        barmode="group",
        color_discrete_map={"Sales": COLORS["blue"], "Profit": COLORS["teal"]},
        title="Sales vs profit by category",
        text_auto=".2s",
    )
    fig.update_layout(**CHART_LAYOUT)
    fig.update_traces(textposition="outside")
    return fig


def chart_subcategory_profit(df):
    sub = (
        df.groupby("Sub-Category")["Profit"]
        .sum()
        .reset_index()
        .sort_values("Profit")
    )
    sub["Color"] = sub["Profit"].apply(lambda x: COLORS["teal"] if x >= 0 else COLORS["coral"])
    fig = go.Figure(go.Bar(
        x=sub["Profit"].round(0), y=sub["Sub-Category"],
        orientation="h",
        marker_color=sub["Color"],
    ))
    fig.update_layout(title="Profit by sub-category (loss in red)", **CHART_LAYOUT,
                      xaxis_title="Total Profit ($)")
    fig.add_vline(x=0, line_color="#888", line_width=1)
    return fig


def chart_region_performance(df):
    region = (
        df.groupby("Region")[["Sales", "Profit"]]
        .sum()
        .reset_index()
    )
    region["Profit Margin %"] = (region["Profit"] / region["Sales"] * 100).round(1)
    fig = px.scatter(
        region, x="Sales", y="Profit",
        size="Sales", color="Region",
        text="Region",
        title="Region — sales vs profit (bubble size = revenue)",
        color_discrete_sequence=list(COLORS.values()),
    )
    fig.update_traces(textposition="top center")
    fig.update_layout(**CHART_LAYOUT)
    return fig


def chart_discount_vs_profit(df):
    sample = df.sample(min(2000, len(df)), random_state=42)
    fig = px.scatter(
        sample, x="Discount", y="Profit Margin",
        color="Category",
        trendline="ols",
        title="Discount vs profit margin — are discounts killing profits?",
        color_discrete_sequence=list(COLORS.values()),
        opacity=0.6,
    )
    fig.update_layout(**CHART_LAYOUT)
    fig.add_hline(y=0, line_color=COLORS["coral"], line_dash="dash", line_width=1.5)
    return fig


def chart_segment_sales(df):
    seg = df.groupby("Segment")["Sales"].sum().reset_index()
    fig = px.pie(
        seg, names="Segment", values="Sales",
        title="Revenue share by customer segment",
        color_discrete_sequence=[COLORS["blue"], COLORS["teal"], COLORS["amber"]],
        hole=0.45,
    )
    fig.update_layout(**CHART_LAYOUT)
    fig.update_traces(textposition="outside", textinfo="percent+label")
    return fig


def chart_shipping_mode(df):
    ship = (
        df.groupby("Ship Mode")[["Sales", "Profit"]]
        .sum()
        .reset_index()
        .sort_values("Sales", ascending=False)
    )
    fig = px.bar(
        ship, x="Ship Mode", y="Sales",
        color="Profit",
        title="Revenue by shipping mode",
        color_continuous_scale=["#D85A30", "#f0f0f0", "#1D9E75"],
        text_auto=".2s",
    )
    fig.update_layout(**CHART_LAYOUT)
    fig.update_traces(textposition="outside")
    return fig


def chart_top_products(df, n=10):
    top = (
        df.groupby("Product Name")["Sales"]
        .sum()
        .nlargest(n)
        .reset_index()
        .sort_values("Sales")
    )
    top["Product Name"] = top["Product Name"].str[:40] + "..."
    fig = px.bar(
        top, x="Sales", y="Product Name",
        orientation="h",
        title=f"Top {n} products by revenue",
        color="Sales",
        color_continuous_scale=["#B5D4F4", "#185FA5"],
        text_auto=".2s",
    )
    fig.update_layout(**CHART_LAYOUT, showlegend=False, coloraxis_showscale=False)
    return fig


def chart_state_heatmap(df):
    state_sales = (
        df.groupby("State")["Sales"].sum().reset_index()
    )
    fig = px.choropleth(
        state_sales,
        locations="State",
        locationmode="USA-states",
        color="Sales",
        scope="usa",
        title="Sales distribution across US states",
        color_continuous_scale=["#E6F1FB", "#185FA5"],
    )
    fig.update_layout(**CHART_LAYOUT)
    return fig


def chart_quarterly_growth(df):
    qtr = (
        df.groupby("Quarter")["Sales"]
        .sum()
        .reset_index()
        .sort_values("Quarter")
    )
    qtr["Growth %"] = qtr["Sales"].pct_change() * 100
    fig = make_subplots(specs=[[{"secondary_y": True}]])
    fig.add_trace(go.Bar(
        x=qtr["Quarter"], y=qtr["Sales"].round(0),
        name="Sales", marker_color=COLORS["blue"], opacity=0.8
    ), secondary_y=False)
    fig.add_trace(go.Scatter(
        x=qtr["Quarter"], y=qtr["Growth %"].round(1),
        name="QoQ Growth %", mode="lines+markers",
        line=dict(color=COLORS["amber"], width=2.5),
        connectgaps=True,
    ), secondary_y=True)
    fig.update_layout(title="Quarterly sales & growth rate", **CHART_LAYOUT,
                      legend=dict(orientation="h", y=1.1))
    fig.update_xaxes(tickangle=45, showgrid=False)
    fig.update_yaxes(title_text="Sales ($)", secondary_y=False, showgrid=True, gridcolor="#f0f0f0")
    fig.update_yaxes(title_text="Growth %", secondary_y=True, showgrid=False)
    return fig


def chart_ship_days_dist(df):
    fig = px.histogram(
        df, x="Ship Days", color="Ship Mode",
        nbins=15,
        title="Shipping days distribution by mode",
        barmode="overlay",
        opacity=0.75,
        color_discrete_sequence=list(COLORS.values()),
    )
    fig.update_layout(**CHART_LAYOUT)
    return fig


def chart_correlation_heatmap(df):
    num_cols = ["Sales", "Quantity", "Discount", "Profit", "Ship Days", "Profit Margin"]
    corr = df[num_cols].corr().round(2)
    fig = go.Figure(go.Heatmap(
        z=corr.values,
        x=corr.columns.tolist(),
        y=corr.columns.tolist(),
        colorscale=[[0, "#D85A30"], [0.5, "#f5f5f5"], [1, "#1D9E75"]],
        zmid=0,
        text=corr.values.round(2),
        texttemplate="%{text}",
    ))
    fig.update_layout(title="Correlation matrix — numeric features", **CHART_LAYOUT)
    return fig


# ── 5. BUSINESS INSIGHTS ─────────────────────────────────────────────────────
def get_insights(df):
    # Insight 1: loss-making sub-categories
    loss_subs = df.groupby("Sub-Category")["Profit"].sum()
    loss_subs = loss_subs[loss_subs < 0].sort_values()

    # Insight 2: discount threshold
    discount_bins = pd.cut(df["Discount"], bins=[-0.01, 0, 0.1, 0.2, 0.3, 0.5, 1.0],
                           labels=["0%", "1-10%", "11-20%", "21-30%", "31-50%", "51%+"])
    disc_profit = df.groupby(discount_bins, observed=True)["Profit Margin"].mean().round(1)

    # Insight 3: best region
    best_region = df.groupby("Region")["Profit"].sum().idxmax()
    best_region_profit = df.groupby("Region")["Profit"].sum().max()

    # Insight 4: peak month
    monthly_sales = df.groupby("Month")["Sales"].sum()
    peak_month = monthly_sales.idxmax()
    peak_sales = monthly_sales.max()

    # Insight 5: avg ship days by mode
    ship_perf = df.groupby("Ship Mode")["Ship Days"].mean().round(1).sort_values()

    return {
        "loss_subcategories": loss_subs,
        "discount_vs_margin": disc_profit,
        "best_region": (best_region, round(best_region_profit, 0)),
        "peak_month": (peak_month, round(peak_sales, 0)),
        "ship_performance": ship_perf,
    }
