-- Stores (kirana and modern trade): one row per store_id.

with source as (

    select * from {{ source('erp', 'stores') }}

),

renamed as (

    select
        store_id,
        distributor_id,
        trim(store_name)                      as store_name,
        lower(trim(store_type))               as store_type,      -- kirana / modern_trade
        initcap(trim(city))                   as city,
        initcap(trim(state))                  as state,
        pincode,
        try_to_date(onboarded_date)           as onboarded_date,
        _source_file,
        _loaded_at
    from source

)

select * from renamed
