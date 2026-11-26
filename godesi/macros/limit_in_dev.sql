{#
    limit_in_dev(n)
    Adds "limit n" ONLY when running in dev AND the dev_sample variable is switched on:
        dbt build -s stg_off__products+ --vars "{dev_sample: true}"
    Normal runs (and every prod run) are never limited, so tests and totals stay correct.
    Use it on big tables to try out a change in seconds instead of processing every row.
#}
{% macro limit_in_dev(n=1000) -%}
    {%- if target.name == 'dev' and var('dev_sample', false) -%}
    limit {{ n }}
    {%- endif -%}
{%- endmacro %}
