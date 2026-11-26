{#
    Where should each model be built?
    - dev  : everything goes to your sandbox (target.schema = DBT_DEV_HEGDE)
    - prod : models go to the schema set in dbt_project.yml (STAGING / INTERMEDIATE / MARTS)
    This replaces dbt's default rule, which would create names like DBT_DEV_HEGDE_STAGING.
#}
{% macro generate_schema_name(custom_schema_name, node) -%}
    {%- if target.name == 'prod' and custom_schema_name is not none -%}
        {{ custom_schema_name | trim | upper }}
    {%- else -%}
        {{ target.schema }}
    {%- endif -%}
{%- endmacro %}