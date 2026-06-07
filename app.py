import streamlit as st
import pandas as pd
from analysis import (
    load_data, get_kpis, data_quality_report, get_insights,
    chart_monthly_sales, chart_category_breakdown, chart_subcategory_profit,
    chart_region_performance, chart_discount_vs_profit, chart_segment_sales,
    chart_shipping_mode, chart_top_products, chart_state_heatmap,
    chart_quarterly_growth, chart_ship_days_dist, chart_correlation_heatmap,
)

# ── PAGE CONFIG ───────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="E-Commerce Sales Dashboard",
    page_icon="🛒",
    layout="wide",
    initial_sidebar_state="expanded",
)

st.markdown("""
<style>
    .block-container { padding-top: 1.5rem; padding-bottom: 2rem; }
    .metric-card { background: #f8f9fa; border-radius: 10px; padding: 1rem 1.25rem; }
    [data-testid="stMetricValue"] { font-size: 1.6rem !important; font-weight: 600; }
    .section-title { font-size: 1.1rem; font-weight: 600; margin: 1.5rem 0 0.5rem; color: #1a1a2e; }
    .insight-box { background: #eaf3de; border-left: 4px solid #1D9E75;
                   padding: 0.75rem 1rem; border-radius: 0 8px 8px 0; margin: 0.5rem 0; font-size: 0.92rem; }
    .warning-box { background: #faece7; border-left: 4px solid #D85A30;
                   padding: 0.75rem 1rem; border-radius: 0 8px 8px 0; margin: 0.5rem 0; font-size: 0.92rem; }
</style>
""", unsafe_allow_html=True)


# ── LOAD DATA ─────────────────────────────────────────────────────────────────
@st.cache_data
def get_df():
    return load_data("data/superstore.csv")

try:
    df_raw = get_df()
except FileNotFoundError:
    st.error("Dataset not found! Please place `superstore.csv` inside the `data/` folder.")
    st.stop()


# ── SIDEBAR FILTERS ───────────────────────────────────────────────────────────
st.sidebar.image("https://img.icons8.com/color/48/shopping-cart.png", width=40)
st.sidebar.title("Filters")

years = sorted(df_raw["Year"].dropna().unique())
sel_years = st.sidebar.multiselect("Year", years, default=years)

categories = sorted(df_raw["Category"].dropna().unique())
sel_cats = st.sidebar.multiselect("Category", categories, default=categories)

regions = sorted(df_raw["Region"].dropna().unique())
sel_regions = st.sidebar.multiselect("Region", regions, default=regions)

segments = sorted(df_raw["Segment"].dropna().unique())
sel_segs = st.sidebar.multiselect("Customer segment", segments, default=segments)

# Apply filters
df = df_raw[
    df_raw["Year"].isin(sel_years) &
    df_raw["Category"].isin(sel_cats) &
    df_raw["Region"].isin(sel_regions) &
    df_raw["Segment"].isin(sel_segs)
].copy()

if df.empty:
    st.warning("No data matches your filters. Please adjust the sidebar.")
    st.stop()

st.sidebar.markdown(f"**{len(df):,}** rows selected")
st.sidebar.markdown("---")
st.sidebar.markdown("**Project:** EDA + Dashboard  \n**Dataset:** Global Superstore  \n**Built with:** Streamlit + Plotly")


# ── HEADER ────────────────────────────────────────────────────────────────────
st.title("🛒 E-Commerce Sales Intelligence Dashboard")
st.caption(f"Global Superstore · {df['Order Date'].min().strftime('%b %Y')} – {df['Order Date'].max().strftime('%b %Y')} · {len(df):,} orders")

tabs = st.tabs(["📊 Overview", "📦 Products", "🗺 Geography", "🚚 Shipping", "🔍 Data Quality", "💡 Insights"])


# ══════════════════════════════════════════════════════════════════════════════
# TAB 1 — OVERVIEW
# ══════════════════════════════════════════════════════════════════════════════
with tabs[0]:
    kpi = get_kpis(df)

    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Total Revenue",    f"${kpi['total_sales']:,.0f}")
    col2.metric("Total Profit",     f"${kpi['total_profit']:,.0f}")
    col3.metric("Profit Margin",    f"{kpi['profit_margin']}%")
    col4.metric("Unique Orders",    f"{kpi['total_orders']:,}")

    col5, col6, col7, col8 = st.columns(4)
    col5.metric("Customers",        f"{kpi['total_customers']:,}")
    col6.metric("Avg Order Value",  f"${kpi['avg_order_value']:,.0f}")
    col7.metric("Avg Discount",     f"{kpi['avg_discount']}%")
    col8.metric("Avg Shipping Days",f"{kpi['avg_ship_days']} days")

    st.markdown("---")
    c1, c2 = st.columns([2, 1])
    with c1:
        st.plotly_chart(chart_monthly_sales(df), use_container_width=True)
    with c2:
        st.plotly_chart(chart_segment_sales(df), use_container_width=True)

    st.plotly_chart(chart_quarterly_growth(df), use_container_width=True)
    st.plotly_chart(chart_category_breakdown(df), use_container_width=True)


# ══════════════════════════════════════════════════════════════════════════════
# TAB 2 — PRODUCTS
# ══════════════════════════════════════════════════════════════════════════════
with tabs[1]:
    st.plotly_chart(chart_subcategory_profit(df), use_container_width=True)

    c1, c2 = st.columns(2)
    with c1:
        n = st.slider("Top N products", 5, 20, 10)
        st.plotly_chart(chart_top_products(df, n), use_container_width=True)
    with c2:
        st.plotly_chart(chart_discount_vs_profit(df), use_container_width=True)

    st.plotly_chart(chart_correlation_heatmap(df), use_container_width=True)


# ══════════════════════════════════════════════════════════════════════════════
# TAB 3 — GEOGRAPHY
# ══════════════════════════════════════════════════════════════════════════════
with tabs[2]:
    st.plotly_chart(chart_state_heatmap(df), use_container_width=True)
    st.plotly_chart(chart_region_performance(df), use_container_width=True)

    region_tbl = (
        df.groupby("Region")
        .agg(Sales=("Sales","sum"), Profit=("Profit","sum"), Orders=("Order ID","nunique"))
        .assign(**{"Margin %": lambda x: (x["Profit"]/x["Sales"]*100).round(1)})
        .sort_values("Sales", ascending=False)
        .reset_index()
    )
    region_tbl["Sales"]  = region_tbl["Sales"].map("${:,.0f}".format)
    region_tbl["Profit"] = region_tbl["Profit"].map("${:,.0f}".format)
    st.dataframe(region_tbl, use_container_width=True, hide_index=True)


# ══════════════════════════════════════════════════════════════════════════════
# TAB 4 — SHIPPING
# ══════════════════════════════════════════════════════════════════════════════
with tabs[3]:
    c1, c2 = st.columns(2)
    with c1:
        st.plotly_chart(chart_shipping_mode(df), use_container_width=True)
    with c2:
        st.plotly_chart(chart_ship_days_dist(df), use_container_width=True)

    ship_tbl = (
        df.groupby("Ship Mode")
        .agg(
            Avg_Ship_Days=("Ship Days","mean"),
            Orders=("Order ID","nunique"),
            Revenue=("Sales","sum"),
            Profit=("Profit","sum"),
        )
        .round(1)
        .sort_values("Avg_Ship_Days")
        .reset_index()
    )
    st.dataframe(ship_tbl, use_container_width=True, hide_index=True)


# ══════════════════════════════════════════════════════════════════════════════
# TAB 5 — DATA QUALITY
# ══════════════════════════════════════════════════════════════════════════════
with tabs[4]:
    st.markdown('<div class="section-title">Dataset shape</div>', unsafe_allow_html=True)
    st.write(f"**{df.shape[0]:,}** rows × **{df.shape[1]}** columns")

    st.markdown('<div class="section-title">Data types & missing values</div>', unsafe_allow_html=True)
    st.dataframe(data_quality_report(df_raw), use_container_width=True, hide_index=True)

    st.markdown('<div class="section-title">Descriptive statistics</div>', unsafe_allow_html=True)
    st.dataframe(df[["Sales","Profit","Discount","Quantity","Ship Days"]].describe().round(2),
                 use_container_width=True)

    st.markdown('<div class="section-title">Outlier check — Profit</div>', unsafe_allow_html=True)
    q1, q3 = df["Profit"].quantile([0.25, 0.75])
    iqr = q3 - q1
    outliers = df[(df["Profit"] < q1 - 1.5*iqr) | (df["Profit"] > q3 + 1.5*iqr)]
    st.write(f"**{len(outliers):,}** profit outliers detected ({len(outliers)/len(df)*100:.1f}% of data)")
    st.dataframe(
        outliers[["Order ID","Category","Sub-Category","Sales","Profit","Discount"]].head(20),
        use_container_width=True, hide_index=True
    )


# ══════════════════════════════════════════════════════════════════════════════
# TAB 6 — INSIGHTS
# ══════════════════════════════════════════════════════════════════════════════
with tabs[5]:
    ins = get_insights(df)

    st.markdown("### 5 Key business insights")

    # Insight 1
    loss_list = ", ".join(ins["loss_subcategories"].index.tolist())
    st.markdown(f"""
    <div class="warning-box">
    <strong>Insight 1 — Loss-making sub-categories</strong><br>
    {loss_list} are generating <strong>negative profit</strong>. 
    Management should review pricing or discontinue these lines.
    </div>""", unsafe_allow_html=True)

    # Insight 2
    disc_tbl = ins["discount_vs_margin"]
    flip_point = disc_tbl[disc_tbl < 0].index[0] if (disc_tbl < 0).any() else "30%+"
    st.markdown(f"""
    <div class="warning-box">
    <strong>Insight 2 — Discounts destroy margins</strong><br>
    Profit margin turns <strong>negative at {flip_point} discount</strong>. 
    High-discount orders are a net loss — the store needs a discount cap policy.
    </div>""", unsafe_allow_html=True)

    st.dataframe(disc_tbl.reset_index().rename(columns={"Discount":"Discount Band","Profit Margin":"Avg Margin %"}),
                 use_container_width=True, hide_index=True)

    # Insight 3
    best_r, best_p = ins["best_region"]
    st.markdown(f"""
    <div class="insight-box">
    <strong>Insight 3 — Most profitable region</strong><br>
    <strong>{best_r}</strong> leads with ${best_p:,.0f} in profit. 
    Marketing budget should be concentrated here for maximum ROI.
    </div>""", unsafe_allow_html=True)

    # Insight 4
    peak_m, peak_s = ins["peak_month"]
    st.markdown(f"""
    <div class="insight-box">
    <strong>Insight 4 — Peak sales month</strong><br>
    <strong>{peak_m}</strong> was the highest revenue month (${peak_s:,.0f}). 
    This suggests seasonal demand — inventory and staffing should be scaled up proactively.
    </div>""", unsafe_allow_html=True)

    # Insight 5
    fastest = ins["ship_performance"].index[0]
    fastest_days = ins["ship_performance"].iloc[0]
    st.markdown(f"""
    <div class="insight-box">
    <strong>Insight 5 — Shipping efficiency</strong><br>
    <strong>{fastest}</strong> is the fastest shipping mode at {fastest_days} days average. 
    Shifting more volume to this mode can improve customer satisfaction scores.
    </div>""", unsafe_allow_html=True)

    st.markdown("---")
    st.caption("Built by Harsh · Global Superstore EDA · Streamlit + Plotly")
