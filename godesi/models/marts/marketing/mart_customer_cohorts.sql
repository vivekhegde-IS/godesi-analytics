-- Q5: do D2C and online customers come back?
-- Grain: one row per cohort_month (month of first order) and months_since_first_order.
-- retention_pct = customers active in that month / customers in the cohort.
-- cumulative_revenue_per_customer is the cohort's lifetime value so far (LTV).

with orders as (

    select customer_id, order_date, net_revenue_inr
    from {{ ref('fct_orders') }}
    where customer_id is not null
      and not is_cancelled

),

customers as (

    select customer_id, cohort_month
    from {{ ref('dim_customers') }}
    where has_ordered

),

activity as (

    select
        c.cohort_month,
        datediff(month, c.cohort_month, date_trunc('month', o.order_date)) as months_since_first_order,
        count(distinct o.customer_id)          as active_customers,
        count(*)                               as orders,
        sum(o.net_revenue_inr)                 as net_revenue_inr
    from orders as o
    inner join customers as c
        on o.customer_id = c.customer_id
    group by all

),

cohort_size as (

    select cohort_month, count(*) as cohort_customers
    from customers
    group by cohort_month

)

select
    a.cohort_month,
    a.months_since_first_order,
    s.cohort_customers,
    a.active_customers,
    round(a.active_customers / s.cohort_customers * 100, 1)                  as retention_pct,
    a.orders,
    a.net_revenue_inr,
    round(
        sum(a.net_revenue_inr) over (partition by a.cohort_month order by a.months_since_first_order)
        / s.cohort_customers, 2
    )                                                                        as cumulative_revenue_per_customer
from activity as a
inner join cohort_size as s
    on a.cohort_month = s.cohort_month
