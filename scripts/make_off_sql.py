
"""Reads the header of the Open Food Facts TSV and prints the CREATE TABLE and COPY INTO SQL."""
import sys

path = sys.argv[1] if len(sys.argv) > 1 else "../data/off_india_raw.tsv"

with open(path, encoding="utf-8") as f:
    header = f.readline().rstrip("\n").split("\t")

# hyphens are not allowed in unquoted names: energy-kcal_100g -> energy_kcal_100g
cols = [c.replace("-", "_") for c in header]
print(f"-- {len(cols)} columns read from {path}\n")

print("CREATE TABLE IF NOT EXISTS GODESI_RAW.OPEN_FOOD_FACTS.PRODUCTS (")
for c in cols:
    print(f"    {c} VARCHAR,")
print("    _source_file VARCHAR,")
print("    _loaded_at   TIMESTAMP_NTZ")
print(");\n")

print("COPY INTO GODESI_RAW.OPEN_FOOD_FACTS.PRODUCTS (")
print("    " + ", ".join(cols) + ", _source_file, _loaded_at")
print(")")
print("FROM (")
print("    SELECT " + ", ".join(f"${i}" for i in range(1, len(cols) + 1))
      + ", METADATA$FILENAME, CURRENT_TIMESTAMP()")
print("    FROM @GODESI_RAW.ERP.RAW_STAGE/off/")
print(")")
print("FILE_FORMAT = (FORMAT_NAME = GODESI_RAW.OPEN_FOOD_FACTS.OFF_TSV)")
print("ON_ERROR = ABORT_STATEMENT;")