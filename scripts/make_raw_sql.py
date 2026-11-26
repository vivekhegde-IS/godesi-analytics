"""
Write the Snowflake SQL that loads the generated CSVs into GODESI_RAW.

Reads the header of every CSV in data/raw/batch1/ and prints, for each one:
CREATE TABLE (all VARCHAR + _source_file + _loaded_at) and COPY INTO.
The COPY reads that file from EVERY batch folder in the stage, so the same
statement loads batch1 now and only the new batch2 file later.

Run from the repo root:
    python scripts/make_raw_sql.py | Out-File -Encoding utf8 setup/raw_generated.sql
"""
import csv
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
BATCH1 = REPO / "data" / "raw" / "batch1"
STAGE = "@GODESI_RAW.ERP.RAW_STAGE"
FILE_FORMAT = "GODESI_RAW.ERP.CSV_FORMAT"

# csv file name -> (schema, table): each file goes to the schema of the system it comes from
TARGETS = {
    "products":                ("ERP", "PRODUCTS"),
    "promotions":              ("ERP", "PROMOTIONS"),
    "distributors":            ("ERP", "DISTRIBUTORS"),
    "stores":                  ("ERP", "STORES"),
    "erp_orders":              ("ERP", "ORDERS"),
    "erp_order_items":         ("ERP", "ORDER_ITEMS"),
    "customers":               ("ECOM", "CUSTOMERS"),
    "ecom_orders":             ("ECOM", "ORDERS"),
    "ecom_order_items":        ("ECOM", "ORDER_ITEMS"),
    "ecom_returns":            ("ECOM", "RETURNS"),
    "marketplace_orders":      ("MARKETPLACE", "ORDERS"),
    "marketplace_order_items": ("MARKETPLACE", "ORDER_ITEMS"),
    "inventory_daily":         ("INVENTORY", "INVENTORY_DAILY"),
}

checks = []
for name, (schema, table) in TARGETS.items():
    path = BATCH1 / f"{name}.csv"
    with open(path, encoding="utf-8", newline="") as f:
        reader = csv.reader(f)
        cols = next(reader)
        n_rows = sum(1 for _ in reader)
    full = f"GODESI_RAW.{schema}.{table}"
    checks.append((full, n_rows))

    print(f"-- {name}.csv -> {full}   ({len(cols)} columns, {n_rows:,} rows in batch1)")
    print(f"CREATE TABLE IF NOT EXISTS {full} (")
    for c in cols:
        print(f"    {c} VARCHAR,")
    print("    _source_file VARCHAR,")
    print("    _loaded_at   TIMESTAMP_NTZ")
    print(");")
    print(f"COPY INTO {full} ({', '.join(cols)}, _source_file, _loaded_at)")
    print("FROM (")
    print("    SELECT " + ", ".join(f"${i}" for i in range(1, len(cols) + 1))
          + ", METADATA$FILENAME, CURRENT_TIMESTAMP()")
    print(f"    FROM {STAGE}")
    print(")")
    # matches batch1/<name>.csv, batch2/<name>.csv ... but not e.g. erp_<name>.csv
    print(f"PATTERN = '.*batch[0-9]+/{name}[.]csv([.]gz)?'")
    print(f"FILE_FORMAT = (FORMAT_NAME = {FILE_FORMAT})")
    print("ON_ERROR = ABORT_STATEMENT;\n")

print("-- VERIFY: row counts after loading batch1 (expected = rows in the batch1 CSVs)")
print("\nUNION ALL\n".join(
    f"SELECT '{full}' AS table_name, COUNT(*) AS actual, {n} AS expected FROM {full}"
    for full, n in checks) + "\nORDER BY table_name;")
