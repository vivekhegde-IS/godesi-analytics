-- Q8 and Q9 (real data): how crowded is each segment, and how does GoDesi compare?
-- Grain: one row per market_segment and brand (brands with no name excluded).
-- Segment-level columns (same value on every row of a segment) show crowding.

with products as (

    select * from {{ ref('dim_market_products') }}
    where brand is not null

),

brand_segment as (

    select
        market_segment,
        brand,
        boolor_agg(is_godesi)                                 as is_godesi,
        count(*)                                              as products,
        round(median(sugars_100g), 1)                         as median_sugars_100g,
        median(net_quantity)                                  as median_pack_size,
        count_if(nutriscore_grade = 'A')                      as nutriscore_a,
        count_if(nutriscore_grade = 'B')                      as nutriscore_b,
        count_if(nutriscore_grade = 'C')                      as nutriscore_c,
        count_if(nutriscore_grade = 'D')                      as nutriscore_d,
        count_if(nutriscore_grade = 'E')                      as nutriscore_e,
        count_if(nutriscore_grade is null)                    as nutriscore_unknown
    from products
    group by market_segment, brand

)

select
    *,
    sum(products) over (partition by market_segment)                       as segment_products,
    count(*) over (partition by market_segment)                            as segment_brands,
    round(products / sum(products) over (partition by market_segment) * 100, 2) as share_of_segment_pct,
    rank() over (partition by market_segment order by products desc)       as brand_rank_in_segment
from brand_segment
