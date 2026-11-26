{{ config(store_failures=true) }}

-- A customer cannot order before they signed up.
-- If this failed, cohorts and "days to first order" would be wrong (negative days,
-- customers counted in a cohort before they existed).
-- A singular test PASSES when it returns 0 rows: every row returned is a broken order.

select
    o.order_id,
    o.customer_id,
    o.order_date,
    c.signup_date
from {{ ref('fct_orders') }} as o
inner join {{ ref('dim_customers') }} as c
    on o.customer_id = c.customer_id
where o.order_date < c.signup_date
