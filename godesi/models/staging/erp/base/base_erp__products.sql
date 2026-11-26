-- Base model: EVERY version of every product, with proper types.
-- Grain: one row per sku_id per version (72 rows = 60 originals + 12 price changes from batch2).
-- Two models build on it:
--   * stg_erp__products            keeps only the latest version (current product master)
--   * int_products__price_history  keeps all versions with valid_from / valid_to (SCD Type 2)

with source as (

    select * from {{ source('erp', 'products') }}

),

renamed as (

    select
        -- ids
        sku_id,
        barcode,                                          -- only the 9 real GoDesi products have one

        -- descriptive
        trim(product_name)                    as product_name,
        category,
        sub_category,

        -- numbers: raw text -> numbers (TRY_ returns NULL instead of failing)
        try_to_number(pack_size_g)            as pack_size_g,
        try_to_number(mrp_inr, 10, 2)         as mrp_inr,
        try_to_number(cost_inr, 10, 2)        as cost_inr,

        -- flags: 'True' / 'False' text -> boolean
        try_to_boolean(is_real_product)       as is_real_product,
        try_to_boolean(is_active)             as is_active,

        -- dates and timestamps
        try_to_date(launch_date)              as launch_date,
        try_to_timestamp_ntz(updated_at)      as updated_at,

        -- audit columns from the load
        _source_file,
        _loaded_at

    from source

)

select * from renamed
