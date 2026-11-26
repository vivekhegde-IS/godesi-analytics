-- All real packaged-food products sold in India (Open Food Facts).
-- Grain: one row per barcode (26,293).
-- market_segment groups products so GoDesi can be compared with its real competitors.
-- GoDesi's own rows often have no category in Open Food Facts, so their segment comes
-- from the GoDesi product master instead.

with products as (

    select * from {{ ref('stg_off__products') }}

),

godesi as (

    select barcode, category as godesi_category
    from {{ ref('stg_erp__products') }}
    where barcode is not null

),

segmented as (

    select
        p.*,
        case
            when g.godesi_category in ('Candy & Pops', 'Mithai')                         then 'Sweets & mithai'
            when g.godesi_category = 'Namkeen'                                           then 'Salty snacks'
            -- drinks first, so 'Sweetened beverages' is not mistaken for a sweet
            when p.food_group in ('beverages', 'alcoholic beverages')
              or lower(p.main_category) like any ('%beverage%', '%drink%', '%juice%')     then 'Beverages'
            when p.food_sub_group = 'sweets'
              or lower(p.main_category) like any ('%sweet snack%', '%indian sweet%', '%mithai%',
                                                  '%confection%', '%candies%', '%candy%',
                                                  '%imli%', '%laddu%', '%ice pop%')     then 'Sweets & mithai'
            when p.food_sub_group = 'chocolate products'
              or lower(p.main_category) like '%chocolate%'                               then 'Chocolate'
            when p.food_sub_group in ('biscuits and cakes', 'pastries')
              or lower(p.main_category) like any ('%biscuit%', '%cookie%', '%cake%')     then 'Biscuits & cakes'
            when p.food_group = 'salty snacks'
              or lower(p.main_category) like any ('%snack%', '%crisp%', '%chips%',
                                                  '%namkeen%', '%bhujia%')               then 'Salty snacks'
            when p.food_group is not null                                                then initcap(p.food_group)
            else 'Uncategorised'
        end                                                     as market_segment
    from products as p
    left join godesi as g
        on p.barcode = g.barcode

)

select
    barcode,
    product_name,
    brand,
    is_godesi,
    brand is not null and not is_godesi                        as is_competitor,
    market_segment,
    main_category,
    food_group,
    food_sub_group,
    net_quantity,
    quantity_unit,
    nutriscore_grade,
    nova_group,
    energy_kcal_100g,
    sugars_100g,
    fat_100g,
    saturated_fat_100g,
    salt_100g,
    proteins_100g,
    additives_count,
    created_at,
    year(created_at)                                           as listed_year
from segmented
