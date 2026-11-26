{#
    standardize_city(column)
    Cleans a free-text city or state: removes spaces at the ends, collapses double spaces and
    capitalises each word ('  bengaluru ' -> 'Bengaluru', 'NEW  DELHI' -> 'New Delhi').
    Old names (Bangalore -> Bengaluru) are still mapped by the city_name_mapping seed.
    Used by customers, stores and distributors, so all three produce the same spelling
    and join to dim_geography.
#}
{% macro standardize_city(column) -%}
    initcap(regexp_replace(trim({{ column }}), '\\s+', ' '))
{%- endmacro %}
