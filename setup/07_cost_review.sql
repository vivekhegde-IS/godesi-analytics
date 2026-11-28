-- =====================================================================
-- 07_cost_review.sql: what does this project cost, and who spends it?
-- Run in Snowsight as ACCOUNTADMIN (ACCOUNT_USAGE is only visible to it). Read-only: changes nothing.
-- ACCOUNT_USAGE lags 45 minutes to 3 hours behind, so today's last runs may be missing.
-- Put the answers in docs/cost_review.md.
-- =====================================================================
use role ACCOUNTADMIN;
use warehouse GODESI_WH;

-- ---------- 1. credits per day on GODESI_WH, last 30 days ----------
select
    to_date(start_time)                                     as usage_date,
    round(sum(credits_used_compute), 3)                     as compute_credits,
    round(sum(credits_used_cloud_services), 3)              as cloud_services_credits,
    round(sum(credits_used), 3)                             as total_credits
from snowflake.account_usage.warehouse_metering_history
where warehouse_name = 'GODESI_WH'
  and start_time >= dateadd(day, -30, current_timestamp())
group by 1
order by 1;

-- ---------- 2. total credits per warehouse since the account started ----------
select warehouse_name, round(sum(credits_used), 2) as credits
from snowflake.account_usage.warehouse_metering_history
group by 1
order by 2 desc;

-- ---------- 3. who uses the warehouse: time and an estimate of credits per query tag ----------
-- dbt_ci (pull requests), dbt_prod_daily (GitHub daily job), godesi_dashboard_export (CSV export).
-- Queries without a tag: your Snowsight worksheets, Power BI, Streamlit in Snowflake, local dbt runs.
-- Estimate: X-Small = 1 credit per hour of running time (an upper bound: queries running in parallel share it).
select
    coalesce(nullif(query_tag, ''), '(no tag) ' || role_name)        as workload,
    count(*)                                                          as queries,
    round(sum(execution_time) / 1000 / 60, 1)                         as execution_minutes,
    round(sum(execution_time) / 1000 / 3600 * 1, 3)                   as est_credits_upper_bound
from snowflake.account_usage.query_history
where warehouse_name = 'GODESI_WH'
  and start_time >= dateadd(day, -30, current_timestamp())
group by 1
order by execution_minutes desc;

-- ---------- 4. the 10 slowest queries of the last 30 days (where to optimise first) ----------
select
    start_time,
    role_name,
    query_tag,
    round(total_elapsed_time / 1000, 1)                      as seconds,
    round(bytes_scanned / power(1024, 2), 1)                 as mb_scanned,
    left(regexp_replace(query_text, '\\s+', ' '), 120)       as query_start
from snowflake.account_usage.query_history
where warehouse_name = 'GODESI_WH'
  and start_time >= dateadd(day, -30, current_timestamp())
order by total_elapsed_time desc
limit 10;

-- ---------- 5. storage: how big are the databases? ----------
select
    database_name,
    round(avg(average_database_bytes) / power(1024, 3), 3)  as avg_gb,
    round(avg(average_failsafe_bytes) / power(1024, 3), 3)  as avg_failsafe_gb
from snowflake.account_usage.database_storage_usage_history
where usage_date >= dateadd(day, -7, current_date())
group by 1
order by 2 desc;

-- ---------- 6. the 10 biggest tables ----------
select table_catalog, table_schema, table_name,
       round(active_bytes / power(1024, 2), 1)              as active_mb,
       round(time_travel_bytes / power(1024, 2), 1)         as time_travel_mb
from snowflake.account_usage.table_storage_metrics
where table_catalog in ('GODESI_RAW', 'GODESI_ANALYTICS') and deleted = false
order by active_bytes desc
limit 10;

-- ---------- 7. the cost guard: is the resource monitor still in place? ----------
show resource monitors;
-- read: credit_quota, used_credits, remaining_credits, and that GODESI_WH is attached
show warehouses like 'GODESI_WH';
-- read: size X-Small, auto_suspend 60, resource_monitor GODESI_RM

-- ---------- 8. one month of the daily job, estimated ----------
-- (minutes of one daily run from query 3 / 60) x 30 days x 1 credit per hour = credits per month.
-- Multiply by your price per credit (Snowsight > Admin > Cost management shows it) for the money cost.
