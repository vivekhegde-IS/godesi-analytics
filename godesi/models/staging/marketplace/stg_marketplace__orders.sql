-- Marketplace (Amazon, Flipkart) and quick-commerce (Blinkit, Zepto, Instamart) orders: one row per order_id.
-- Cleans three problems: (1) two timestamp formats, 'YYYY-MM-DD HH:MI:SS' and quick-commerce
-- 'DD/MM/YYYY HH:MI'; (2) exact duplicate rows sent twice; (3) late status updates in batch2.
-- Keeping one row per order_id (the latest) solves both (2) and (3).

with source as (

    select * from {{ source('marketplace', 'orders') }}

),

renamed as (

    select
        order_id,
        lower(trim(channel))                  as channel,
        lower(trim(platform))                 as platform,
        customer_id,
        store_id,
        lower(trim(status))                   as order_status,
        upper(trim(promo_code))               as promo_code,
        coalesce(
            try_to_timestamp_ntz(order_ts, 'YYYY-MM-DD HH24:MI:SS'),
            try_to_timestamp_ntz(order_ts, 'DD/MM/YYYY HH24:MI')
        )                                     as ordered_at,
        coalesce(
            try_to_timestamp_ntz(updated_at, 'YYYY-MM-DD HH24:MI:SS'),
            try_to_timestamp_ntz(updated_at, 'DD/MM/YYYY HH24:MI')
        )                                     as updated_at,
        _source_file,
        _loaded_at
    from source

),

latest as (

    select *
    from renamed
    qualify row_number() over (
        partition by order_id
        order by updated_at desc, _loaded_at desc
    ) = 1

)

select * from latest
