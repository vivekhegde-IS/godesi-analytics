-- Q4: Which regions and cities grow fastest? 2025 vs 2024.
-- GROUPING SETS returns region totals and cities in one result (level = 'region' or 'city').

with yearly as (

    select
        region,
        city,
        sum(iff(year = 2024, net_revenue_inr, 0))  as net_revenue_2024,
        sum(iff(year = 2025, net_revenue_inr, 0))  as net_revenue_2025
    from {{ ref('mart_sales_daily') }}
    group by grouping sets ((region), (region, city))

)

select
    iff(city is null, 'region', 'city')                                          as level,
    region,
    city,
    round(net_revenue_2024 / 1e5, 1)                                             as net_revenue_2024_lakh,
    round(net_revenue_2025 / 1e5, 1)                                             as net_revenue_2025_lakh,
    round({{ safe_divide('net_revenue_2025 - net_revenue_2024', 'net_revenue_2024') }} * 100, 1) as revenue_yoy_pct
from yearly
order by level desc, revenue_yoy_pct desc
