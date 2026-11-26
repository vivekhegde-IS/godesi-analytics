-- Real products sold in India, from Open Food Facts (ODbL licence).
-- Grain: one row per barcode.
-- Keeps ~35 useful columns out of 211 and cleans the real-world mess:
--   * brands: many spellings (Haldiram's / haldirams / Haldiram Snacks Pvt. Ltd.) -> brand_mapping seed
--   * quantity: free text ('500 g', '1kg', '200 gm', '1 Ltr') -> net_quantity + quantity_unit (g or ml)
--   * tags: 'en:' language prefixes removed from the main category
--   * Nutri-Score: 'unknown' / 'not-applicable' -> NULL
--   * nutrition per 100 g: text -> numbers (TRY_TO_DOUBLE)

with source as (

    select * from {{ source('open_food_facts', 'products') }}

),

brand_map as (

    select * from {{ ref('brand_mapping') }}

),

base as (

    select
        code                                                     as barcode,
        nullif(trim(product_name), '')                           as product_name,
        nullif(trim(generic_name), '')                           as generic_name,

        -- brand: take the first brand listed, build a key from letters and digits only
        nullif(trim(split_part(brands, ',', 1)), '')             as brand_raw,
        regexp_replace(lower(split_part(brands, ',', 1)), '[^a-z0-9]', '') as brand_key,
        brands                                                   as brands_all,

        -- quantity: keep the raw text, extract number and unit
        nullif(trim(quantity), '')                               as quantity_raw,
        try_to_double(
            regexp_substr(lower(quantity), '[0-9]+([.][0-9]+)?')
        )                                                        as quantity_number,
        regexp_substr(
            lower(quantity),
            '[0-9.]+ ?(kg|kgs|gms|gm|grams|gram|gr|g|ml|ltr|litre|liter|lt|l|oz)',
            1, 1, 'e', 1
        )                                                        as quantity_unit_raw,
        nullif(trim(serving_size), '')                           as serving_size,

        -- categories
        categories_tags,                                         -- full list, used for the bridge table
        nullif(trim(regexp_replace(main_category_en, '^[a-z]{2}:', '')), '') as main_category,  -- 'en:Imli' -> 'Imli'
        nullif(nullif(lower(pnns_groups_1), 'unknown'), '')      as food_group,
        nullif(nullif(lower(pnns_groups_2), 'unknown'), '')      as food_sub_group,
        labels_tags,

        -- ingredients and scores
        ingredients_text,
        try_to_number(additives_n)                               as additives_count,
        case when lower(nutriscore_grade) in ('a', 'b', 'c', 'd', 'e')
             then upper(nutriscore_grade) end                    as nutriscore_grade,
        try_to_number(nutriscore_score)                          as nutriscore_score,
        try_to_number(nova_group)                                as nova_group,

        -- nutrition per 100 g. Values that are physically impossible (typing errors in
        -- Open Food Facts, e.g. 2000 g sugar per 100 g) become NULL, so they cannot distort averages.
        iff(try_to_double(energy_kcal_100g) between 0 and 900,
            try_to_double(energy_kcal_100g), null)                as energy_kcal_100g,
        iff(try_to_double(fat_100g) between 0 and 100,
            try_to_double(fat_100g), null)                        as fat_100g,
        iff(try_to_double(saturated_fat_100g) between 0 and 100,
            try_to_double(saturated_fat_100g), null)              as saturated_fat_100g,
        iff(try_to_double(carbohydrates_100g) between 0 and 100,
            try_to_double(carbohydrates_100g), null)              as carbohydrates_100g,
        iff(try_to_double(sugars_100g) between 0 and 100,
            try_to_double(sugars_100g), null)                     as sugars_100g,
        iff(try_to_double(fiber_100g) between 0 and 100,
            try_to_double(fiber_100g), null)                      as fiber_100g,
        iff(try_to_double(proteins_100g) between 0 and 100,
            try_to_double(proteins_100g), null)                   as proteins_100g,
        iff(try_to_double(salt_100g) between 0 and 100,
            try_to_double(salt_100g), null)                       as salt_100g,

        -- popularity and data quality
        try_to_number(unique_scans_n)                            as unique_scans,
        try_to_double(completeness)                              as completeness_score,
        image_url,

        -- dates: Unix seconds -> timestamps
        to_timestamp_ntz(try_to_number(created_t))               as created_at,
        to_timestamp_ntz(try_to_number(last_modified_t))         as last_modified_at,

        _source_file,
        _loaded_at

    from source

),

cleaned as (

    select
        b.*,

        -- brand: seed mapping first, otherwise the first listed brand as written
        coalesce(m.brand, b.brand_raw)                           as brand,
        coalesce(m.brand = 'GoDesi', false)                      as is_godesi,

        -- quantity in a standard unit: grams for solids, millilitres for liquids
        case
            when b.quantity_unit_raw in ('kg', 'kgs')                          then b.quantity_number * 1000
            when b.quantity_unit_raw in ('g', 'gm', 'gms', 'gram', 'grams', 'gr') then b.quantity_number
            when b.quantity_unit_raw = 'oz'                                    then round(b.quantity_number * 28.35, 1)
            when b.quantity_unit_raw in ('l', 'lt', 'ltr', 'litre', 'liter')   then b.quantity_number * 1000
            when b.quantity_unit_raw = 'ml'                                    then b.quantity_number
        end                                                      as net_quantity,
        case
            when b.quantity_unit_raw in ('kg', 'kgs', 'g', 'gm', 'gms', 'gram', 'grams', 'gr', 'oz') then 'g'
            when b.quantity_unit_raw in ('l', 'lt', 'ltr', 'litre', 'liter', 'ml')                   then 'ml'
        end                                                      as quantity_unit

    from base as b
    left join brand_map as m
        on b.brand_key = m.brand_key

)

select
    barcode,
    product_name,
    generic_name,
    brand,
    brand_raw,
    brands_all,
    is_godesi,
    quantity_raw,
    net_quantity,
    quantity_unit,
    serving_size,
    main_category,
    food_group,
    food_sub_group,
    categories_tags,
    labels_tags,
    ingredients_text,
    additives_count,
    nutriscore_grade,
    nutriscore_score,
    nova_group,
    energy_kcal_100g,
    fat_100g,
    saturated_fat_100g,
    carbohydrates_100g,
    sugars_100g,
    fiber_100g,
    proteins_100g,
    salt_100g,
    unique_scans,
    completeness_score,
    image_url,
    created_at,
    last_modified_at,
    _source_file,
    _loaded_at
from cleaned
{{ limit_in_dev(1000) }}
