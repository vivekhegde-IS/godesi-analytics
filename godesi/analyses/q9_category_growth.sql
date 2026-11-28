-- Q9: Is the market growing? New products listed per segment per year (Open Food Facts), 2019 onwards.
-- The newest year is still in progress (the data is a 2026 snapshot), so it is flagged and must not be
-- compared with full years.

select
    market_segment,
    listed_year,
    new_products,
    brands_listing,
    cumulative_products,
    round({{ safe_divide('new_products - lag(new_products) over (partition by market_segment order by listed_year)',
                         'lag(new_products) over (partition by market_segment order by listed_year)') }} * 100, 0)
                                                                                 as new_products_yoy_pct,
    listed_year = max(listed_year) over ()                                       as is_partial_year
from {{ ref('mart_category_growth') }}
where listed_year >= 2019
order by market_segment, listed_year
