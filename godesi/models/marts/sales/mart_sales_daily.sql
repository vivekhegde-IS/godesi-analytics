-- Q1 and Q4: revenue and orders over time, by channel and place.
-- Grain: one row per order_date, channel, platform and state/city. Cancelled orders excluded.
-- Ratios (AOV, margin %) are NOT stored here: averages cannot be summed, so the dashboard
-- calculates them from the totals (AOV = net revenue / orders) at any level it shows.

with lines as (

    select * from {{ ref('fct_order_items') }}
    where not is_cancelled

),

dates as (

    select date_day, year, month, year_month, is_weekend, is_festival_window, festival_window_name
    from {{ ref('dim_date') }}

),

geo as (

    select city, region from {{ ref('dim_geography') }}

)

select
    l.order_date,
    d.year,
    d.month,
    d.year_month,
    d.is_weekend,
    d.is_festival_window,
    d.festival_window_name,
    l.channel,
    l.platform,
    g.region,
    l.state,
    l.city,
    count(distinct l.order_id)                    as orders,
    sum(l.quantity)                               as units,
    sum(l.gross_revenue_inr)                      as gross_revenue_inr,
    sum(l.discount_inr)                           as discount_inr,
    sum(l.net_revenue_inr)                        as net_revenue_inr,
    sum(l.cogs_inr)                               as cogs_inr,
    sum(l.gross_margin_inr)                       as gross_margin_inr,
    sum(l.refund_inr)                             as refund_inr
from lines as l
left join dates as d
    on l.order_date = d.date_day
left join geo as g
    on l.city = g.city
group by all
