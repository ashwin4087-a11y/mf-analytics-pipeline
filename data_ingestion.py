import argparse
import pandas as pd
from pipeline import loaders, cleaners, enrichers, mfapi_client, writers

def run_pipeline(offline=False):
    print("Loading raw datasets...")
    raw = loaders.load_all()

    print("\nCleaning and validating...")
    clean = cleaners.clean_all(raw)

    if not offline:
        print("\nFetching latest NAV data from MFAPI...")
        live_nav = mfapi_client.fetch_live_nav(clean["funds"]["amfi_code"].tolist())

        if not live_nav.empty:
            historical = clean["nav"].copy()
            historical["source"] = "historical"

            combined = pd.concat([historical, live_nav], ignore_index=True)
            clean["nav"] = (
                combined.sort_values(["amfi_code", "date", "source"])
                .drop_duplicates(["amfi_code", "date"], keep="last")
                .reset_index(drop=True)
            )
            print(f"Added/upserted {len(live_nav):,} live NAV rows.")
        else:
            print("MFAPI returned no live rows; using historical NAV only.")
    else:
        print("\nOffline mode: skipping MFAPI.")

    print("\nBuilding enriched datasets...")
    enriched = enrichers.enrich_all(clean)

    print("\nWriting processed datasets...")
    writers.write_all(enriched)
    return enriched

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--offline", action="store_true")
    args = parser.parse_args()
    run_pipeline(offline=args.offline)
