-- Price history of every product as SCD Type 2.
-- Grain: one row per sku_id per price version.
-- valid_from = when this version started; valid_to = when the next version started
-- (NULL for the version that is still current).
-- A price change applies from the START of the day it was entered: the ERP records the change
-- at 09:00, but the channels already charge the new price from midnight (the 5.3 test
-- "unit_price_inr <= mrp_at_order_inr" found those early-morning orders).
-- Use it to find the price that was valid at any moment:
--   where ordered_at >= valid_from and (ordered_at < valid_to or valid_to is null)

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
        -- the first version is valid from the launch day (or its own day, if earlier)
        iff(
            row_number() over (partition by sku_id order by updated_at) = 1,
            least(updated_at::date, launch_date),
            updated_at::date
        )::timestamp_ntz                                                  as valid_from,
        (lead(updated_at) over (partition by sku_id order by updated_at))::date::timestamp_ntz
                                                                          as valid_to,
        _source_file
    from versions

)

select
    *,
    valid_to is null as is_current
from history
