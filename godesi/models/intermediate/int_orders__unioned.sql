-- All orders from the three source systems in one shape.
-- Grain: one row per order_id (order ids are unique across systems).
--   erp          -> offline orders from stores via distributors
--   ecom         -> D2C website orders
--   marketplace  -> Amazon, Flipkart and quick-commerce orders

with erp as (

    select 'erp' as source_system, * from {{ ref('stg_erp__orders') }}

),

ecom as (

    select 'ecom' as source_system, * from {{ ref('stg_ecom__orders') }}

),

marketplace as (

    select 'marketplace' as source_system, * from {{ ref('stg_marketplace__orders') }}

),

unioned as (

    select * from erp
    union all
    select * from ecom
    union all
    select * from marketplace

)

select
    order_id,
    source_system,
    channel,
    platform,
    customer_id,
    store_id,
    order_status,
    order_status = 'cancelled'            as is_cancelled,
    promo_code,
    ordered_at,
    ordered_at::date                      as order_date,
    updated_at
from unioned
