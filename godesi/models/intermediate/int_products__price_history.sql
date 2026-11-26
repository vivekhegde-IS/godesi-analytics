-- Price history of every product as SCD Type 2.
-- Grain: one row per sku_id per price version.
-- valid_from = when this version started; valid_to = when the next version started
-- (NULL for the version that is still current).
-- Use it to find the price that was valid on any date:
--   where order_date >= valid_from and (order_date < valid_to or valid_to is null)

with versions as (

    select
        sku_id,
        product_name,
        mrp_inr,
        cost_inr,
        launch_date,
        updated_at,
        _source_file
    from {{ ref('base_erp__products') }}

),

history as (

    select
        sku_id,
        product_name,
        mrp_inr,
        cost_inr,
        row_number() over (partition by sku_id order by updated_at)       as version_number,
        -- the first version is valid from the start of the launch day: launch-day orders placed
        -- before 09:00 (the time on updated_at) must still find a price
        iff(
            row_number() over (partition by sku_id order by updated_at) = 1,
            least(updated_at, launch_date::timestamp_ntz),
            updated_at
        )                                                                 as valid_from,
        lead(updated_at) over (partition by sku_id order by updated_at)   as valid_to,
        _source_file
    from versions

)

select
    *,
    valid_to is null as is_current
from history
