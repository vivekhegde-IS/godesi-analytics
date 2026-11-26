{#
    safe_divide(numerator, denominator)
    Divides without the "Division by zero" error: returns NULL when the denominator is 0 or NULL.
    Used for every ratio (AOV, margin %, uplift %, days of cover) so the rule lives in one place.
    Example:  {{ safe_divide('net_revenue_inr', 'orders') }}
          ->  (net_revenue_inr) / nullif((orders), 0)
#}
{% macro safe_divide(numerator, denominator) -%}
    ({{ numerator }}) / nullif(({{ denominator }}), 0)
{%- endmacro %}
