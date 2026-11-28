-- Q8: How does GoDesi compare with competitors? Top 10 brands in each segment where GoDesi sells,
-- plus GoDesi itself, with product count, rank, sugar and Nutri-Score D/E share (real Open Food Facts data).

with godesi_segments as (

    select distinct market_segment
    from {{ ref('mart_market_landscape') }}
    where is_godesi

)

select
    l.market_segment,
    l.brand_rank_in_segment,
    l.brand,
    l.is_godesi,
    l.products,
    l.segment_brands,
    l.share_of_segment_pct,
    l.median_sugars_100g,
    round({{ safe_divide('l.nutriscore_d + l.nutriscore_e',
                         'l.products - l.nutriscore_unknown') }} * 100, 0)       as nutriscore_de_pct_of_graded
from {{ ref('mart_market_landscape') }} as l
inner join godesi_segments as g
    on l.market_segment = g.market_segment
where l.brand_rank_in_segment <= 10 or l.is_godesi
order by l.market_segment, l.brand_rank_in_segment
