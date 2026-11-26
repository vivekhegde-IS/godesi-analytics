-- All order lines from the three source systems in one shape.
-- Grain: one row per order_item_id.

with erp as (

    select 'erp' as source_system, * from {{ ref('stg_erp__order_items') }}

),

ecom as (

    select 'ecom' as source_system, * from {{ ref('stg_ecom__order_items') }}

),

marketplace as (

    select 'marketplace' as source_system, * from {{ ref('stg_marketplace__order_items') }}

),

unioned as (

    select * from erp
    union all
    select * from ecom
    union all
    select * from marketplace

)

select
    order_item_id,
    order_id,
    source_system,
    sku_id,
    quantity,
    unit_price_inr,
    discount_inr
from unioned
