-- Q2: which SKUs and categories drive revenue and margin?
-- Grain: one row per month and sku_id. Cancelled orders excluded.

with lines as (

    select * from {{ ref('fct_order_items') }}
    where not is_cancelled

),

products as (

    select sku_id, product_name, category, sub_category, is_real_product, is_new_launch
    from {{ ref('dim_products') }}

)

select
    date_trunc('month', l.order_date)                                   as order_month,
    l.sku_id,
    p.product_name,
    p.category,
    p.sub_category,
    p.is_real_product,
    p.is_new_launch,
    count(distinct l.order_id)                                          as orders,
    sum(l.quantity)                                                     as units,
    sum(l.net_revenue_inr)                                              as net_revenue_inr,
    sum(l.cogs_inr)                                                     as cogs_inr,
    sum(l.gross_margin_inr)                                             as gross_margin_inr,
    round({{ safe_divide('sum(l.gross_margin_inr)', 'sum(l.net_revenue_inr)') }} * 100, 1) as gross_margin_pct,
    count_if(l.is_returned)                                             as returned_lines,
    sum(l.refund_inr)                                                   as refund_inr
from lines as l
left join products as p
    on l.sku_id = p.sku_id
group by all
