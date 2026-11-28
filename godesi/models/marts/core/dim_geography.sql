-- Geography dimension. Grain: one row per city.
-- Cities come from customers, stores and distributors (already cleaned in staging).

with cities as (

    select city, state from {{ ref('stg_ecom__customers') }}
    union distinct
    select city, state from {{ ref('stg_erp__stores') }}
    union distinct
    select city, state from {{ ref('stg_erp__distributors') }}

)

select
    city,
    state,
    case
        when state in ('Karnataka', 'Tamil Nadu', 'Telangana', 'Kerala', 'Andhra Pradesh') then 'South'
        when state in ('Maharashtra', 'Gujarat', 'Goa')                                     then 'West'
        when state in ('Delhi', 'Haryana', 'Rajasthan', 'Uttar Pradesh', 'Punjab')          then 'North'
        when state in ('West Bengal', 'Odisha', 'Bihar', 'Assam')                           then 'East'
        else 'Other'
    end                                   as region,
    city = 'Bengaluru'                    as is_home_city              -- GoDesi is a Bengaluru brand
from cities
where city is not null
