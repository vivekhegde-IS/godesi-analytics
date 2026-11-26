-- Staging model for the ERP product master.
-- Grain: one row per sku_id: the latest version of each product.
-- Types are cast in base_erp__products; here we only keep the newest version.
-- (All versions, with valid_from / valid_to, are in int_products__price_history.)

with products as (

    select * from {{ ref('base_erp__products') }}

),

latest as (

    select *
    from products
    qualify row_number() over (
        partition by sku_id
        order by updated_at desc, _loaded_at desc
    ) = 1

)

select * from latest
