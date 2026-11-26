-- A product cannot be sold before its launch date.
-- If this failed, new-launch performance (Q3) would include impossible early sales.

select
    f.order_item_id,
    f.sku_id,
    f.order_date,
    p.launch_date
from {{ ref('fct_order_items') }} as f
inner join {{ ref('dim_products') }} as p
    on f.sku_id = p.sku_id
where f.order_date < p.launch_date
