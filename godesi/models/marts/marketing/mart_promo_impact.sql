-- Q7 (stretch): do promotions lift sales?
-- Grain: one row per promo_code.
-- Compares average daily net revenue in the channels a promo applies to:
--   during the promo window  vs  the 28 days before it started.
-- Always-on promos (WELCOME10, FREESHIP) have no "before" period inside the data.

with promos as (

    select * from {{ ref('stg_erp__promotions') }}

),

daily as (

    -- online revenue per day and channel (promos only apply to online orders)
    select order_date, channel, sum(net_revenue_inr) as net_revenue_inr
    from {{ ref('fct_order_items') }}
    where not is_cancelled
      and channel in ('d2c', 'marketplace', 'quick_commerce')
    group by order_date, channel

),

promo_days as (

    select
        p.promo_code,
        p.promo_name,
        p.promo_channel,
        p.discount_pct,
        p.start_date,
        p.end_date,
        sum(iff(d.order_date between p.start_date and p.end_date, d.net_revenue_inr, 0))
            / (datediff(day, p.start_date, p.end_date) + 1)                    as avg_daily_revenue_during,
        sum(iff(d.order_date between dateadd(day, -28, p.start_date) and dateadd(day, -1, p.start_date),
                d.net_revenue_inr, 0)) / 28                                    as avg_daily_revenue_before
    from promos as p
    left join daily as d
        on (p.promo_channel = 'all' or p.promo_channel = d.channel)
        and d.order_date between dateadd(day, -28, p.start_date) and p.end_date
    group by all

),

redemptions as (

    select promo_code, count(distinct order_id) as orders_with_code, sum(discount_inr) as discount_given_inr
    from {{ ref('fct_order_items') }}
    where promo_code is not null and not is_cancelled
    group by promo_code

)

select
    p.*,
    round({{ safe_divide('p.avg_daily_revenue_during - p.avg_daily_revenue_before',
                       'p.avg_daily_revenue_before') }} * 100, 1)       as revenue_uplift_pct,
    coalesce(r.orders_with_code, 0)                               as orders_with_code,
    coalesce(r.discount_given_inr, 0)                             as discount_given_inr,
    p.start_date <= '2024-01-28'                                  as has_no_full_before_period
from promo_days as p
left join redemptions as r
    on p.promo_code = r.promo_code
