# Component 1 feature engineering - shared by training and inference (imported by the saved pipelines).
import numpy as np
import pandas as pd

CATEGORICAL = ["product_variant", "line_id", "machine_id", "shift", "crew_team", "source_region", "blanching_method",
               "pack_format", "extraction_method", "event_context", "monsoon_season", "batch_size_category"]
DRYER_WATER_CAPACITY_KG = {"DRY-A": 1650.0, "DRY-C": 1450.0, "DRY-B": 1900.0}
MAINT_INTERVAL_DAYS = {"DRY-A": 35, "DRY-C": 30, "DRY-B": 40, "PRS-1": 28, "PRS-2": 28, "EXP-1": 21, "EXP-2": 21, "CFG-1": 30}
ENGINEERED = ["lab_kernel_fat_pct_db", "feed_fat_pct_est", "fat_input_kg", "dryer_load_index", "dryer_overload", "wear_ratio_sq",
              "fat_to_target_ratio", "dk_moisture_dev_sq", "night_or_evening_shift", "heavy_rain_week", "nut_price_per_mn_nuts",
              "lab_moisture_x_immature"]


def _num(d, c):
    if c in d.columns:
        return pd.to_numeric(d[c], errors="coerce").astype(float)
    return pd.Series(np.nan, index=d.index, dtype=float)


def add_features(df):
    d = df.copy()
    for c in d.columns:
        if c in CATEGORICAL:
            d[c] = d[c].astype(object).where(d[c].notna(), "Unknown").astype(str)
        elif d[c].dtype == object or str(d[c].dtype) in ("string", "str"):
            conv = pd.to_numeric(d[c], errors="coerce")
            if conv.notna().sum() >= d[c].notna().sum():
                d[c] = conv
    for c in CATEGORICAL:
        if c not in d.columns:
            d[c] = "Unknown"
    machine = d["machine_id"].astype(str)
    feed, moist = _num(d, "product_specific_feed_kg"), _num(d, "lab_kernel_moisture_pct")
    cap = machine.map(DRYER_WATER_CAPACITY_KG).astype(float)
    d["dryer_load_index"] = feed * (moist + 1.2 - 2.5) / 100.0 / cap
    d["dryer_overload"] = (d["dryer_load_index"] - 1.0).clip(lower=0)
    interval = machine.map(MAINT_INTERVAL_DAYS).astype(float)
    d["wear_ratio_sq"] = (_num(d, "days_since_maintenance") / interval) ** 2
    d["fat_to_target_ratio"] = _num(d, "lab_kernel_fat_pct_wb") / _num(d, "target_fat_pct")
    d["dk_moisture_dev_sq"] = (_num(d, "feed_moisture_pct") - 7.2) ** 2
    d["night_or_evening_shift"] = d["shift"].isin(["Night", "Evening"]).astype(int)
    d["heavy_rain_week"] = (_num(d, "rain_7d_mm") > 100).astype(int)
    d["nut_price_per_mn_nuts"] = _num(d, "retail_nut_price_lkr_lag1m") / _num(d, "national_coconut_prod_mn_nuts_lag2m")
    fat_wb = _num(d, "lab_kernel_fat_pct_wb")
    d["lab_kernel_fat_pct_db"] = fat_wb / (1 - moist / 100.0)
    fm = _num(d, "feed_moisture_pct")
    d["feed_fat_pct_est"] = np.where(fm.notna(), d["lab_kernel_fat_pct_db"] * (1 - fm / 100.0), fat_wb)
    d["fat_input_kg"] = feed * d["feed_fat_pct_est"] / 100.0
    d["lab_moisture_x_immature"] = moist * _num(d, "immature_nut_pct")
    return d
