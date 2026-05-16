"""Deterministic synthetic property / lease tables (student + BFR-style operating narrative).

Public positioning reflected at a HIGH LEVEL ONLY (education + multifamily ecosystems inspired by
published Core Spaces marketing)—all numbers remain synthetic and unofficial.
"""

from __future__ import annotations

from dataclasses import dataclass

import numpy as np
import pandas as pd

from cs_portfolio.config import DATASET_VERSION_DEFAULT, bronze_dir, ensure_dirs


@dataclass(frozen=True)
class SyntheticConfig:
    random_seed: int = 42
    n_properties: int = 36
    n_leases: int = 5200


# Portfolio narrative (ASCII-friendly names; PBIP-ready)
_ECOSYSTEMS = ("student_housing_pad", "btr_single_family_lot", "hybrid_corner")

_BRAND_LINE_POOL = (
    # Nods to layered / concentric vitality without claiming trademarked marks
    "LivStripe-O synthetic",
    "HarbourGlow synthetic",
    "TapestryBands synthetic",
    "SignalLoop synthetic",
    "MetroHalo synthetic",
)

_FLAGSHIP_STYLE = ("urban_highrise", "wrap_garden", "cottage_cluster", "townhome_strip")

_METRO_CLUSTER = ("major_msa_hub", "college_city_corridor", "sunbelt_launch", "growth_infill")

_METROS_STUDENT = ["Austin", "Columbus", "Denver", "Chicago", "Bloomington", "Madison", "Tempe corridor"]
_METROS_BTR = ["Nashville", "Orlando", "Phoenix", "Denver", "Columbus", "Austin", "Chicago"]

_ADJECTIVE = [
    "Meridian",
    "Harbour",
    "Brightline",
    "Tapestry",
    "Piedmont",
    "Catalyst",
    "Nova",
    "Waypoint",
    "Alto",
]
_SUFFIX = ["Courts", "Quarter", "District", "Park", "Terrace", "Walk", "Flats"]


def build_synthetic_tables(cfg: SyntheticConfig | None = None) -> dict[str, pd.DataFrame]:
    cfg = cfg or SyntheticConfig()
    rng = np.random.default_rng(cfg.random_seed)

    eco = rng.choice(np.array(list(_ECOSYSTEMS)), size=cfg.n_properties, p=[0.55, 0.30, 0.15])
    flagship = rng.choice(np.array(list(_FLAGSHIP_STYLE)), size=cfg.n_properties)
    brand_line = rng.choice(np.array(list(_BRAND_LINE_POOL)), size=cfg.n_properties)
    metro_cluster = rng.choice(np.array(list(_METRO_CLUSTER)), size=cfg.n_properties)

    metros: list[str] = []
    units_n: list[int] = []
    for e in eco:
        if e == "student_housing_pad":
            metros.append(str(rng.choice(np.array(_METROS_STUDENT))))
            units_n.append(int(rng.integers(220, 720)))
        elif e == "btr_single_family_lot":
            metros.append(str(rng.choice(np.array(_METROS_BTR))))
            units_n.append(int(rng.integers(90, 320)))
        else:
            metros.append(str(rng.choice(np.array(sorted(set(_METROS_STUDENT + _METROS_BTR))))))
            units_n.append(int(rng.integers(160, 480)))

    prop_names = [
        f"{rng.choice(np.array(_ADJECTIVE))} {rng.choice(np.array(_SUFFIX))}" for _ in range(cfg.n_properties)
    ]

    prop = pd.DataFrame(
        {
            "property_id": [f"PROP{i + 1:03d}" for i in range(cfg.n_properties)],
            "property_name": prop_names,
            "metro": metros,
            "ecosystem_segment": eco,
            "brand_line": brand_line,
            "flagship_style": flagship,
            "metro_cluster": metro_cluster,
            "units_count": units_n,
        }
    )

    units: list[dict] = []
    for _, row in prop.iterrows():
        pid = row["property_id"]
        n_u = int(row["units_count"])
        for u in range(n_u):
            if row["ecosystem_segment"] == "btr_single_family_lot":
                bd_w = rng.choice(np.array([2, 3, 4, 5]), p=[0.1, 0.35, 0.42, 0.13])
            elif row["ecosystem_segment"] == "student_housing_pad":
                bd_w = rng.choice(np.array([1, 2, 3, 4]), p=[0.28, 0.48, 0.17, 0.07])
            else:
                bd_w = rng.choice(np.array([1, 2, 3, 4]), p=[0.18, 0.44, 0.28, 0.10])
            units.append(
                {
                    "unit_id": f"{pid}-U{u + 1:04d}",
                    "property_id": pid,
                    "bedrooms": int(bd_w),
                }
            )
    unit = pd.DataFrame(units)

    unit_ids = unit["unit_id"].to_numpy()
    chosen_units = rng.choice(unit_ids, size=cfg.n_leases, replace=True)

    base_start = pd.Timestamp("2021-01-01")
    start_offsets = rng.integers(0, 1400, size=cfg.n_leases)
    lease_start_date = pd.Series(base_start + pd.to_timedelta(start_offsets, unit="D")).dt.normalize()
    tenure_months = rng.integers(6, 26, size=cfg.n_leases)
    as_of_date = pd.Series(pd.to_datetime(lease_start_date) + pd.to_timedelta((tenure_months * 30).astype("int64"), unit="D")).dt.normalize()

    late = rng.poisson(0.82, size=cfg.n_leases)
    work_orders = rng.poisson(1.28, size=cfg.n_leases)
    prior_renewals = rng.integers(0, 5, size=cfg.n_leases)

    prop_df_ix = prop.set_index("property_id")
    pid_for_lease = unit.set_index("unit_id").loc[chosen_units, "property_id"].to_numpy()
    eco_vec = prop_df_ix.loc[pid_for_lease, "ecosystem_segment"].to_numpy()

    rent = rng.normal(1680, 255, size=cfg.n_leases)
    rent = np.where(eco_vec == "btr_single_family_lot", rent + 220, rent)
    rent = np.where(eco_vec == "student_housing_pad", rent - 90, rent)
    rent = rent.clip(650, 5200)

    market_rent = rent * rng.normal(1.0, 0.085, size=cfg.n_leases)
    rent_ratio = (rent / market_rent).clip(0.72, 1.22)

    unit_df = unit.set_index("unit_id")
    prop_df = prop.set_index("property_id")
    bed = unit_df.loc[chosen_units, "bedrooms"].to_numpy()
    pid = unit_df.loc[chosen_units, "property_id"].to_numpy()
    metro = prop_df.loc[pid, "metro"].to_numpy()
    mc = prop_df.loc[pid, "metro_cluster"].to_numpy()

    z = (
        0.14
        - 1.35 * (rent_ratio - 1.0)
        - 0.085 * late
        - 0.042 * work_orders
        + 0.31 * prior_renewals
        + np.where(bed >= 3, 0.16, 0.0)
        + np.where(np.isin(metro, ["Austin", "Denver", "Nashville"]), 0.1, 0.0)
        - 0.03 * np.maximum(0, tenure_months - 14)
        + np.where(eco_vec == "btr_single_family_lot", 0.11, -0.04)
        + np.where(mc == "college_city_corridor", -0.05, 0.02)
    )
    noise = rng.normal(0, 0.52, size=cfg.n_leases)
    p = 1 / (1 + np.exp(-(z + noise)))
    renewed = (rng.uniform(size=cfg.n_leases) < p).astype(np.int8)

    lease = pd.DataFrame(
        {
            "lease_id": [f"L{i + 1:06d}" for i in range(cfg.n_leases)],
            "unit_id": chosen_units,
            "property_id": pid,
            "metro": metro,
            "lease_start_date": lease_start_date.dt.strftime("%Y-%m-%d"),
            "leased_month": lease_start_date.dt.to_period("M").astype(str),
            "as_of_date": as_of_date.dt.strftime("%Y-%m-%d"),
            "tenure_months": tenure_months.astype(np.int16),
            "monthly_rent": np.round(rent, 2),
            "market_rent_proxy": np.round(market_rent, 2),
            "rent_to_market_ratio": np.round(rent_ratio, 4),
            "late_payment_count_12m": late.astype(np.int16),
            "work_order_count_12m": work_orders.astype(np.int16),
            "prior_renewal_count": prior_renewals.astype(np.int16),
            "bedrooms": bed.astype(np.int8),
            "renewed": renewed,
            "synthetic_signal_z": np.round(z, 4),
            "dataset_version_id": DATASET_VERSION_DEFAULT,
        }
    )

    return {"dim_property": prop, "dim_unit": unit, "fact_lease_episode": lease}


def write_bronze_parquet(tables: dict[str, pd.DataFrame]) -> dict[str, str]:
    ensure_dirs()
    out: dict[str, str] = {}
    for name, df in tables.items():
        path = bronze_dir() / f"{name}.parquet"
        df.to_parquet(path, index=False)
        out[name] = str(path)
    return out


def run_synthetic_to_bronze(cfg: SyntheticConfig | None = None) -> dict[str, str]:
    tables = build_synthetic_tables(cfg)
    return write_bronze_parquet(tables)
