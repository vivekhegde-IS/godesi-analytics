# Cost review

How much this project spends in Snowflake, who spends it, and what keeps it low.
Numbers from `setup/07_cost_review.sql` (Snowflake `ACCOUNT_USAGE`), reviewed on **29 November 2026**, after the
first CI run and the first daily production run on GitHub Actions. `ACCOUNT_USAGE` lags up to 3 hours.

## Summary

- The whole project, from the first load to dashboards and CI/CD, has used **6.47 credits** on `GODESI_WH` in 5 days
  (plus 0.84 on the default `COMPUTE_WH` while setting up). That is a third of the **20-credit monthly cap**.
- **The automated work is almost free:** the daily production run and a CI run each need well under a minute of
  warehouse time. Expected steady state: **about 1 to 1.5 credits a month**.
- **The biggest cost was people, not pipelines:** the Streamlit app inside Snowflake keeps the warehouse running while
  it is open. 14 sessions kept it busy for about 157 minutes, roughly **2.6 credits, 40% of everything**.

## Setup that controls cost

| Control | Setting | Effect |
|---|---|---|
| Warehouse size | X-Small (1 credit per running hour) | The smallest size; the whole project builds in about 40 seconds |
| Auto-suspend | 60 seconds | The warehouse stops a minute after the last query |
| Resource monitor | `GODESI_RM`: 20 credits a month, notify at 75%, suspend at 100%, suspend immediately at 110% | A runaway cost is impossible |
| Incremental model | `fct_order_items` (merge on `row_updated_at`) | A daily run with no new orders processes 0 rows (`SUCCESS 0`) |
| Slim CI | `state:modified+ --defer` | A one-model pull request builds 1 model + its tests (about 6 s) instead of 191 nodes |
| Power BI | Import mode | Clicking in the report costs nothing; only a refresh queries Snowflake |
| Public dashboard | CSV exports on Streamlit Community Cloud | Visitors never wake the warehouse |
| Query tags | `dbt_ci`, `dbt_prod_daily`, `godesi_dashboard_export` | Every automated workload can be traced in `QUERY_HISTORY` |

## Credits used

| Day | Compute | Cloud services | Total | What happened |
|---|---|---|---|---|
| 24 Nov | 0.000 | 0.001 | 0.001 | Setup scripts |
| 25 Nov | 0.034 | 0.001 | 0.035 | Raw data loads |
| 26 Nov | 2.301 | 0.084 | 2.385 | dbt modelling, tests, docs |
| 27 Nov | 2.324 | 0.003 | 2.327 | Analyses, Power BI, Streamlit in Snowflake |
| 28 Nov | 1.678 | 0.043 | 1.721 | Dashboards, brand fix, CI tests |
| **Total** | **6.337** | **0.132** | **6.469** | Cloud services are 2% (under the 10% that is free) |

| Warehouse | Credits since the start |
|---|---|
| GODESI_WH | 6.47 |
| COMPUTE_WH (Snowflake's default, first practice queries) | 0.84 |

Resource monitor `GODESI_RM` this month: **6.51 of 20 credits used, 13.49 left**.

## Who spends it (query 3, execution time)

| Workload | Queries | Execution minutes | Credits (upper bound) |
|---|---|---|---|
| Streamlit in Snowflake (app sessions) | 14 | 156.8 | 2.614 |
| Local dbt runs and tests (TRANSFORMER, no tag) | 4,398 | 5.0 | 0.084 |
| `dbt_ci` (GitHub pull request CI + local CI tests) | 1,437 | 1.5 | 0.025 |
| Loading raw data (LOADER) | 344 | 0.4 | 0.006 |
| `dbt_prod_daily` (GitHub daily run) | 341 | 0.4 | 0.007 |
| Admin work (SYSADMIN, SECURITYADMIN, ACCOUNTADMIN) | 615 | 0.3 | 0.007 |
| Power BI refreshes and REPORTER queries | about 330 | 0.4 | about 0.005 |
| `godesi_dashboard_export` | 60 | 0.1 | 0.001 |

Execution time adds up to about 2.7 credits, but the meter shows 6.47. The difference is time the warehouse was
**running but idle**: each resume is billed for at least 60 seconds, auto-suspend waits 60 seconds after the last
query, and a Streamlit app holds the warehouse while its tab is open.

**The 10 slowest queries** of the month were all `execute streamlit "GODESI_ANALYTICS"."APPS"."GODESI_DASHBOARD"()`,
lasting 4 to 24 minutes each: one per app session, ending only after about 15 minutes without activity.

## Storage (queries 5 and 6)

| Database | Average size |
|---|---|
| GODESI_ANALYTICS | 0.051 GB |
| GODESI_RAW | 0.010 GB (+0.002 GB fail-safe) |

Biggest tables: `fct_order_items` 7.5 MB (in MARTS and again in the dev schema), Open Food Facts `products` 5.6 MB,
`fct_orders` 4 MB. Columnar compression keeps the whole project at about **60 MB**: storage costs a fraction of a
cent a month. The zero-copy clone from Phase 6 (`GODESI_ANALYTICS_CLONE`) uses 0 GB because nothing in it changed.

## Monthly estimate (steady state)

| Workload | Assumption | Credits a month |
|---|---|---|
| Daily production run | about 1-2 minutes of warehouse time a day (40 s build + export + 60 s auto-suspend) | about 0.5-1.0 |
| CI | about 8 pull requests a month, 1 minute each (slim CI is often seconds) | about 0.15 |
| Dashboards | Power BI refresh weekly; public app reads CSVs | under 0.05 |
| Streamlit in Snowflake | depends on use: about 0.25 credits per session | 0 to 2 |
| **Total** | | **about 1 to 3 credits** |

At list prices of a few US dollars per credit, that is a few dollars a month, well inside the 20-credit cap.

## Findings and what I would do next

1. **Close the Streamlit in Snowflake tab when done.** Each open session keeps the X-Small warehouse running for about
   15 minutes. Share the public link (CSV-based, free) with the founder; keep the Snowflake app for live checks.
2. **Keep X-Small.** The slowest dbt model runs in about 6 seconds; a bigger warehouse would cost 2x more per second
   without a real gain.
3. **Tag everything.** Power BI and the Snowflake app could get their own warehouse or a query tag, so the review can
   separate them without guessing from JSON tags.
4. **Clean up:** drop `GODESI_ANALYTICS_CLONE` (setup practice from Phase 6) and stop using `COMPUTE_WH`.
5. **If the data grew 100 times:** cluster `fct_order_items` by `order_date`, keep slim CI so pull requests stay cheap,
   and check `WAREHOUSE_METERING_HISTORY` weekly.
6. **When the trial ends:** the public dashboard (CSV) and the Power BI file keep working; disable the daily workflow
   (Actions > Daily production run > ... > Disable workflow) so it does not fail every day.
