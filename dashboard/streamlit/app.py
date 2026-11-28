"""GoDesi Sales & Distribution Analytics: Streamlit dashboard.

One app, two places to run it:
- INSIDE SNOWFLAKE (Streamlit in Snowflake): reads GODESI_ANALYTICS.MARTS live with the app owner's
  role (REPORTER), using the SQL in queries.py.
- ANYWHERE ELSE (your laptop, Streamlit Community Cloud): reads the CSV files in ./marts that
  scripts/export_marts.py exported with the same SQL. No Snowflake login needed.
Run locally:  streamlit run dashboard/streamlit/app.py
Every KPI is a ratio of sums (never an average of ratios), the same rule as the dbt marts.
"""
import datetime
import decimal
import sys
from pathlib import Path

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

sys.path.insert(0, str(Path(__file__).parent))   # so queries.py is found in every runtime
from queries import QUERIES  # noqa: E402

DATA = Path(__file__).parent / "marts"
CHANNEL_COLOURS = {"offline": "#2F5D7C", "marketplace": "#E39B2D", "quick_commerce": "#6A8E3F", "d2c": "#B4451F"}
SAFFRON, GREY, INK = "#B4451F", "#9AA5B1", "#1F2933"
AMBER, BLUE, GREEN = "#E39B2D", "#2F5D7C", "#6A8E3F"
REGION_COLOURS = {"South": SAFFRON, "West": AMBER, "North": BLUE, "East": GREEN}
PALETTE = [SAFFRON, AMBER, BLUE, GREEN, "#8E5B9A", GREY]

st.set_page_config(page_title="GoDesi Sales Analytics", page_icon="🍬", layout="wide")


# Streamlit changed how charts stretch to full width (use_container_width -> width="stretch");
# Streamlit in Snowflake may run an older version, so pick the right argument.
_ST_VERSION = tuple(int(x) for x in st.__version__.split(".")[:2])
STRETCH = {"width": "stretch"} if _ST_VERSION >= (1, 50) else {"use_container_width": True}


# ------------------------------------------------------------------ data
def snowflake_session():
    """The Snowpark session when running inside Snowflake, otherwise None."""
    try:
        from snowflake.snowpark.context import get_active_session
        return get_active_session()
    except Exception:
        return None


SESSION = snowflake_session()


def normalise(df: pd.DataFrame) -> pd.DataFrame:
    """Make live Snowflake results look exactly like the CSV files: lower-case names,
    dates as 'YYYY-MM-DD' text, NUMBER as float."""
    df.columns = [c.lower() for c in df.columns]
    for c in df.columns:
        if pd.api.types.is_datetime64_any_dtype(df[c]):
            df[c] = df[c].dt.strftime("%Y-%m-%d")
        elif df[c].dtype == object:
            first = df[c].dropna().head(1)
            if len(first) and isinstance(first.iloc[0], (datetime.date, datetime.datetime)):
                df[c] = df[c].map(lambda v: v.isoformat()[:10] if v is not None else None)
            elif len(first) and isinstance(first.iloc[0], decimal.Decimal):
                df[c] = df[c].astype(float)
    return df


@st.cache_data(ttl=3600)
def load(name: str) -> pd.DataFrame:
    if SESSION is not None:                                   # inside Snowflake: live marts
        return normalise(SESSION.sql(QUERIES[name]).to_pandas())
    return pd.read_csv(DATA / f"{name}.csv")                  # anywhere else: exported files


sales = load("sales_monthly")
months = load("months")
channel_perf = load("channel_performance")
products = load("product_performance")
cohorts = load("customer_cohorts")
customers = load("customers_monthly")
promos = load("promo_impact")
inventory = load("inventory_monthly")
market = load("market_landscape")
growth = load("category_growth")

channel_perf["year"] = channel_perf["order_month"].str[:4].astype(int)
products["year"] = products["order_month"].str[:4].astype(int)


# ------------------------------------------------------------------ helpers
def inr(x: float) -> str:
    """Indian style: crore / lakh."""
    if pd.isna(x):
        return "-"
    if abs(x) >= 1e7:
        return f"₹{x / 1e7:,.2f} cr"
    if abs(x) >= 1e5:
        return f"₹{x / 1e5:,.1f} lakh"
    return f"₹{x:,.0f}"


def ratio(a: float, b: float) -> float:
    return a / b if b else float("nan")


def pct(x: float, digits: int = 1) -> str:
    return "-" if pd.isna(x) else f"{x * 100:.{digits}f}%"


def chart(fig, height=380, right=10):
    fig.update_layout(template="plotly_white", height=height, margin=dict(l=10, r=right, t=60, b=10), font_color=INK,
                      legend_title_text="", plot_bgcolor="white", paper_bgcolor="white",
                      title_font_color=INK, title_x=0.01)
    # theme=None: keep OUR colours (dark text on white cards). Streamlit's own theme would turn the text
    # white in Snowsight's dark mode, making labels invisible on the white chart background.
    st.plotly_chart(fig, theme=None, **STRETCH)


# ------------------------------------------------------------------ sidebar filters
st.sidebar.title("🍬 GoDesi")
st.sidebar.caption("Sales & Distribution Analytics")
year = st.sidebar.selectbox("Year", ["All years", 2025, 2024])
channels = st.sidebar.multiselect("Channel", list(CHANNEL_COLOURS), default=list(CHANNEL_COLOURS))
regions = st.sidebar.multiselect("Region", sorted(sales["region"].dropna().unique()),
                                 default=sorted(sales["region"].dropna().unique()))
st.sidebar.markdown("---")
st.sidebar.caption(("Live data from Snowflake MARTS. " if SESSION is not None else "Data exported from Snowflake MARTS. ") +
                   "Sales data is synthetic (portfolio project). Market data: Open Food Facts (ODbL). "
                   "Built with Snowflake + dbt.")

sel = sales[sales["channel"].isin(channels) & sales["region"].isin(regions)]
sel_year = sel if year == "All years" else sel[sel["year"] == year]


def totals(df: pd.DataFrame) -> dict:
    s = df[["net_revenue_inr", "orders", "gross_margin_inr", "gross_revenue_inr", "discount_inr"]].sum()
    return {"net": s["net_revenue_inr"], "orders": s["orders"], "aov": ratio(s["net_revenue_inr"], s["orders"]),
            "margin": ratio(s["gross_margin_inr"], s["net_revenue_inr"])}


st.title("GoDesi Sales & Distribution Analytics, 2024–2025")
tab_over, tab_prod, tab_chan, tab_cust, tab_supply, tab_about = st.tabs(
    ["Executive overview", "Products", "Channels & regions", "Customers & promotions", "Supply & market",
     "About the data"])

# ------------------------------------------------------------------ 1. overview (Q1, Q2)
with tab_over:
    now = totals(sel_year)
    if year == "All years":
        cur, prev, label = totals(sel[sel["year"] == 2025]), totals(sel[sel["year"] == 2024]), "2025 vs 2024"
    else:
        cur, prev, label = now, totals(sel[sel["year"] == year - 1]), f"{year} vs {year - 1}"
    has_prev = prev["net"] > 0

    def delta(key):
        return pct(ratio(cur[key] - prev[key], prev[key])) if has_prev else None

    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Net revenue", inr(now["net"]), delta("net"), help=f"Change: {label}. Cancelled orders excluded.")
    c2.metric("Orders", f"{now['orders']:,.0f}", delta("orders"))
    c3.metric("Average order value", inr(now["aov"]), delta("aov"), help="Net revenue / orders")
    c4.metric("Gross margin", pct(now["margin"]),
              f"{(cur['margin'] - prev['margin']) * 100:+.1f} pts" if has_prev else None,
              help="(Net revenue - COGS) / net revenue")

    left, right = st.columns([2, 1])
    with left:
        m = sel_year.groupby("year_month", as_index=False)["net_revenue_inr"].sum().merge(months, on="year_month")
        m["month type"] = m["has_major_festival"].map({True: "Major festival month", False: "Other month"})
        fig = px.bar(m, x="year_month", y="net_revenue_inr", color="month type", hover_data=["festivals"],
                     color_discrete_map={"Major festival month": SAFFRON, "Other month": GREY},
                     labels={"year_month": "", "net_revenue_inr": "Net revenue (₹)"},
                     title="Festival months drive the peaks: October–November is the high point")
        chart(fig)
    with right:
        mix = sel_year.groupby(["year", "channel"], as_index=False)["net_revenue_inr"].sum()
        mix["share"] = mix["net_revenue_inr"] / mix.groupby("year")["net_revenue_inr"].transform("sum")
        fig = px.bar(mix, x="year", y="share", color="channel", color_discrete_map=CHANNEL_COLOURS,
                     text=mix["share"].map(lambda v: f"{v:.0%}"), title="Channel mix: offline brings ~77%",
                     labels={"year": "", "share": "Share of net revenue"})
        fig.update_traces(textposition="inside", insidetextanchor="middle", textangle=0)
        fig.update_layout(uniformtext_minsize=10, uniformtext_mode="hide")
        fig.update_xaxes(type="category")
        fig.update_yaxes(tickformat=".0%", range=[0, 1])
        chart(fig)

# ------------------------------------------------------------------ 2. products (Q3)
with tab_prod:
    p = products if year == "All years" else products[products["year"] == year]
    sku = (p.groupby(["sku_id", "product_name", "category", "is_new_launch"], as_index=False)
           [["net_revenue_inr", "gross_margin_inr", "units"]].sum()
           .sort_values("net_revenue_inr", ascending=False))
    sku["rank"] = range(1, len(sku) + 1)
    sku["cumulative share"] = sku["net_revenue_inr"].cumsum() / sku["net_revenue_inr"].sum()
    top20 = sku.loc[sku["rank"] <= max(1, round(len(sku) * 0.2)), "net_revenue_inr"].sum() / sku["net_revenue_inr"].sum()
    st.markdown(f"**The top 20% of SKUs bring {top20:.0%} of net revenue.** The 10 best sellers are all Mithai.")

    left, right = st.columns(2)
    with left:
        top = sku.head(10).sort_values("net_revenue_inr")
        fig = px.bar(top, x="net_revenue_inr", y="product_name", color="category", orientation="h",
                     title="Top 10 products by net revenue",
                     labels={"net_revenue_inr": "Net revenue (₹)", "product_name": ""},
                     color_discrete_sequence=[SAFFRON, "#E39B2D", "#2F5D7C"])
        chart(fig, 420)
    with right:
        fig = go.Figure()
        fig.add_bar(x=sku["rank"], y=sku["net_revenue_inr"], name="Net revenue", marker_color=GREY,
                    hovertext=sku["product_name"])
        fig.add_scatter(x=sku["rank"], y=sku["cumulative share"], name="Cumulative share", yaxis="y2",
                        line=dict(color=SAFFRON, width=3))
        fig.update_layout(title="Pareto: how concentrated revenue is", xaxis_title="Products ranked by revenue",
                          yaxis=dict(title="Net revenue (₹)"),
                          yaxis2=dict(overlaying="y", side="right", tickformat=".0%", range=[0, 1.02]),
                          legend=dict(orientation="h", y=1.1, x=0))
        chart(fig, 420, right=50)

    cat = p.groupby("category", as_index=False)[["net_revenue_inr", "gross_margin_inr"]].sum()
    cat["gross margin %"] = cat["gross_margin_inr"] / cat["net_revenue_inr"]
    left, right = st.columns(2)
    with left:
        fig = px.bar(cat.sort_values("net_revenue_inr"), x="net_revenue_inr", y="category", orientation="h",
                     text=cat.sort_values("net_revenue_inr")["gross margin %"].map(lambda v: f"margin {v:.1%}"),
                     title="Revenue and margin by category", color_discrete_sequence=[SAFFRON],
                     labels={"net_revenue_inr": "Net revenue (₹)", "category": ""})
        chart(fig, 320)
    with right:
        nl = p.groupby(["order_month", "is_new_launch"], as_index=False)["net_revenue_inr"].sum()
        nl["product age"] = nl["is_new_launch"].map({True: "Launched 2024 or later", False: "Older products"})
        fig = px.bar(nl, x="order_month", y="net_revenue_inr", color="product age",
                     color_discrete_map={"Launched 2024 or later": SAFFRON, "Older products": GREY},
                     title="Are new launches adding growth?", labels={"order_month": "", "net_revenue_inr": "Net revenue (₹)"})
        chart(fig, 320)

# ------------------------------------------------------------------ 3. channels and regions (Q2, Q4)
with tab_chan:
    cp = channel_perf[channel_perf["channel"].isin(channels)]
    cp = cp if year == "All years" else cp[cp["year"] == year]
    ch = cp.groupby("channel", as_index=False)[["net_revenue_inr", "gross_revenue_inr", "discount_inr",
                                                "gross_margin_inr", "orders", "order_lines", "returned_lines"]].sum()
    ch = ch.sort_values("net_revenue_inr", ascending=False)
    table = pd.DataFrame({
        "Channel": ch["channel"],
        "Net revenue": ch["net_revenue_inr"].map(inr),
        "Share": (ch["net_revenue_inr"] / ch["net_revenue_inr"].sum()).map(pct),
        "Gross margin": (ch["gross_margin_inr"] / ch["net_revenue_inr"]).map(pct),
        "Discount": (ch["discount_inr"] / ch["gross_revenue_inr"]).map(lambda v: pct(v, 2)),
        "Return rate": [("not tracked" if c == "offline" else pct(r / n, 2))
                        for c, r, n in zip(ch["channel"], ch["returned_lines"], ch["order_lines"])],
        "AOV": (ch["net_revenue_inr"] / ch["orders"]).map(inr),
    })
    st.subheader("Channel trade-off: offline brings the volume, online brings the margin")
    st.dataframe(table.set_index("Channel"), **STRETCH)        # set_index instead of hide_index: works on old Streamlit
    st.caption("Returns are only recorded for online orders; offline (shops and distributors) has no promo discounts.")

    left, right = st.columns(2)
    yoy = sel.pivot_table(index="region", columns="year", values="net_revenue_inr", aggfunc="sum").reset_index()
    if {2024, 2025} <= set(yoy.columns):
        yoy["growth"] = yoy[2025] / yoy[2024] - 1
        with left:
            r = yoy.sort_values("growth")
            fig = px.bar(r, x="growth", y="region", orientation="h", text=r["growth"].map(lambda v: f"{v:+.0%}"),
                         title="Revenue growth by region, 2025 vs 2024", color="region",
                         color_discrete_map=REGION_COLOURS, labels={"growth": "", "region": ""})
            fig.update_layout(showlegend=False)
            fig.update_traces(textposition="outside", cliponaxis=False, textfont_color=INK)
            fig.update_xaxes(range=[0, r["growth"].max() * 1.2])
            fig.update_yaxes(categoryorder="total ascending")
            fig.update_xaxes(tickformat=".0%")
            chart(fig, 320)
        with right:
            cy = sel.pivot_table(index=["region", "city"], columns="year", values="net_revenue_inr",
                                 aggfunc="sum").reset_index().fillna(0)
            big = cy[cy[2024] >= 10e5].copy()                      # at least ₹10 lakh in 2024: no tiny bases
            big["growth"] = big[2025] / big[2024] - 1
            big = big.sort_values("growth").tail(10)
            fig = px.bar(big, x="growth", y="city", color="region", orientation="h",
                         text=big["growth"].map(lambda v: f"{v:+.0%}"), color_discrete_map=REGION_COLOURS,
                         title="Fastest-growing cities (2024 revenue ≥ ₹10 lakh)", labels={"growth": "", "city": ""})
            fig.update_traces(textposition="outside", cliponaxis=False, textfont_size=11)
            fig.update_xaxes(tickformat=".0%", range=[0, big["growth"].max() * 1.2])
            fig.update_yaxes(categoryorder="total ascending")
            chart(fig, 320)
    st.caption("Cities with a very small 2024 base are left out of the growth ranking: +400% on ₹5 lakh is not "
               "a trend.")

# ------------------------------------------------------------------ 4. customers and promotions (Q5, Q7)
with tab_cust:
    last = cohorts["cohort_month"].max()
    c = cohorts.copy()
    c["end"] = pd.to_datetime(c["cohort_month"]) + c["months_since_first_order"].map(lambda n: pd.DateOffset(months=int(n)))
    c = c[c["end"] <= pd.to_datetime(last)]                         # only cohorts old enough for that month
    curve = c.groupby("months_since_first_order").agg(
        active=("active_customers", "sum"), size=("cohort_customers", "sum"),
        revenue=("cumulative_revenue_per_customer", lambda s: (s * c.loc[s.index, "cohort_customers"]).sum()))
    curve["retention"] = curve["active"] / curve["size"]
    curve["ltv"] = curve["revenue"] / curve["size"]

    k1, k2, k3 = st.columns(3)
    k1.metric("Retention after 1 month", pct(curve.loc[1, "retention"]))
    k2.metric("Retention after 12 months", pct(curve.loc[12, "retention"]))
    k3.metric("12-month value per customer", inr(curve.loc[12, "ltv"]))
    m1 = c[c["months_since_first_order"] == 1].assign(y=lambda d: d["cohort_month"].str[:4]).groupby("y")[
        ["active_customers", "cohort_customers"]].sum()
    m1 = (m1["active_customers"] / m1["cohort_customers"]).to_dict()
    st.caption("Weighted over all cohorts: total active customers / total cohort customers (bigger cohorts count more).")
    if {"2024", "2025"} <= set(m1):
        st.info(f"**The average hides a trend:** month-1 retention is **{m1['2024']:.1%}** for customers who started in "
                f"2024 but only **{m1['2025']:.1%}** for 2025 starters. The data begins in January 2024, so the early "
                "cohorts include customers who were already buying in 2023 (left-censoring). For a new customer today, "
                "plan with about 12-15%.")

    left, right = st.columns([3, 2])
    with left:
        heat = cohorts[cohorts["months_since_first_order"].between(1, 12)].pivot(   # month 0 is always 100%
            index="cohort_month", columns="months_since_first_order", values="retention_pct")
        heat.index = heat.index.str[:7]
        fig = px.imshow(heat, color_continuous_scale=["#FFFFFF", AMBER, SAFFRON], aspect="auto", text_auto=".0f",
                        labels=dict(x="", y="", color="Retention %"),
                        title="Cohort retention % by months since first order (1-12): newer cohorts come back less")
        fig.update_traces(textfont_size=9)
        fig.update_xaxes(showgrid=False, dtick=1, side="top", type="category")
        fig.update_yaxes(showgrid=False, type="category", tickfont_size=10, title="first-order month")
        chart(fig, 560)
    with right:
        fig = px.line(curve.reset_index(), x="months_since_first_order", y="ltv", markers=True,
                      title="Value per customer over time (LTV curve)", color_discrete_sequence=[SAFFRON],
                      labels={"months_since_first_order": "Months since first order", "ltv": "Cumulative ₹ per customer"})
        chart(fig, 560)

    left, right = st.columns(2)
    with left:
        cu = customers if year == "All years" else customers[customers["year_month"].str[:4] == str(year)]
        fig = px.bar(cu, x="year_month", y="net_revenue_inr", color="customer_type",
                     color_discrete_map={"new": GREY, "returning": SAFFRON},
                     title="Online revenue: new vs returning customers",
                     labels={"year_month": "", "net_revenue_inr": "Net revenue (₹)", "customer_type": ""})
        chart(fig, 360)
    with right:
        pr = promos[~promos["has_no_full_before_period"]].sort_values("revenue_uplift_pct").copy()
        pr["result"] = (pr["revenue_uplift_pct"] >= 0).map({True: "Lifted revenue", False: "Lost revenue"})
        fig = px.bar(pr, x="revenue_uplift_pct", y="promo_code", orientation="h", color="result",
                     color_discrete_map={"Lifted revenue": GREEN, "Lost revenue": SAFFRON},
                     text=pr["revenue_uplift_pct"].map(lambda v: f"{v:+.0f}%"),
                     hover_data={"discount_pct": True, "discount_given_inr": ":,.0f", "orders_with_code": True},
                     title="Promo uplift: daily revenue vs the 28 days before",
                     labels={"revenue_uplift_pct": "Uplift %", "promo_code": "", "result": ""})
        fig.update_traces(textposition="outside", cliponaxis=False, textfont_size=10)
        lo, hi = pr["revenue_uplift_pct"].min(), pr["revenue_uplift_pct"].max()
        fig.update_xaxes(range=[min(lo, 0) - 25, hi + 25], ticksuffix="%")
        fig.update_yaxes(dtick=1, tickfont_size=10, categoryorder="total ascending")
        fig.update_layout(legend=dict(orientation="h", y=1.06, x=0))
        chart(fig, 600)

# ------------------------------------------------------------------ 5. supply and market (Q6, Q8, Q9)
with tab_supply:
    left, right = st.columns(2)
    with left:
        inv = inventory.merge(months[["year_month", "has_major_festival"]], on="year_month", how="left")
        fig = go.Figure()
        fig.add_bar(x=inv["year_month"], y=inv["stockout_warehouse_sku_days"], name="Stock-out days (rust = festival month)",
                    marker_color=[SAFFRON if f else AMBER for f in inv["has_major_festival"].fillna(False)])
        fig.add_scatter(x=inventory["year_month"], y=inventory["avg_network_days_of_cover"], name="Days of cover",
                        yaxis="y2", line=dict(color="#2F5D7C", width=3))
        fig.update_layout(title="Stock-outs peak in October 2025, right before Diwali",
                          yaxis=dict(title="Warehouse-SKU days at zero stock"),
                          yaxis2=dict(title="Average days of cover", overlaying="y", side="right"),
                          legend=dict(orientation="h", y=1.1, x=0))
        chart(fig, 400, right=60)
    with right:
        segs = sorted(market.loc[market["is_godesi"], "market_segment"].unique())
        seg = st.selectbox("Market segment (Open Food Facts India)", segs, key="segment",
                           index=segs.index("Sweets & mithai") if "Sweets & mithai" in segs else 0)
        ms = market[market["market_segment"] == seg]
        cut = max(10, int(ms.loc[ms["is_godesi"], "brand_rank_in_segment"].max()))        # down to GoDesi, ties included
        show = ms[ms["brand_rank_in_segment"] <= cut]
        show = show.sort_values("products")
        fig = px.bar(show, x="products", y="brand", orientation="h",
                     color=show["is_godesi"].map({True: "GoDesi", False: "Other brands"}),
                     color_discrete_map={"GoDesi": SAFFRON, "Other brands": BLUE},
                     title=f"{seg}: brands by number of products listed",
                     labels={"products": "Products in Open Food Facts India", "brand": "", "color": ""})
        fig.update_yaxes(categoryorder="total ascending")
        chart(fig, 400)
        g = ms[ms["is_godesi"]].iloc[0]
        st.caption(f"GoDesi: rank {int(g['brand_rank_in_segment'])} of {int(g['segment_brands'])} brands, median "
                   f"sugar {g['median_sugars_100g']} g per 100 g."
                   + (" The segment mixes all sweet foods (chocolate, honey, jams), not only mithai."
                      if seg == "Sweets & mithai" else ""))

    full = growth[growth["listed_year"].between(2019, growth["listed_year"].max() - 1)   # drop the partial year
                  & (growth["market_segment"] != "Uncategorised")]                         # no category in OFF
    top_segs = full.groupby("market_segment")["new_products"].sum().nlargest(6).index
    fig = px.line(full[full["market_segment"].isin(top_segs)], x="listed_year", y="new_products",
                  color="market_segment", markers=True, color_discrete_sequence=PALETTE,
                  title="New products listed per year in the largest segments (full years, categorised only)",
                  labels={"listed_year": "", "new_products": "New products", "market_segment": ""})
    chart(fig, 380)

# ------------------------------------------------------------------ 6. about
with tab_about:
    st.markdown("""
### How this dashboard is built
- **Snowflake** holds the raw data; **dbt** cleans, models and tests it (144 data tests + 1 unit test on every build).
- The dashboard reads the **MARTS** layer only, exported to small CSV files by `scripts/export_marts.py`.
- KPIs are always a **ratio of sums**: AOV = net revenue / orders, margin % = gross margin / net revenue.

### Definitions
| KPI | Definition |
|---|---|
| Net revenue | gross revenue (quantity x price charged) - promo discount; cancelled orders excluded |
| Gross margin % | (net revenue - cost of goods) / net revenue |
| AOV | net revenue / number of orders |
| Retention (month N) | customers of a cohort who ordered in month N / customers in the cohort |
| Promo uplift | average daily revenue during the promo vs the 28 days before |

### Limitations
- Sales, customer and inventory data are **synthetic** (generated with a fixed seed); only the 9 GoDesi products
  found in Open Food Facts are real.
- Open Food Facts is crowd-sourced: 64% of products have no category, and the newest year is partial.
- Two ERP price records are wrong at the source (known data-quality warning, revenue not affected).
""")
