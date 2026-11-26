
"""
Generate synthetic GoDesi sales data (Jan 2024 to Dec 2025).

Built on top of the 9 real GoDesi products found in Open Food Facts.
Everything else (prices, stores, customers, orders, stock) is synthetic.

Run from the repo root:   python scripts/generate_data.py
Output:                   data/raw/batch1/*.csv  (and batch2/ later)
"""
from pathlib import Path

import numpy as np
import pandas as pd
from faker import Faker

# ---------------------------------------------------------------- settings
SEED = 42                                   # same seed -> same data every run
rng = np.random.default_rng(SEED)
fake = Faker("en_IN")                       # Indian names, cities, pincodes
Faker.seed(SEED)

REPO = Path(__file__).resolve().parents[1]              # .../godesi-analytics
OFF_TSV = REPO.parent / "data" / "off_india_raw.tsv"   # the real file, outside the repo
OUT = REPO / "data" / "raw"                             # ignored by git

START = pd.Timestamp("2024-01-01")
END = pd.Timestamp("2025-12-31")


def save(df, name, batch="batch1"):
    """Write one table to data/raw/<batch>/<name>.csv and print its row count."""
    folder = OUT / batch
    folder.mkdir(parents=True, exist_ok=True)
    df.to_csv(folder / f"{name}.csv", index=False)
    print(f"  {batch}/{name}.csv".ljust(36), f"{len(df):>8,} rows")


def price_ending_9(x):
    """Indian retail style: 97.3 -> 99, 241 -> 249."""
    return int(np.ceil(x / 10) * 10 - 1)


# ---------------------------------------------------------------- C1: products
# Details for the 9 real GoDesi products. Open Food Facts has their barcode and
# name, but pack size and price are mostly missing, so these are our assumptions.
REAL_DETAILS = {
    # barcode:        (category,       sub_category,   pack_size_g, mrp_inr)
    "8906108890173": ("Candy & Pops", "Imli Pops",      80,  99),
    "8906108890050": ("Candy & Pops", "Imli Pops",      32,  40),
    "8906108891767": ("Candy & Pops", "Fruit Pops",     80,  99),
    "8906108890005": ("Candy & Pops", "Assorted Pops", 160, 180),
    "8906108893549": ("Candy & Pops", "Ice Pops",      240, 150),
    "8906108893525": ("Mithai",       "Kaju Sweets",   180, 299),
    "8906108893792": ("Mithai",       "Ghee Sweets",   200, 249),
    "8906108895581": ("Mithai",       "Laddu",         200, 349),
    "8906108895147": ("Namkeen",      "Bhel",          150,  99),
}

# 51 synthetic products: 17 per category, in GoDesi's style.
SYNTHETIC = {
    "Candy & Pops": ["Kokum", "Jamun", "Ber", "Amla", "Kala Khatta", "Guava Chilli",
                     "Kacha Aam", "Jaljeera", "Paan", "Chatpata Imli", "Orange Peel",
                     "Gulkand", "Phalsa", "Karonda", "Tamarind Jaggery", "Kesar Aam",
                     "Mixed Fruit"],
    "Mithai":       ["Soan Papdi", "Besan Laddu", "Dharwad Peda", "Kaju Roll",
                     "Coconut Barfi", "Milk Peda", "Badam Halwa", "Motichoor Laddu",
                     "Anjeer Barfi", "Peanut Chikki", "Til Chikki", "Gajak",
                     "Rava Laddu", "Belgaum Kunda", "Kaju Pista Roll", "Dry Fruit Barfi",
                     "Chandrakala"],
    "Namkeen":      ["Masala Peanuts", "Khatta Meetha", "Chakli", "Moong Dal",
                     "Aloo Bhujia", "Madras Mixture", "Kodubale", "Banana Chips",
                     "Ragi Chips", "Nippattu", "Corn Flakes Mixture", "Masala Kaju",
                     "Bhakarwadi", "Sev", "Chana Jor Garam", "Mangalore Mixture",
                     "Avalakki Chivda"],
}
PACK_SIZES = {"Candy & Pops": [32, 80, 160], "Mithai": [200, 250, 400], "Namkeen": [150, 200, 400]}
RS_PER_GRAM = {"Candy & Pops": 1.2, "Mithai": 1.3, "Namkeen": 0.6}   # rough price level


def make_products():
    # 1. find the real GoDesi rows by BRAND (barcode prefix 8906108 is shared with other brands)
    off = pd.read_csv(OFF_TSV, sep="\t", dtype=str,
                      usecols=["code", "product_name", "brands"])
    real = off[off["brands"].str.contains(r"go\s?desi", case=False, na=False)].copy()
    assert len(real) == 9, f"expected 9 GoDesi rows, found {len(real)}"

    rows = []
    for _, r in real.iterrows():
        cat, sub, pack, mrp = REAL_DETAILS[r["code"]]
        name = r["product_name"] if isinstance(r["product_name"], str) else "Desi Popz Assorted"
        rows.append(dict(barcode=r["code"], product_name=name, category=cat, sub_category=sub,
                         pack_size_g=pack, mrp_inr=mrp, is_real_product=True,
                         launch_date=fake.date_between(pd.Timestamp("2019-01-01"), pd.Timestamp("2023-06-30"))))

    # 2. invent the other 51 products
    for cat, names in SYNTHETIC.items():
        for n in names:
            pack = int(rng.choice(PACK_SIZES[cat]))
            mrp = price_ending_9(pack * RS_PER_GRAM[cat] * rng.uniform(0.85, 1.25))
            # 70% launched before the sales period, 30% are new launches during it
            if rng.random() < 0.7:
                launch = fake.date_between(pd.Timestamp("2020-01-01"), pd.Timestamp("2023-12-31"))
            else:
                launch = fake.date_between(START, pd.Timestamp("2025-09-30"))
            sub = "Pops" if cat == "Candy & Pops" else n.split()[-1]
            prefix = "Desi Popz " if cat == "Candy & Pops" else ""
            rows.append(dict(barcode=None, product_name=f"{prefix}{n}", category=cat, sub_category=sub,
                             pack_size_g=pack, mrp_inr=mrp, is_real_product=False, launch_date=launch))

    df = pd.DataFrame(rows)
    df.insert(0, "sku_id", [f"GD-{i:04d}" for i in range(1, len(df) + 1)])
    df["cost_inr"] = (df["mrp_inr"] * rng.uniform(0.45, 0.60, len(df))).round(2)  # 40-55% gross margin
    df["is_active"] = rng.random(len(df)) > 0.05                                  # ~5% discontinued
    df["updated_at"] = pd.to_datetime(df["launch_date"]).dt.strftime("%Y-%m-%d 09:00:00")
    return df


# ---------------------------------------------------------------- main
def main():
    print("Generating GoDesi synthetic data (seed =", SEED, ")")
    products = make_products()
    save(products, "products")
    print("Done.")


if __name__ == "__main__":
    main()