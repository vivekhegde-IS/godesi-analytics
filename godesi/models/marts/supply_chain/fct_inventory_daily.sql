-- Fact: end-of-day stock. Grain: one row per snapshot_date, warehouse_id and sku_id.
-- Network columns (all warehouses together) answer Q6: are we stocking out or overstocking?
--   days_of_cover = network stock / average units sold per day over the last 28 days

with stock as (

    select * from {{ ref('stg_inventory__inventory_daily') }}

),

daily_sales as (

    select order_date, sku_id, sum(quantity) as units_sold
    from {{ ref('fct_order_items') }}
    where not is_cancelled
    group by order_date, sku_id

),

network as (

    select
        s.snapshot_date,
        s.sku_id,
        sum(s.on_hand_units)                   as network_on_hand_units,
        coalesce(max(d.units_sold), 0)         as units_sold
    from stock as s
    left join daily_sales as d
        on s.snapshot_date = d.order_date
        and s.sku_id = d.sku_id
    group by s.snapshot_date, s.sku_id

),

network_cover as (

    select
        *,
        avg(units_sold) over (
            partition by sku_id
            order by snapshot_date
            rows between 27 preceding and current row
        )                                      as avg_daily_units_28d
    from network

)

select
    s.snapshot_date,
    s.warehouse_id,
    s.sku_id,
    s.on_hand_units,
    s.on_hand_units = 0                                          as is_stockout,
    n.network_on_hand_units,
    n.units_sold                                                 as network_units_sold,
    round(n.avg_daily_units_28d, 1)                              as network_avg_daily_units_28d,
    round(n.network_on_hand_units / nullif(n.avg_daily_units_28d, 0), 1) as network_days_of_cover
from stock as s
inner join network_cover as n
    on s.snapshot_date = n.snapshot_date
    and s.sku_id = n.sku_id
