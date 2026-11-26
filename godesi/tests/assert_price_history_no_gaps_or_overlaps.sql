{{ config(store_failures=true) }}

-- SCD2 price ranges must chain perfectly: each version ends exactly when the next one
-- starts, and only the last version is open (valid_to is null).
-- A gap means some orders find no price; an overlap means some orders find two prices
-- (and the enriched order lines would be duplicated).

with ordered as (

    select
        sku_id,
        version_number,
        valid_from,
        valid_to,
        lead(valid_from) over (partition by sku_id order by version_number) as next_valid_from
    from {{ ref('int_products__price_history') }}

)

select *
from ordered
where
    -- not the last version: must end exactly where the next begins
    (next_valid_from is not null and (valid_to is null or valid_to <> next_valid_from))
    -- the last version must be open-ended
    or (next_valid_from is null and valid_to is not null)
    -- a range must not end before it starts
    or valid_to <= valid_from
