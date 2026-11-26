-- Distributors: one row per distributor_id.

with source as (

    select * from {{ source('erp', 'distributors') }}

),

renamed as (

    select
        distributor_id,
        trim(distributor_name)                as distributor_name,
        initcap(trim(city))                   as city,
        initcap(trim(state))                  as state,
        try_to_date(onboarded_date)           as onboarded_date,
        _source_file,
        _loaded_at
    from source

)

select * from renamed
