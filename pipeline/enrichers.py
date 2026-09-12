import pandas as pd


def build_nav_enriched(data):
    nav = data["nav"].copy()
    if "source" not in nav.columns:
        nav["source"] = "historical"

    nav = nav.sort_values(["amfi_code", "date"]).reset_index(drop=True)

    # Vectorised rolling returns — NaN out rows where the window crosses a
    # fund boundary so we never bleed pct_change across different amfi_codes.
    # pandas 3.0 groupby().apply() drops the group-key column; using
    # vectorised pct_change + boundary masking avoids that entirely.
    grp_change = (nav["amfi_code"] != nav["amfi_code"].shift(1)).fillna(True)

    for periods, col in [
        (1,  "nav_1d_return_pct"),
        (7,  "nav_7d_return_pct"),
        (30, "nav_30d_return_pct"),
    ]:
        ret = nav["nav"].pct_change(periods) * 100

        # Build a mask: True for every row whose look-back window touches a
        # fund boundary (i.e. the first `periods` rows of each group).
        boundary_mask = grp_change.copy()
        for i in range(1, periods):
            boundary_mask = boundary_mask | grp_change.shift(-i, fill_value=False)

        ret[boundary_mask] = float("nan")
        nav[col] = ret

    nav = nav.merge(
        data["funds"][["amfi_code", "category", "plan", "fund_house"]],
        on="amfi_code", how="left", validate="many_to_one",
    )
    return nav.reset_index(drop=True)


def build_performance_enriched(data):
    perf = data["performance"].copy()
    funds = data["funds"][[
        "amfi_code", "launch_date", "benchmark", "sub_category", "risk_category",
    ]]
    latest = data["nav"].groupby("amfi_code")["date"].max().rename("latest_nav_date")
    perf = perf.merge(funds, on="amfi_code", how="left", validate="one_to_one")
    perf = perf.merge(latest, on="amfi_code", how="left", validate="one_to_one")
    perf["alpha_positive"] = perf["alpha"] > 0
    return perf


def build_transactions_enriched(data):
    tx = data["transactions"].copy()
    tx = tx.merge(
        data["funds"][["amfi_code", "category", "fund_house"]],
        on="amfi_code", how="left", validate="many_to_one",
    )
    tx["transaction_month"] = tx["transaction_date"].dt.to_period("M").astype(str)
    return tx


def build_market_summary(data):
    aum = data["aum"].copy()
    aum["month"] = aum["date"].dt.to_period("M").astype(str)
    aum["metric_type"] = "aum"

    sip = data["sip"].copy()
    sip["month"] = sip["month"].dt.to_period("M").astype(str)
    sip["metric_type"] = "sip"

    folio = data["folio"].copy()
    folio["month"] = folio["month"].dt.to_period("M").astype(str)
    folio["metric_type"] = "folio"

    cat = data["category_inflows"].copy()
    cat["month"] = cat["month"].dt.to_period("M").astype(str)
    cat["metric_type"] = "category_inflows"

    return (
        pd.concat([aum, sip, folio, cat], ignore_index=True, sort=False)
        .sort_values(["month", "metric_type"])
        .reset_index(drop=True)
    )


def enrich_all(data):
    benchmark = (
        data["benchmark"]
        .pivot(index="date", columns="index_name", values="close_value")
        .reset_index()
        .sort_values("date")
        .reset_index(drop=True)
    )

    return {
        "funds":         data["funds"],
        "nav":           build_nav_enriched(data),
        "performance":   build_performance_enriched(data),
        "transactions":  build_transactions_enriched(data),
        "holdings":      data["holdings"],
        "market_summary": build_market_summary(data),
        "benchmark":     benchmark,
    }
