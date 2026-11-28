-- Q1: How are revenue, orders and AOV trending? (yearly, with YoY growth)
-- Cancelled orders excluded (mart_sales_daily already excludes them).
-- Ratios are computed from summed amounts, never averaged.

with yearly as (

    select
        year,
        sum(net_revenue_inr)                   as net_revenue_inr,
        sum(gross_margin_inr)                  as gross_margin_inr,
        sum(orders)                            as orders,          -- safe: an order has one day, platform and city
        sum(units)                             as units
    from {{ ref('mart_sales_daily') }}
    group by year

)

select
    year,
    round(net_revenue_inr / 1e7, 2)                                        as net_revenue_crore,
    orders,
    units,
    round({{ safe_divide('net_revenue_inr', 'orders') }}, 0)               as aov_inr,
    round({{ safe_divide('gross_margin_inr', 'net_revenue_inr') }} * 100, 1) as gross_margin_pct,
    round({{ safe_divide('net_revenue_inr - lag(net_revenue_inr) over (order by year)',
                         'lag(net_revenue_inr) over (order by year)') }} * 100, 1) as revenue_yoy_pct,
    round({{ safe_divide('orders - lag(orders) over (order by year)',
                         'lag(orders) over (order by year)') }} * 100, 1)  as orders_yoy_pct
from yearly
order by year
