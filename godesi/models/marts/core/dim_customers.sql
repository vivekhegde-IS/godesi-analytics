-- Customer dimension. Grain: one row per customer_id (all 30,000 sign-ups,
-- including those who never ordered).

with customers as (

    select * from {{ ref('stg_ecom__customers') }}

),

first_orders as (

    select * from {{ ref('int_customers__first_order') }}

)

select
    c.customer_id,
    c.first_name,
    c.last_name,
    c.email,
    c.city,
    c.state,
    c.pincode,
    c.acquisition_source,
    c.signup_date,
    date_trunc('month', c.signup_date)                       as signup_month,
    f.first_order_date,
    date_trunc('month', f.first_order_date)                  as cohort_month,      -- month of first order
    f.first_order_channel,
    f.last_ordered_at::date                                  as last_order_date,
    coalesce(f.lifetime_orders, 0)                           as lifetime_orders,
    f.customer_id is not null                                as has_ordered,
    coalesce(f.lifetime_orders, 0) > 1                       as is_repeat_customer,
    datediff(day, c.signup_date, f.first_order_date)         as days_to_first_order
from customers as c
left join first_orders as f
    on c.customer_id = f.customer_id
