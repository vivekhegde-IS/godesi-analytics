-- First order and order count per online customer (cancelled orders excluded).
-- Grain: one row per customer_id that placed at least one order.

with orders as (

    select *
    from {{ ref('int_orders__unioned') }}
    where customer_id is not null
      and not is_cancelled

),

ranked as (

    select
        customer_id,
        order_id,
        ordered_at,
        channel,
        row_number() over (partition by customer_id order by ordered_at, order_id) as order_sequence
    from orders

)

select
    customer_id,
    min(ordered_at)                                         as first_ordered_at,
    min(ordered_at)::date                                   as first_order_date,
    max(iff(order_sequence = 1, channel, null))             as first_order_channel,
    max(ordered_at)                                         as last_ordered_at,
    count(*)                                                as lifetime_orders
from ranked
group by customer_id
