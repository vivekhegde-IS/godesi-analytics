-- End-of-day stock: one row per snapshot_date, warehouse_id and sku_id.

with source as (

    select * from {{ source('inventory', 'inventory_daily') }}

),

renamed as (

    select
        try_to_date(snapshot_date)            as snapshot_date,
        warehouse_id,
        sku_id,
        try_to_number(on_hand_units)          as on_hand_units,
        _source_file,
        _loaded_at
    from source

)

select * from renamed
