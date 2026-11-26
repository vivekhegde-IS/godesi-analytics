-- Brands in the Indian packaged-food market (real data, cleaned with the brand_mapping seed).
-- Grain: one row per brand. Products with no brand are excluded.

with products as (

    select * from {{ ref('dim_market_products') }}
    where brand is not null

),

main_segment as (

    -- the segment where each brand has the most products
    select brand, market_segment
    from products
    group by brand, market_segment
    qualify row_number() over (partition by brand order by count(*) desc, market_segment) = 1

)

select
    p.brand,
    boolor_agg(p.is_godesi)                                          as is_godesi,
    not boolor_agg(p.is_godesi)                                      as is_competitor,
    m.market_segment                                                 as main_segment,
    count(*)                                                         as product_count,
    count(distinct p.market_segment)                                 as segment_count,
    round(median(p.sugars_100g), 1)                                  as median_sugars_100g,
    count_if(p.nutriscore_grade in ('A', 'B'))                       as nutriscore_ab_products,
    count_if(p.nutriscore_grade in ('D', 'E'))                       as nutriscore_de_products,
    min(p.listed_year)                                               as first_listed_year
from products as p
inner join main_segment as m
    on p.brand = m.brand
group by p.brand, m.market_segment
