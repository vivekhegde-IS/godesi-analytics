-- Q7: Do promotions lift revenue, and what do they cost?
-- Promos without 28 full days of history before them are excluded from the uplift ranking.

select
    promo_code,
    promo_name,
    promo_channel,
    discount_pct,
    start_date,
    end_date,
    round(avg_daily_revenue_before, 0)                                           as avg_daily_revenue_before_inr,
    round(avg_daily_revenue_during, 0)                                           as avg_daily_revenue_during_inr,
    revenue_uplift_pct,
    orders_with_code,
    round(discount_given_inr, 0)                                                 as discount_given_inr
from {{ ref('mart_promo_impact') }}
where not has_no_full_before_period
order by revenue_uplift_pct desc
