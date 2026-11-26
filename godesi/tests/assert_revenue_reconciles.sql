{{ config(store_failures=true) }}

-- Net revenue (cancelled orders excluded) must be the same in the line fact, the order
-- fact and the daily sales mart. If a join fans out or drops rows, the totals split and
-- the dashboard shows different revenue on different pages.
-- Returns one row (the three totals) only when they differ by more than 1 rupee.

with totals as (

    select
        (select sum(net_revenue_inr) from {{ ref('fct_order_items') }} where not is_cancelled) as line_fact_inr,
        (select sum(net_revenue_inr) from {{ ref('fct_orders') }}      where not is_cancelled) as order_fact_inr,
        (select sum(net_revenue_inr) from {{ ref('mart_sales_daily') }})                       as sales_mart_inr

)

select *
from totals
where abs(line_fact_inr - order_fact_inr) > 1
   or abs(line_fact_inr - sales_mart_inr) > 1
