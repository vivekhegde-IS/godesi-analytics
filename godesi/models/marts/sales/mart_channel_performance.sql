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
    round({{ safe_divide('net_revenue_inr', 'orders') }}, 2)                                       as aov_inr,
    round({{ safe_divide('discount_inr', 'gross_revenue_inr') }} * 100, 2)                        as discount_pct,
    round({{ safe_divide('gross_margin_inr', 'net_revenue_inr') }} * 100, 1)                      as gross_margin_pct,
    round({{ safe_divide('returned_lines', 'order_lines') }} * 100, 2)                            as return_rate_pct
from monthly
