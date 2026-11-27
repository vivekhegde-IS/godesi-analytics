-- Q6: Are we stocking out or overstocking? Stock-out days and cover per month.

select
    date_trunc('month', snapshot_date)                         as snapshot_month,
    count_if(is_stockout)                                      as stockout_warehouse_sku_days,
    count(distinct iff(is_stockout, sku_id, null))             as skus_with_stockout,
    round(avg(network_days_of_cover), 1)                       as avg_network_days_of_cover,
    count_if(network_days_of_cover > 90)                       as overstock_warehouse_sku_days   -- > 3 months of stock
from {{ ref('fct_inventory_daily') }}
group by 1
order by stockout_warehouse_sku_days desc
