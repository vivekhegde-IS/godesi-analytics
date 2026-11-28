"""The SQL behind every dataset of the dashboard, in ONE place.

Used twice:
- inside Snowflake (Streamlit in Snowflake), the app runs these queries live on the marts;
- outside Snowflake, scripts/export_marts.py runs them once and saves CSV files the app reads.
Only aggregated mart data: no customer names, e-mails or pincodes.
"""

M = "GODESI_ANALYTICS.MARTS"

QUERIES = {
    # monthly sales by channel, platform and place (Q1, Q2, Q4). Orders can be summed: an order has one
    # day, platform and city.
    "sales_monthly": f"""
        select year, year_month, channel, platform, region, state, city,
               sum(orders) as orders, sum(units) as units,
               sum(gross_revenue_inr) as gross_revenue_inr, sum(discount_inr) as discount_inr,
               sum(net_revenue_inr) as net_revenue_inr, sum(cogs_inr) as cogs_inr,
               sum(gross_margin_inr) as gross_margin_inr, sum(refund_inr) as refund_inr
        from {M}.MART_SALES_DAILY
        group by all
        order by year_month, channel, platform, region, state, city""",
    # one row per month: does it contain a major festival window, and which festivals
    "months": f"""
        select year_month,
               boolor_agg(is_major_festival_window) as has_major_festival,
               listagg(distinct festival_name, ', ') within group (order by festival_name) as festivals
        from {M}.DIM_DATE
        group by year_month
        order by year_month""",
    "channel_performance": f"select * from {M}.MART_CHANNEL_PERFORMANCE order by order_month, channel",
    "product_performance": f"select * from {M}.MART_PRODUCT_PERFORMANCE order by order_month, sku_id",
    "customer_cohorts": f"select * from {M}.MART_CUSTOMER_COHORTS order by cohort_month, months_since_first_order",
    # new vs returning revenue from online customers (Q5)
    "customers_monthly": f"""
        select to_char(order_date, 'YYYY-MM') as year_month,
               iff(is_first_order, 'new', 'returning') as customer_type,
               count(*) as orders, sum(net_revenue_inr) as net_revenue_inr
        from {M}.FCT_ORDERS
        where not is_cancelled and customer_id is not null
        group by all
        order by 1, 2""",
    "promo_impact": f"select * from {M}.MART_PROMO_IMPACT order by start_date, promo_code",
    # stock-outs and cover per month (Q6)
    "inventory_monthly": f"""
        select to_char(snapshot_date, 'YYYY-MM') as year_month,
               count_if(is_stockout) as stockout_warehouse_sku_days,
               count(distinct iff(is_stockout, sku_id, null)) as skus_with_stockout,
               round(avg(network_days_of_cover), 1) as avg_network_days_of_cover
        from {M}.FCT_INVENTORY_DAILY
        group by 1
        order by 1""",
    "market_landscape": f"select * from {M}.MART_MARKET_LANDSCAPE order by market_segment, brand_rank_in_segment, brand",
    "category_growth": f"select * from {M}.MART_CATEGORY_GROWTH order by market_segment, listed_year",
}
