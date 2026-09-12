import time
import requests
import pandas as pd
from .config import MFAPI_BASE_URL, MFAPI_TIMEOUT, MFAPI_MAX_RETRIES, LIVE_NAV_DAYS

def _fetch_one(amfi_code):
    url = MFAPI_BASE_URL.format(amfi_code=amfi_code)
    last_error = None

    for attempt in range(MFAPI_MAX_RETRIES + 1):
        try:
            response = requests.get(url, timeout=MFAPI_TIMEOUT)
            response.raise_for_status()
            rows = response.json().get("data", [])
            if not rows:
                return pd.DataFrame(columns=["amfi_code", "date", "nav", "source"])

            df = pd.DataFrame(rows)
            df["date"] = pd.to_datetime(df["date"], format="%d-%m-%Y", errors="coerce")
            df["nav"] = pd.to_numeric(df["nav"], errors="coerce")
            df = df.dropna(subset=["date", "nav"])

            cutoff = pd.Timestamp.today().normalize() - pd.Timedelta(days=LIVE_NAV_DAYS)
            df = df[df["date"] >= cutoff].copy()
            df["amfi_code"] = int(amfi_code)
            df["source"] = "live"
            return df[["amfi_code", "date", "nav", "source"]]

        except Exception as exc:
            last_error = exc
            if attempt < MFAPI_MAX_RETRIES:
                time.sleep(0.5 * (attempt + 1))

    print(f"MFAPI skipped {amfi_code}: {last_error}")
    return pd.DataFrame(columns=["amfi_code", "date", "nav", "source"])

def fetch_live_nav(amfi_codes):
    frames = []
    for code in dict.fromkeys(int(x) for x in amfi_codes):
        df = _fetch_one(code)
        if not df.empty:
            frames.append(df)

    if not frames:
        return pd.DataFrame(columns=["amfi_code", "date", "nav", "source"])

    return (
        pd.concat(frames, ignore_index=True)
        .drop_duplicates(["amfi_code", "date"], keep="last")
        .sort_values(["amfi_code", "date"])
        .reset_index(drop=True)
    )
