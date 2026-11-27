"""Export the dashboard data from Snowflake (GODESI_ANALYTICS.MARTS, prod) to small CSV files.

The public Streamlit app reads these files, so it works without a Snowflake login and keeps working
after the Snowflake trial ends. The SQL lives in dashboard/streamlit/queries.py (the same queries the
app runs live inside Snowflake). Only aggregated mart data: no customer names, e-mails or pincodes.

Run from the repo root with the project venv (it has the Snowflake connector):
    .venv\\Scripts\\python.exe scripts\\export_marts.py

Connection: read from ~/.dbt/profiles.yml (target "prod": account, user, key pair, role).
Nothing secret is written to the repo.
"""
import sys
from pathlib import Path

import pandas as pd
import snowflake.connector
import yaml

APP_DIR = Path(__file__).resolve().parents[1] / "dashboard" / "streamlit"
sys.path.insert(0, str(APP_DIR))
from queries import QUERIES  # noqa: E402

PROFILE, TARGET = "godesi", "prod"
OUT = APP_DIR / "marts"


def connect():
    profile = yaml.safe_load((Path.home() / ".dbt" / "profiles.yml").read_text())
    t = profile[PROFILE]["outputs"][TARGET]
    return snowflake.connector.connect(
        account=t["account"], user=t["user"], private_key_file=t["private_key_path"],
        role=t["role"], warehouse=t["warehouse"], database=t["database"],
        session_parameters={"QUERY_TAG": "godesi_dashboard_export"},
    )


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    with connect() as conn:
        for name, sql in QUERIES.items():
            cur = conn.cursor()
            cur.execute(sql)
            df = pd.DataFrame(cur.fetchall(), columns=[c[0].lower() for c in cur.description])
            df.to_csv(OUT / f"{name}.csv", index=False)
            print(f"{name:22s} {len(df):6d} rows")
    total = pd.read_csv(OUT / "sales_monthly.csv")["net_revenue_inr"].sum()
    print(f"check: net revenue = {total:,.2f} (expected 187,644,074.79)")


if __name__ == "__main__":
    main()
