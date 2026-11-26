-- Q9 (real data): new products listed per segment per year (all products, with or without brand).
-- Grain: one row per market_segment and listed_year.

select
    market_segment,
    listed_year,
    count(*)                                                as new_products,
    count(distinct brand)                                   as brands_listing,
    sum(count(*)) over (partition by market_segment order by listed_year) as cumulative_products
from {{ ref('dim_market_products') }}
group by market_segment, listed_year
