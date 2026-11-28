-- Q2: How does the channel mix compare? Share, margin, discount, returns, AOV and growth per channel.

with by_channel as (

    select
        channel,
        sum(net_revenue_inr)                                           as net_revenue_inr,
        sum(iff(year(order_month) = 2024, net_revenue_inr, 0))         as net_revenue_2024,
        sum(iff(year(order_month) = 2025, net_revenue_inr, 0))         as net_revenue_2025,
        sum(gross_revenue_inr)                                         as gross_revenue_inr,
        sum(discount_inr)                                              as discount_inr,
        sum(gross_margin_inr)                                          as gross_margin_inr,
        sum(orders)                                                    as orders,
        sum(order_lines)                                               as order_lines,
        sum(returned_lines)                                            as returned_lines
    from {{ ref('mart_channel_performance') }}
    group by channel

)

select
    channel,
    round(net_revenue_inr / 1e7, 2)                                              as net_revenue_crore,
    round(net_revenue_inr / sum(net_revenue_inr) over () * 100, 1)               as revenue_share_pct,
    round({{ safe_divide('gross_margin_inr', 'net_revenue_inr') }} * 100, 1)     as gross_margin_pct,
    round({{ safe_divide('discount_inr', 'gross_revenue_inr') }} * 100, 2)       as discount_pct,
    round({{ safe_divide('returned_lines', 'order_lines') }} * 100, 2)           as return_rate_pct,
    round({{ safe_divide('net_revenue_inr', 'orders') }}, 0)                     as aov_inr,
    round({{ safe_divide('net_revenue_2025 - net_revenue_2024', 'net_revenue_2024') }} * 100, 1) as revenue_yoy_pct
from by_channel
order by net_revenue_inr desc
