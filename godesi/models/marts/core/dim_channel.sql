-- Channel dimension. Grain: one row per platform (where the order was placed).

select
    platform,
    channel,
    channel_group,
    is_online
from {{ ref('channel_mapping') }}
