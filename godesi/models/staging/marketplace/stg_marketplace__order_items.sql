-- Marketplace and quick-commerce order lines: one row per order_item_id.
-- About 2% of prices arrive as text like 'Rs. 120.00': strip the prefix BEFORE converting,
-- otherwise TRY_TO_NUMBER would silently turn them into NULL.

with source as (

    select * from {{ source('marketplace', 'order_items') }}

),

renamed as (

    select
        order_item_id,
        order_id,
        sku_id,
        try_to_number(qty)                    as quantity,
        try_to_number(
            trim(replace(unit_price_inr, 'Rs.', '')), 10, 2
        )                                     as unit_price_inr,
        try_to_number(discount_inr, 10, 2)    as discount_inr,
        _source_file,
        _loaded_at
    from source

)

select * from renamed
