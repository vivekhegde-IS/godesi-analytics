-- Q3: Which products drive revenue? Rank, cumulative share (Pareto) and margin per SKU.

with by_sku as (

    select
        sku_id,
        product_name,
        category,
        is_new_launch,
        sum(net_revenue_inr)                   as net_revenue_inr,
        sum(gross_margin_inr)                  as gross_margin_inr,
        sum(units)                             as units
    from {{ ref('mart_product_performance') }}
    group by all

),

ranked as (

    select
        *,
        row_number() over (order by net_revenue_inr desc)                                 as revenue_rank,
        count(*) over ()                                                                  as sku_count,
        sum(net_revenue_inr) over (order by net_revenue_inr desc rows unbounded preceding)
            / sum(net_revenue_inr) over ()                                                as cumulative_share
    from by_sku

)

select
    revenue_rank,
    sku_id,
    product_name,
    category,
    is_new_launch,
    round(net_revenue_inr / 1e5, 1)                                              as net_revenue_lakh,
    round({{ safe_divide('gross_margin_inr', 'net_revenue_inr') }} * 100, 1)     as gross_margin_pct,
    round(cumulative_share * 100, 1)                                             as cumulative_share_pct,
    revenue_rank <= ceil(sku_count * 0.2)                                        as is_top_20pct_sku
from ranked
order by revenue_rank
