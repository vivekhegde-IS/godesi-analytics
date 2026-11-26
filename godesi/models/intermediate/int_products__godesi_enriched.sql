-- GoDesi products with real Open Food Facts details for the 9 real SKUs.
-- Grain: one row per sku_id (60). Synthetic SKUs have no barcode, so their OFF columns are NULL.

with products as (

    select * from {{ ref('stg_erp__products') }}

),

off as (

    select * from {{ ref('stg_off__products') }}
    where is_godesi

)

select
    p.*,
    off.product_name             as off_product_name,
    off.main_category            as off_main_category,
    off.nutriscore_grade,
    off.nova_group,
    off.energy_kcal_100g,
    off.sugars_100g,
    off.fat_100g,
    off.salt_100g,
    off.image_url
from products as p
left join off
    on p.barcode = off.barcode
