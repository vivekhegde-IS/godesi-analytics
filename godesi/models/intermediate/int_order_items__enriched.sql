-- Order lines with everything needed for revenue and margin.
-- Grain: one row per order_item_id (same row count as int_order_items__unioned: no fan-out).
-- Money definitions used everywhere downstream:
--   gross_revenue_inr = quantity x unit price (price actually charged)
--   net_revenue_inr   = gross revenue - promo discount
--   cogs_inr          = quantity x product cost
--   gross_margin_inr  = net revenue - cogs
-- MRP and cost come from the price version that was valid when the order was placed (SCD2 join).

with items as (

    select * from {{ ref('int_order_items__unioned') }}

),

orders as (

    select * from {{ ref('int_orders__unioned') }}

),

price_history as (

    select * from {{ ref('int_products__price_history') }}

),

products as (

    select sku_id, product_name, category, sub_category, is_real_product
    from {{ ref('stg_erp__products') }}

),

joined as (

    select
        i.order_item_id,
        i.order_id,
        o.source_system,
        o.channel,
        o.platform,
        o.customer_id,
        o.store_id,
        o.order_status,
        o.is_cancelled,
        o.promo_code,
        o.ordered_at,
        o.order_date,
        o.updated_at                                  as order_updated_at,

        i.sku_id,
        p.product_name,
        p.category,
        p.sub_category,
        p.is_real_product,

        i.quantity,
        i.unit_price_inr,
        i.discount_inr,
        ph.mrp_inr                                    as mrp_at_order_inr,
        ph.cost_inr                                   as unit_cost_inr

    from items as i
    inner join orders as o
        on i.order_id = o.order_id
    left join products as p
        on i.sku_id = p.sku_id
    -- SCD2 join: the price version valid at the moment of the order (ranges never overlap)
    left join price_history as ph
        on  i.sku_id = ph.sku_id
        and o.ordered_at >= ph.valid_from
        and (o.ordered_at < ph.valid_to or ph.valid_to is null)

)

select
    *,
    quantity * unit_price_inr                                        as gross_revenue_inr,
    quantity * unit_price_inr - discount_inr                         as net_revenue_inr,
    quantity * unit_cost_inr                                         as cogs_inr,
    quantity * unit_price_inr - discount_inr - quantity * unit_cost_inr as gross_margin_inr
from joined
