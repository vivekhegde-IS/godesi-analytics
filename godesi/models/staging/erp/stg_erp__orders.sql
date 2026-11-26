-- Offline orders (stores ordering through distributors): one row per order_id.
-- Batch2 re-sends late status updates, so keep the latest version of each order.

with source as (

    select * from {{ source('erp', 'orders') }}

),

renamed as (

    select
        order_id,
        lower(trim(channel))                  as channel,
        lower(trim(platform))                 as platform,
        customer_id,                                       -- empty for offline orders
        store_id,
        lower(trim(status))                   as order_status,
        upper(trim(promo_code))               as promo_code,
        try_to_timestamp_ntz(order_ts, 'YYYY-MM-DD HH24:MI:SS')   as ordered_at,
        try_to_timestamp_ntz(updated_at, 'YYYY-MM-DD HH24:MI:SS') as updated_at,
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
