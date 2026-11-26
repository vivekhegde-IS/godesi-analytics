-- Product dimension (current attributes). Grain: one row per sku_id.
-- Price history is in int_products__price_history / snap_products.

select
    sku_id,
    barcode,
    product_name,
    category,
    sub_category,
    pack_size_g,
    mrp_inr                                                  as current_mrp_inr,
    cost_inr                                                 as current_cost_inr,
    round({{ safe_divide('mrp_inr - cost_inr', 'mrp_inr') }} * 100, 1) as current_margin_at_mrp_pct,
    launch_date,
    launch_date >= '2024-01-01'                              as is_new_launch,     -- launched during the sales period
    is_active,
    is_real_product,
    off_product_name,
    off_main_category,
    nutriscore_grade,
    nova_group,
    energy_kcal_100g,
    sugars_100g,
    fat_100g,
    salt_100g,
    image_url
from {{ ref('int_products__godesi_enriched') }}
