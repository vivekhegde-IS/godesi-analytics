{{ config(store_failures=true) }}

-- A refund can never be larger than what the customer paid for that line.
-- If it were, "revenue after returns" could go negative and return rates would be overstated.

select
    order_item_id,
    net_revenue_inr,
    refund_inr
from {{ ref('fct_order_items') }}
where refund_inr > net_revenue_inr + 0.01
