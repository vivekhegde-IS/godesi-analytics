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


# ---------------------------------------------------------------- C2: shared reference data
# Festival dates (reused in C3 for seasonality). Diwali = Lakshmi Puja day.
FESTIVALS = {
    "SANKRANTI":    ["2024-01-15", "2025-01-14"],
    "REPUBLICDAY":  ["2024-01-26", "2025-01-26"],
    "HOLI":         ["2024-03-25", "2025-03-14"],
    "UGADI":        ["2024-04-09", "2025-03-30"],
    "INDEPENDENCE": ["2024-08-15", "2025-08-15"],
    "RAKHI":        ["2024-08-19", "2025-08-09"],
    "GANESHA":      ["2024-09-07", "2025-08-27"],
    "NAVRATRI":     ["2024-10-03", "2025-09-22"],
    "DIWALI":       ["2024-10-31", "2025-10-20"],
    "XMAS":         ["2024-12-25", "2025-12-25"],
}

# Cities GoDesi sells in: (city, state, pincode prefix, weight).
# Weighted to the South, and Karnataka most of all, since GoDesi is a Bengaluru brand.
CITIES = [
    ("Bengaluru", "Karnataka", "560", 22), ("Mysuru", "Karnataka", "570", 5),
    ("Hubballi", "Karnataka", "580", 3), ("Mangaluru", "Karnataka", "575", 3),
    ("Chennai", "Tamil Nadu", "600", 9), ("Coimbatore", "Tamil Nadu", "641", 4),
    ("Hyderabad", "Telangana", "500", 9), ("Kochi", "Kerala", "682", 4),
    ("Thiruvananthapuram", "Kerala", "695", 2), ("Mumbai", "Maharashtra", "400", 9),
    ("Pune", "Maharashtra", "411", 6), ("New Delhi", "Delhi", "110", 8),
    ("Gurugram", "Haryana", "122", 3), ("Ahmedabad", "Gujarat", "380", 4),
    ("Kolkata", "West Bengal", "700", 4), ("Jaipur", "Rajasthan", "302", 3),
    ("Lucknow", "Uttar Pradesh", "226", 2),
]
CITY_DF = pd.DataFrame(CITIES, columns=["city", "state", "pin_prefix", "weight"])
CITY_P = (CITY_DF["weight"] / CITY_DF["weight"].sum()).to_numpy()
PIN_PREFIX = dict(zip(CITY_DF["city"], CITY_DF["pin_prefix"]))


def pick_cities(n):
    """Pick n cities by weight; return a DataFrame with city, state and a matching pincode."""
    idx = rng.choice(len(CITY_DF), size=n, p=CITY_P)
    df = CITY_DF.iloc[idx][["city", "state"]].reset_index(drop=True)
    df["pincode"] = make_pincodes(df["city"])
    return df


def make_pincodes(cities):
    """A 6-digit pincode that starts with the city's real prefix, e.g. Bengaluru -> 560xxx."""
    tail = pd.Series(rng.integers(1, 100, len(cities))).map("{:03d}".format)
    return cities.map(PIN_PREFIX).reset_index(drop=True) + tail


def random_dates(n, start, end):
    """n random dates between start and end (inclusive)."""
    days = (pd.Timestamp(end) - pd.Timestamp(start)).days
    return pd.Timestamp(start) + pd.to_timedelta(rng.integers(0, days + 1, n), unit="D")


# ---------------------------------------------------------------- C2: promotions (30)
def make_promotions():
    rows = []
    # 20 festival promos: start 7 days before the festival, end the day after it
    for name, dates in FESTIVALS.items():
        for d in dates:
            d = pd.Timestamp(d)
            big = name in ("DIWALI", "RAKHI", "HOLI")
            rows.append(dict(promo_code=f"{name}{d:%y}",
                             promo_name=f"{name.title()} {d.year} offer",
                             start_date=d - pd.Timedelta(days=7),
                             end_date=d + pd.Timedelta(days=1),
                             discount_pct=int(rng.choice([15, 20, 25] if big else [5, 10])),
                             channel="all"))
    # 10 non-festival promos: (code, name, start, end, discount %, channel)
    others = [("WELCOME10",  "First order discount",    "2024-01-01", "2025-12-31", 10, "d2c"),
              ("FREESHIP",   "Free shipping above 499", "2024-01-01", "2025-12-31",  5, "d2c"),
              ("MEGASALE24", "Marketplace mega sale",   "2024-09-27", "2024-10-06", 20, "marketplace"),
              ("MEGASALE25", "Marketplace mega sale",   "2025-09-23", "2025-10-02", 20, "marketplace"),
              ("SUMMER24",   "Summer sale",             "2024-07-20", "2024-07-22", 15, "marketplace"),
              ("SUMMER25",   "Summer sale",             "2025-07-12", "2025-07-14", 15, "marketplace"),
              ("MONSOON24",  "Monsoon munchies",        "2024-07-01", "2024-07-31", 10, "quick_commerce"),
              ("MONSOON25",  "Monsoon munchies",        "2025-07-01", "2025-07-31", 10, "quick_commerce"),
              ("NEWYEAR25",  "New year treat",          "2024-12-28", "2025-01-02", 10, "all"),
              ("NEWYEAR26",  "New year treat",          "2025-12-28", "2025-12-31", 10, "all")]
    for code, nm, s, e, pct, ch in others:
        rows.append(dict(promo_code=code, promo_name=nm, start_date=pd.Timestamp(s),
                         end_date=pd.Timestamp(e), discount_pct=pct, channel=ch))
    df = pd.DataFrame(rows)
    for c in ("start_date", "end_date"):
        df[c] = df[c].dt.strftime("%Y-%m-%d")
    return df


# ---------------------------------------------------------------- C2: distributors (40)
def make_distributors(n=40):
    loc = pick_cities(n)
    suffix = rng.choice(["Traders", "Distributors", "Agencies", "Enterprises", "Foods"], n)
    return pd.DataFrame({
        "distributor_id": [f"D-{i:03d}" for i in range(1, n + 1)],
        "distributor_name": [f"{fake.last_name()} {s}" for s in suffix],
        "city": loc["city"],
        "state": loc["state"],
        # most joined before 2024; some join during the period (network growth)
        "onboarded_date": random_dates(n, "2019-01-01", "2025-06-30").strftime("%Y-%m-%d"),
    })


# ---------------------------------------------------------------- C2: stores (2,000)
def make_stores(distributors, n=2000):
    # each store is served by one distributor and sits in that distributor's city
    d = distributors.iloc[rng.integers(0, len(distributors), n)].reset_index(drop=True)
    kind = rng.choice(["kirana", "modern_trade"], n, p=[0.8, 0.2])
    words = {"kirana": ["General Stores", "Kirana", "Provision Store", "Departmental Store"],
             "modern_trade": ["Supermarket", "Mart", "Fresh", "Hypermarket"]}
    # a store joins 0 to 400 days after its distributor, never after the period ends
    onboard = pd.to_datetime(d["onboarded_date"]) + pd.to_timedelta(rng.integers(0, 400, n), unit="D")
    return pd.DataFrame({
        "store_id": [f"S-{i:05d}" for i in range(1, n + 1)],
        "distributor_id": d["distributor_id"],
        "store_name": [f"{fake.last_name()} {rng.choice(words[k])}" for k in kind],
        "store_type": kind,
        "city": d["city"],
        "state": d["state"],
        "pincode": make_pincodes(d["city"]),
        "onboarded_date": onboard.clip(upper=END).dt.strftime("%Y-%m-%d"),
    })


# ---------------------------------------------------------------- C2: customers (30,000)
def make_customers(n=30000):
    loc = pick_cities(n)
    # sign-ups grow over time: the square root puts more of them later in the period
    first_day = pd.Timestamp("2023-06-01")
    span = (END - first_day).days
    signup = first_day + pd.to_timedelta((np.sqrt(rng.random(n)) * span).astype(int), unit="D")
    first = [fake.first_name() for _ in range(n)]
    last = [fake.last_name() for _ in range(n)]
    return pd.DataFrame({
        "customer_id": [f"C-{i:06d}" for i in range(1, n + 1)],
        "first_name": first,
        "last_name": last,
        # example.com is reserved for examples, so these can never be real addresses
        "email": [f"{f.lower()}.{l.lower()}{i}@example.com" for i, (f, l) in enumerate(zip(first, last))],
        "signup_date": signup.strftime("%Y-%m-%d"),
        "city": loc["city"],
        "state": loc["state"],
        "pincode": loc["pincode"],
        "acquisition_source": rng.choice(
            ["instagram", "google_ads", "organic", "referral", "influencer", "marketplace_insert"],
            n, p=[0.28, 0.20, 0.22, 0.12, 0.10, 0.08]),
    })


# ---------------------------------------------------------------- main
def main():
    print("Generating GoDesi synthetic data (seed =", SEED, ")")
    products = make_products()
    save(products, "products")

    promotions = make_promotions()
    save(promotions, "promotions")

    distributors = make_distributors()
    save(distributors, "distributors")

    stores = make_stores(distributors)
    save(stores, "stores")

    customers = make_customers()
    save(customers, "customers")
    print("Done.")


if __name__ == "__main__":
    main()