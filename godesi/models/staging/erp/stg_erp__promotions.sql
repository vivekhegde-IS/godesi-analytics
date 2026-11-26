-- Promotions: one row per promo_code.

with source as (

    select * from {{ source('erp', 'promotions') }}

),

renamed as (

    select
        upper(trim(promo_code))               as promo_code,
        promo_name,
        try_to_date(start_date)               as start_date,
        try_to_date(end_date)                 as end_date,
        try_to_number(discount_pct, 5, 2)     as discount_pct,
        lower(trim(channel))                  as promo_channel,   -- all / d2c / marketplace / quick_commerce
        _source_file,
        _loaded_at
    from source

)

select * from renamed
