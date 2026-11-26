-- Fact: one row per order. Order totals are summed from fct_order_items, so line and
-- order revenue always agree.

with lines as (

    select * from {{ ref('fct_order_items') }}

),

first_orders as (

    select customer_id, first_ordered_at from {{ ref('int_customers__first_order') }}

),

orders as (

    select
        order_id,
        min(order_date)                                as order_date,
        min(ordered_at)                                as ordered_at,
        min(source_system)                             as source_system,
        min(channel)                                   as channel,
        min(platform)                                  as platform,
        min(customer_id)                               as customer_id,
        min(store_id)                                  as store_id,
        min(city)                                      as city,
        min(state)                                     as state,
        min(order_status)                              as order_status,
        boolor_agg(is_cancelled)                       as is_cancelled,
        min(promo_code)                                as promo_code,
        count(*)                                       as line_count,
        sum(quantity)                                  as units,
        sum(gross_revenue_inr)                         as gross_revenue_inr,
        sum(discount_inr)                              as discount_inr,
        sum(net_revenue_inr)                           as net_revenue_inr,
        sum(cogs_inr)                                  as cogs_inr,
        sum(gross_margin_inr)                          as gross_margin_inr,
        sum(refund_inr)                                as refund_inr,
        sum(net_revenue_after_returns_inr)             as net_revenue_after_returns_inr,
        boolor_agg(is_returned)                        as is_returned,
        max(order_updated_at)                          as updated_at
    from lines
    group by order_id

)

select
    o.*,
    o.promo_code is not null                           as has_promo,
    coalesce(o.ordered_at = f.first_ordered_at and not o.is_cancelled, false) as is_first_order
from orders as o
left join first_orders as f
    on o.customer_id = f.customer_id
