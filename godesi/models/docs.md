{% docs __overview__ %}
# GoDesi Sales & Distribution Analytics

An end-to-end analytics project for **GoDesi** (Bengaluru, Indian sweets and snacks), built with
**Snowflake + dbt**. It answers nine business questions (Q1-Q9) about revenue growth, channels,
products, regions, customers, promotions, inventory and the competitive market.

**Data**
- Four operational systems (synthetic, realistic and deliberately messy): ERP, D2C website,
  marketplaces / quick commerce, and warehouse inventory. 80,000 orders, 2024-2025.
- Real market data: 26,293 products sold in India from Open Food Facts (ODbL licence).

**Layers**
| Layer | Schema | What it does |
|---|---|---|
| Staging | STAGING | one model per source table: rename, cast, clean, dedupe (views) |
| Intermediate | INTERMEDIATE | union the three order systems, SCD2 price join, returns (views) |
| Marts | MARTS | star schema (facts + dimensions) and dashboard-ready marts (tables) |

**Quality**: every model has primary-key tests; foreign keys, accepted values, business rules,
5 singular tests, a unit test and source freshness run on every build.

Use the lineage graph (bottom-right button) to follow any number back to its raw source.
{% enddocs %}


{% docs gross_revenue_inr %}
**Gross revenue (INR)** = quantity x unit price actually charged, before promo discounts.
Includes cancelled orders unless the model says otherwise; filter `is_cancelled = false` for sales KPIs.
{% enddocs %}

{% docs discount_inr %}
**Discount (INR)** = promo-code discount given on the line or order. Never larger than gross revenue
(tested with `dbt_utils.expression_is_true`).
{% enddocs %}

{% docs net_revenue_inr %}
**Net revenue (INR)** = gross revenue - discount. **The main revenue KPI of the project.**
Sales KPIs exclude cancelled orders. Total for 2024-2025 (not cancelled): INR 18,76,44,075.
Reconciled across fct_order_items, fct_orders and mart_sales_daily by the singular test
`assert_revenue_reconciles`.
{% enddocs %}

{% docs cogs_inr %}
**COGS (INR)** = quantity x product cost valid at the time of the order (SCD2 price history).
{% enddocs %}

{% docs gross_margin_inr %}
**Gross margin (INR)** = net revenue - COGS.
{% enddocs %}

{% docs gross_margin_pct %}
**Gross margin %** = gross margin / net revenue x 100. A ratio: never sum or average it across rows;
recalculate it from the summed amounts.
{% enddocs %}

{% docs refund_inr %}
**Refund (INR)** = money paid back for returned lines (0 when not returned). Never larger than the
amount paid for the line (singular test `assert_refund_not_above_line_revenue`).
{% enddocs %}

{% docs net_revenue_after_returns_inr %}
**Net revenue after returns (INR)** = net revenue - refund.
{% enddocs %}

{% docs aov_inr %}
**Average order value (INR)** = net revenue / number of orders. A ratio: recalculate from totals
instead of averaging it.
{% enddocs %}

{% docs retention_pct %}
**Retention %** = customers of a cohort who ordered in month N / customers in the cohort x 100.
Month 0 is always 100%.
{% enddocs %}

{% docs cohort_month %}
**Cohort month** = the month of the customer's FIRST (not cancelled) order. Not the signup month.
{% enddocs %}

{% docs network_days_of_cover %}
**Days of cover** = stock in all warehouses / average units sold per day over the last 28 days.
Below about 7 days means a stock-out risk; very high values mean overstock (Q6).
{% enddocs %}

{% docs revenue_uplift_pct %}
**Revenue uplift %** = (average daily net revenue during the promo - average daily net revenue in the
28 days before) / the before value x 100.
{% enddocs %}

{% docs channel %}
**Channel**: offline (kirana / modern trade through distributors), d2c (godesi.in), marketplace
(Amazon, Flipkart) or quick_commerce (Blinkit, Zepto, Instamart).
{% enddocs %}

{% docs platform %}
**Platform**: where the order was placed (e.g. amazon, blinkit, godesi.in, distributor). Joins to dim_channel.
{% enddocs %}

{% docs is_cancelled %}
**Is cancelled**: true when the latest order status is cancelled. Sales KPIs exclude these orders.
{% enddocs %}

{% docs is_festival_window %}
**Festival window**: the 10 days before a festival plus the festival day (festival_calendar seed),
when sweet sales rise.
{% enddocs %}

{% docs market_segment %}
**Market segment**: Open Food Facts products grouped for comparison with GoDesi
(e.g. Sweets & mithai, Salty snacks, Drinks). Drinks are matched first so "sweetened beverages"
are not counted as sweets.
{% enddocs %}
