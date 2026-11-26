-- Fact: one row per order line (order_item_id). The centre of the star schema.
--
-- INCREMENTAL: the first run builds the whole table. Later runs only process lines whose
-- order or return changed since the last run (row_updated_at), and MERGE them in on
-- order_item_id: changed lines are UPDATED, new lines are INSERTED, nothing is duplicated.
-- This is how the late status updates in batch2 (shipped -> delivered) are applied.

{{
    config(
        materialized='incremental',
        unique_key='order_item_id',
        incremental_strategy='merge',
        on_schema_change='append_new_columns'
    )
}}

with lines as (

    select * from {{ ref('int_order_items__enriched') }}

),

returns as (

    select * from {{ ref('int_returns__aggregated') }}

),

customers as (

    select customer_id, city, state from {{ ref('stg_ecom__customers') }}

),

stores as (

    select store_id, city, state from {{ ref('stg_erp__stores') }}

),

final as (

    select
        -- keys to the dimensions
        l.order_item_id,
        l.order_id,
        l.order_date,                                             -- -> dim_date
        l.platform,                                               -- -> dim_channel
        l.sku_id,                                                 -- -> dim_products
        l.customer_id,                                            -- -> dim_customers (online orders)
        l.store_id,                                               -- -> dim_stores (offline orders)
        coalesce(c.city, s.city)                                  as city,     -- -> dim_geography
        coalesce(c.state, s.state)                                as state,

        -- descriptive context
        l.ordered_at,
        l.source_system,
        l.channel,
        l.category,
        l.promo_code,
        l.order_status,
        l.is_cancelled,

        -- measures
        l.quantity,
        l.unit_price_inr,
        l.mrp_at_order_inr,
        l.unit_cost_inr,
        l.gross_revenue_inr,
        l.discount_inr,
        l.net_revenue_inr,
        l.cogs_inr,
        l.gross_margin_inr,
        r.order_item_id is not null                               as is_returned,
        coalesce(r.refund_inr, 0)                                 as refund_inr,
        l.net_revenue_inr - coalesce(r.refund_inr, 0)             as net_revenue_after_returns_inr,

        -- change tracking for the incremental logic
        l.order_updated_at,
        r.first_returned_at,
        greatest(l.order_updated_at, coalesce(r.first_returned_at, l.order_updated_at)) as row_updated_at

    from lines as l
    left join returns as r
        on l.order_item_id = r.order_item_id
    left join customers as c
        on l.customer_id = c.customer_id
    left join stores as s
        on l.store_id = s.store_id

)

select * from final

{% if is_incremental() %}
-- only lines that changed after the newest change already in this table
where row_updated_at > (select max(row_updated_at) from {{ this }})
{% endif %}
