-- Returns of delivered online order lines: one row per return_id.

with source as (

    select * from {{ source('ecom', 'returns') }}

),

renamed as (

    select
        return_id,
        order_item_id,
        try_to_timestamp_ntz(return_ts, 'YYYY-MM-DD HH24:MI:SS') as returned_at,
        lower(trim(reason))                   as return_reason,
        try_to_number(refund_inr, 10, 2)      as refund_inr,
        _source_file,
        _loaded_at
    from source

)

select * from renamed
