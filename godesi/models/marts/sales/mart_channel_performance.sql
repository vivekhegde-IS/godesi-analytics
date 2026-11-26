-- Q3: which channel performs best, and what does each cost us?
-- Grain: one row per month and channel. Cancelled orders excluded.

with lines as (

    select * from {{ ref('fct_order_items') }}
    where not is_cancelled

),

monthly as (

    select
        date_trunc('month', order_date)            as order_month,
        channel,
        count(distinct order_id)                   as orders,
        count(*)                                   as order_lines,
        sum(quantity)                              as units,
        sum(gross_revenue_inr)                     as gross_revenue_inr,
        sum(discount_inr)                          as discount_inr,
        sum(net_revenue_inr)                       as net_revenue_inr,
        sum(gross_margin_inr)                      as gross_margin_inr,
        count_if(is_returned)                      as returned_lines,
        sum(refund_inr)                            as refund_inr
    from lines
    group by all

)

select
    *,
    round(net_revenue_inr / sum(net_revenue_inr) over (partition by order_month) * 100, 1) as revenue_share_pct,
    round(net_revenue_inr / nullif(orders, 0), 2)                                       as aov_inr,
    round(discount_inr / nullif(gross_revenue_inr, 0) * 100, 2)                        as discount_pct,
    round(gross_margin_inr / nullif(net_revenue_inr, 0) * 100, 1)                      as gross_margin_pct,
    round(returned_lines / nullif(order_lines, 0) * 100, 2)                            as return_rate_pct
from monthly
