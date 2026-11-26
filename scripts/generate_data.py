
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
    print(f"  {batch}/{name}.csv".ljust(42), f"{len(df):>8,} rows")


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


# ---------------------------------------------------------------- C3: sales settings
N_ORDERS = 80_000

# channel -> (share of orders, platforms within the channel and their shares)
CHANNELS = {
    "marketplace":    (0.40, {"amazon": 0.55, "flipkart": 0.45}),
    "quick_commerce": (0.25, {"blinkit": 0.45, "zepto": 0.35, "instamart": 0.20}),
    "d2c":            (0.15, {"godesi.in": 1.0}),
    "offline":        (0.20, {"distributor": 1.0}),
}
# how much busier the days just before each festival are (1.0 = normal day)
FESTIVAL_BOOST = {"DIWALI": 2.6, "RAKHI": 2.0, "HOLI": 1.8, "NAVRATRI": 1.4, "GANESHA": 1.4,
                  "SANKRANTI": 1.3, "UGADI": 1.3, "XMAS": 1.3, "INDEPENDENCE": 1.1, "REPUBLICDAY": 1.1}
MONTH_FACTOR = {1: 1.0, 2: 0.95, 3: 1.05, 4: 1.0, 5: 0.95,
                6: 0.85, 7: 0.80, 8: 0.85, 9: 0.90,          # monsoon dip
                10: 1.15, 11: 1.15, 12: 1.10}


def day_weights():
    """One weight per day: growth x month x weekend x festival. Bigger weight = more orders."""
    days = pd.date_range(START, END, freq="D")
    growth = np.linspace(1.0, 1.6, len(days))                      # the business grows ~60% over 2 years
    month = days.month.map(MONTH_FACTOR).to_numpy()
    weekend = np.where(days.day_of_week >= 5, 1.15, 1.0)
    festival = np.ones(len(days))
    for name, dates in FESTIVALS.items():
        for d in dates:
            # the 10 days before a festival and the day itself get the boost
            window = (days >= pd.Timestamp(d) - pd.Timedelta(days=10)) & (days <= pd.Timestamp(d))
            festival[window] = np.maximum(festival[window], FESTIVAL_BOOST[name])
    w = growth * month * weekend * festival
    return days, w / w.sum(), festival


# ---------------------------------------------------------------- C3: price changes
def make_price_changes(products, n=12):
    """12 products get a price rise once during the period (used for snapshots later)."""
    chosen = products.sample(n, random_state=SEED)
    change_day = random_dates(n, "2024-06-01", "2025-09-30")
    return pd.DataFrame({
        "sku_id": chosen["sku_id"].to_numpy(),
        "old_mrp": chosen["mrp_inr"].to_numpy(),
        "new_mrp": [price_ending_9(m * rng.uniform(1.08, 1.15)) for m in chosen["mrp_inr"]],
        "changed_at": change_day,
    })


def mrp_on(sku_ids, dates, products, price_changes):
    """The MRP that was valid for each (sku, date): new price after the change date, else the old one."""
    mrp = pd.Series(sku_ids).map(products.set_index("sku_id")["mrp_inr"]).to_numpy(dtype=float)
    pc = price_changes.set_index("sku_id")
    for sku, row in pc.iterrows():
        after = (np.asarray(sku_ids) == sku) & (np.asarray(dates) >= row["changed_at"])
        mrp[after] = row["new_mrp"]
    return mrp


# ---------------------------------------------------------------- C3: orders
def make_orders(customers, stores, promotions):
    days, p_day, festival = day_weights()
    n = N_ORDERS

    # 1. when: pick a day by weight, then a time of day (busiest in the evening)
    day_idx = rng.choice(len(days), size=n, p=p_day)
    hour_p = np.array([1, 1, 1, 1, 1, 1, 2, 3, 4, 5, 6, 6, 7, 6, 5, 5, 6, 7, 8, 9, 9, 8, 5, 2], float)
    hour = rng.choice(24, size=n, p=hour_p / hour_p.sum())
    order_ts = (days[day_idx] + pd.to_timedelta(hour, unit="h")
                + pd.to_timedelta(rng.integers(0, 3600, n), unit="s"))

    # 2. which channel and platform
    names = list(CHANNELS)
    channel = rng.choice(names, size=n, p=[CHANNELS[c][0] for c in names])
    platform = np.empty(n, dtype=object)
    for c in names:
        mask = channel == c
        plats = list(CHANNELS[c][1])
        platform[mask] = rng.choice(plats, size=mask.sum(), p=list(CHANNELS[c][1].values()))

    # 3. who: online orders come from customers who had already signed up;
    #    offline orders come from stores that were already onboarded
    cust = customers.sort_values("signup_date").reset_index(drop=True)
    cust_dates = pd.to_datetime(cust["signup_date"]).to_numpy()
    st = stores.sort_values("onboarded_date").reset_index(drop=True)
    store_dates = pd.to_datetime(st["onboarded_date"]).to_numpy()
    order_day = days[day_idx].to_numpy()

    online = channel != "offline"
    n_cust_ok = np.searchsorted(cust_dates, order_day, side="right")    # how many customers existed that day
    n_store_ok = np.searchsorted(store_dates, order_day, side="right")
    customer_id = np.where(online,
                           cust["customer_id"].to_numpy()[(rng.random(n) * np.maximum(n_cust_ok, 1)).astype(int)],
                           None)
    store_id = np.where(~online,
                        st["store_id"].to_numpy()[(rng.random(n) * np.maximum(n_store_ok, 1)).astype(int)],
                        None)

    # 4. promo: ~35% of online orders use a promo that is running that day on that channel
    promos = promotions.assign(start=pd.to_datetime(promotions["start_date"]),
                               end=pd.to_datetime(promotions["end_date"]))
    promo_code = np.full(n, None, dtype=object)
    for i in np.flatnonzero(online & (rng.random(n) < 0.35)):
        d, ch = order_day[i], channel[i]
        ok = promos[(promos["start"] <= d) & (promos["end"] >= d)
                    & promos["channel"].isin(["all", ch])]
        if len(ok):
            promo_code[i] = ok["promo_code"].iloc[rng.integers(len(ok))]

    # 5. status: most are delivered; recent orders are still in progress
    age_days = (END - pd.to_datetime(order_day)).days.to_numpy()
    status = rng.choice(["delivered", "cancelled"], size=n, p=[0.94, 0.06]).astype(object)
    status[(age_days <= 4) & (status == "delivered")] = "shipped"
    status[age_days <= 1] = "placed"
    hours_later = np.select([status == "delivered", status == "shipped", status == "cancelled"],
                            [rng.integers(24, 120, n), rng.integers(6, 24, n), rng.integers(1, 12, n)], 0)
    updated_at = order_ts + pd.to_timedelta(hours_later, unit="h")

    df = pd.DataFrame({"order_ts": order_ts, "channel": channel, "platform": platform,
                       "customer_id": customer_id, "store_id": store_id, "status": status,
                       "promo_code": promo_code, "updated_at": updated_at})
    df = df.sort_values("order_ts").reset_index(drop=True)
    df.insert(0, "order_id", [f"ORD-{i:07d}" for i in range(1, n + 1)])
    df.attrs["festival_by_day"] = pd.Series(festival, index=days)
    return df


# ---------------------------------------------------------------- C3: order items
def sku_weights(products, day, festive):
    """Probability of each SKU on a given day: only launched products; real ones sell more;
    mithai sells much more in festival weeks."""
    launched = pd.to_datetime(products["launch_date"]).to_numpy() <= np.datetime64(day)
    w = np.where(products["is_real_product"], 3.0, 1.0)
    if festive > 1.2:
        w = w * np.where(products["category"] == "Mithai", festive, 1.0)
    w = w * launched
    return w / w.sum()


def make_order_items(orders, products, promotions, price_changes):
    # 1. how many lines per order: 1 to 5 (average about 2.5)
    n_lines = np.minimum(1 + rng.poisson(1.5, len(orders)), 5)
    items = orders.loc[orders.index.repeat(n_lines),
                       ["order_id", "order_ts", "channel", "promo_code"]].reset_index(drop=True)
    items["day"] = items["order_ts"].dt.normalize()

    # 2. which product: sample per day, using that day's SKU probabilities
    festival = orders.attrs["festival_by_day"]
    sku = np.empty(len(items), dtype=object)
    sku_ids = products["sku_id"].to_numpy()
    for day, idx in items.groupby("day").indices.items():
        p = sku_weights(products, day, festival.get(day, 1.0))
        sku[idx] = rng.choice(sku_ids, size=len(idx), p=p)
    items["sku_id"] = sku

    # 3. quantity: shoppers buy 1-3 packs; stores order cases of 6 to 48
    offline = (items["channel"] == "offline").to_numpy()
    qty = np.where(offline, rng.choice([6, 12, 24, 36, 48], len(items)),
                   rng.choice([1, 2, 3], len(items), p=[0.7, 0.2, 0.1]))

    # 4. price: MRP valid on that day; stores pay the trade price (~70% of MRP);
    #    marketplaces sometimes sell a little below MRP
    mrp = mrp_on(items["sku_id"], items["day"], products, price_changes)
    factor = np.where(offline, 0.70,
                      np.where(items["channel"] == "marketplace", rng.choice([1.0, 0.95, 0.9], len(items)), 1.0))
    unit_price = np.round(mrp * factor, 2)

    # 5. discount from the order's promo code
    pct = items["promo_code"].map(promotions.set_index("promo_code")["discount_pct"]).fillna(0).to_numpy()
    discount = np.round(unit_price * qty * pct / 100, 2)

    out = pd.DataFrame({"order_id": items["order_id"], "sku_id": items["sku_id"], "qty": qty,
                        "unit_price_inr": unit_price, "discount_inr": discount})
    out.insert(0, "order_item_id", [f"OI-{i:08d}" for i in range(1, len(out) + 1)])
    return out


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

    # sales: orders and their lines, split by the system they come from
    price_changes = make_price_changes(products)
    orders = make_orders(customers, stores, promotions)
    items = make_order_items(orders, products, promotions, price_changes)

    ts_cols = ["order_ts", "updated_at"]
    orders_out = orders.copy()
    for c in ts_cols:
        orders_out[c] = orders_out[c].dt.strftime("%Y-%m-%d %H:%M:%S")

    source = {"ecom": ["d2c"], "marketplace": ["marketplace", "quick_commerce"], "erp": ["offline"]}
    for system, channels in source.items():
        o = orders_out[orders_out["channel"].isin(channels)]
        save(o, f"{system}_orders")
        save(items[items["order_id"].isin(o["order_id"])], f"{system}_order_items")
    print("Done.")


if __name__ == "__main__":
    main()