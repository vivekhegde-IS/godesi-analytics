-- Offline order lines: one row per order_item_id.

with source as (

    select * from {{ source('erp', 'order_items') }}

),

renamed as (

    select
        order_item_id,
        order_id,
        sku_id,
        try_to_number(qty)                    as quantity,
        try_to_number(unit_price_inr, 10, 2)  as unit_price_inr,
        try_to_number(discount_inr, 10, 2)    as discount_inr,
        _source_file,
        _loaded_at
    from source

)

select * from renamed
