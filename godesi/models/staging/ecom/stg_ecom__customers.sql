-- D2C customers: one row per customer_id.
-- City names arrive in many spellings (Bangalore, BENGALURU, 'Bengaluru '). Clean them:
--   1. trim + lower, then look up old names in the city_name_mapping seed (bangalore -> Bengaluru)
--   2. anything not in the seed just gets proper case (mumbai -> Mumbai)

with source as (

    select * from {{ source('ecom', 'customers') }}

),

city_map as (

    select * from {{ ref('city_name_mapping') }}

),

renamed as (

    select
        s.customer_id,
        trim(s.first_name)                          as first_name,
        trim(s.last_name)                           as last_name,
        lower(trim(s.email))                        as email,
        try_to_date(s.signup_date)                  as signup_date,
        s.city                                      as city_raw,      -- kept for auditing
        coalesce(m.city, {{ standardize_city('s.city') }}) as city,
        {{ standardize_city('s.state') }}           as state,
        nullif(trim(s.pincode), '')                 as pincode,       -- about 3% are missing
        lower(trim(s.acquisition_source))           as acquisition_source,
        s._source_file,
        s._loaded_at
    from source as s
    left join city_map as m
        on lower(trim(s.city)) = m.raw_city

)

select * from renamed
