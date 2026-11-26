-- Staging model for the ERP product master.
-- One row per sku_id, with proper data types.
-- Batch2 re-sent 12 products with new prices; keep only the latest version.
-- (The full price history is kept later by a snapshot, in Phase 4.)

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

),

latest as (

    select *
    from renamed
    -- keep the newest version of each product
    qualify row_number() over (
        partition by sku_id
        order by updated_at desc, _loaded_at desc
    ) = 1

)

select * from latest