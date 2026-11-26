-- Store dimension (offline channel). Grain: one row per store_id.

with stores as (

    select * from {{ ref('stg_erp__stores') }}

),

distributors as (

    select * from {{ ref('stg_erp__distributors') }}

)

select
    s.store_id,
    s.store_name,
    s.store_type,
    s.city,
    s.state,
    s.pincode,
    s.onboarded_date                     as store_onboarded_date,
    s.distributor_id,
    d.distributor_name,
    d.onboarded_date                     as distributor_onboarded_date
from stores as s
left join distributors as d
    on s.distributor_id = d.distributor_id
