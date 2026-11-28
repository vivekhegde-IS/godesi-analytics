-- Q5: Do customers come back? Retention and lifetime value at months 1, 3, 6 and 12.
-- Weighted over all cohorts that are old enough to have reached that month
-- (sum of active customers / sum of cohort customers, not an average of percentages).

with cohorts as (

    select * from {{ ref('mart_customer_cohorts') }}

),

last_month as (

    select max(cohort_month) as max_month from cohorts

),

checkpoints as (

    select
        c.months_since_first_order,
        sum(c.active_customers)                                         as active_customers,
        sum(c.cohort_customers)                                         as cohort_customers,
        sum(c.cumulative_revenue_per_customer * c.cohort_customers)     as cumulative_revenue_inr,
        count(*)                                                        as cohorts_included
    from cohorts as c
    cross join last_month as l
    where c.months_since_first_order in (1, 3, 6, 12)
      -- only cohorts with that many full months of history
      and dateadd(month, c.months_since_first_order, c.cohort_month) <= l.max_month
    group by c.months_since_first_order

)

select
    months_since_first_order,
    cohorts_included,
    round({{ safe_divide('active_customers', 'cohort_customers') }} * 100, 1)          as retention_pct,
    round({{ safe_divide('cumulative_revenue_inr', 'cohort_customers') }}, 0)          as ltv_inr
from checkpoints
order by months_since_first_order
