{#
    drop_ci_schema(schema_name)
    Drops the throw-away schema a pull request was built in (e.g. CI_PR_12), with everything in it.
    Called by the CI workflow at the end of every run, even when the build failed:
        dbt run-operation drop_ci_schema --args "{schema_name: CI_PR_12}" --target ci
    Safety: it refuses any schema whose name does not start with CI_PR_, so a typo can never drop
    STAGING, MARTS or your dev schema.
#}
{% macro drop_ci_schema(schema_name) %}
    {%- set name = schema_name | string | upper -%}
    {%- if not name.startswith('CI_PR_') -%}
        {{ exceptions.raise_compiler_error("drop_ci_schema only drops CI_PR_* schemas, not " ~ name) }}
    {%- endif -%}
    {% do run_query("drop schema if exists " ~ target.database ~ "." ~ name ~ " cascade") %}
    {{ log("Dropped schema " ~ target.database ~ "." ~ name, info=True) }}
{% endmacro %}
