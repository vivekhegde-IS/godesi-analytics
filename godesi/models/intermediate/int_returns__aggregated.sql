-- Returns summed per order line (a line could in theory be returned more than once).
-- Grain: one row per returned order_item_id.

select
    order_item_id,
    count(*)                    as return_count,
    sum(refund_inr)             as refund_inr,
    min(returned_at)            as first_returned_at,
    max(return_reason)          as return_reason          -- one reason per line in this data
from {{ ref('stg_ecom__returns') }}
group by order_item_id
