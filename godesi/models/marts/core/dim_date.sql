-- Calendar dimension. Grain: one row per day, 2024-01-01 to 2025-12-31.
-- Festival columns come from the festival_calendar seed; the "festival window" is the
-- 10 days before a festival plus the day itself (when sales rise).

with days as (

    {{ dbt_utils.date_spine(
        datepart="day",
        start_date="cast('2024-01-01' as date)",
        end_date="cast('2026-01-01' as date)"
    ) }}

),

festivals as (

    select festival_name, festival_date, is_major
    from {{ ref('festival_calendar') }}

),

festival_windows as (

    -- for each day, the festival whose window it falls in (the major / nearest one if two overlap)
    select
        d.date_day,
        f.festival_name,
        f.is_major
    from days as d
    inner join festivals as f
        on d.date_day between dateadd(day, -10, f.festival_date) and f.festival_date
    qualify row_number() over (
        partition by d.date_day
        order by f.is_major desc, f.festival_date asc
    ) = 1

)

select
    d.date_day                                         as date_day,
    year(d.date_day)                                   as year,
    quarter(d.date_day)                                as quarter,
    month(d.date_day)                                  as month,
    monthname(d.date_day)                              as month_name,
    to_char(d.date_day, 'YYYY-MM')                     as year_month,
    date_trunc('month', d.date_day)                    as month_start_date,
    weekofyear(d.date_day)                             as week_of_year,
    dayofweekiso(d.date_day)                           as day_of_week,       -- 1 = Monday ... 7 = Sunday
    dayname(d.date_day)                                as day_name,
    dayofweekiso(d.date_day) in (6, 7)                 as is_weekend,
    month(d.date_day) between 6 and 9                  as is_monsoon,
    fd.festival_name                                   as festival_name,     -- only on the festival day
    fd.festival_name is not null                       as is_festival_day,
    fw.festival_name                                   as festival_window_name,
    fw.festival_name is not null                       as is_festival_window,
    coalesce(fw.is_major, false)                       as is_major_festival_window
from days as d
left join festivals as fd
    on d.date_day = fd.festival_date
left join festival_windows as fw
    on d.date_day = fw.date_day
