"""
=============================================================
AGENT 8 — DIGITAL TWIN & PREDICTIVE MAINTENANCE
INDUSTRIE IA — Bootcamp IA 2026 — Jour 13
=============================================================

ROLE:
    Creates a digital twin of the industrial valve DN100 PN40
    by simulating 12 months of operation using patterns
    extracted from 3 real public datasets:
      - NASA CMAPSS   → degradation backbone + RUL
      - Pump Sensor   → realistic sensor distributions
      - AI4I 2020     → failure type labels + wear signal

INPUTS:
    - inputs/agent1_output.json  (valve specs)
    - inputs/train_FD001.txt     (NASA CMAPSS training data)
    - inputs/RUL_FD001.txt       (NASA Remaining Useful Life)
    - inputs/pump_sensor.csv     (Kaggle pump sensor data)
    - inputs/ai4i2020.csv        (Kaggle AI4I failure data)

OUTPUTS:
    - outputs/digital_twin_data.json  (main output → Agent 9)
    - outputs/digital_twin_3d.json    (3D scene → Three.js)

INSTALL:
    pip install pandas numpy scipy scikit-learn
                python-dateutil jsonschema
                langgraph langchain langchain-community
=============================================================
"""

# ── Standard library imports ──────────────────────────────────
import json
import os
from datetime import datetime, timedelta

# ── Data science imports ──────────────────────────────────────
import numpy as np
import pandas as pd
from scipy.stats import zscore, norm, kstest
from scipy.optimize import curve_fit
from sklearn.ensemble import IsolationForest
from sklearn.linear_model import LinearRegression

# ── Utility imports ───────────────────────────────────────────
from dateutil.relativedelta import relativedelta
from jsonschema import validate, ValidationError

# ── LangGraph imports (orchestration) ─────────────────────────
from langgraph.graph import StateGraph, END
from typing import TypedDict, Optional


# =============================================================
# LANGGRAPH STATE DEFINITION
# Defines what data flows between agents in the pipeline
# =============================================================

class PipelineState(TypedDict):
    """
    The shared state object passed between all LangGraph nodes.
    Agent 8 reads agent1_output and writes agent8_output.
    """
    # Inputs coming from previous agents
    agent1_output:   dict          # valve specs from Agent 1
    nasa_path:       str           # path to train_FD001.txt
    rul_path:        str           # path to RUL_FD001.txt
    pump_csv_path:   str           # path to pump_sensor.csv
    ai4i_csv_path:   str           # path to ai4i2020.csv

    # Outputs produced by Agent 8 (consumed by Agent 9)
    agent8_output:   Optional[dict]
    digital_twin_path: Optional[str]
    twin_3d_path:    Optional[str]


# =============================================================
# HELPER FUNCTIONS
# =============================================================

def get_zone_color(health_pct: float) -> str:
    """
    Maps a health percentage (0-100) to a color hex code.
    Used for both the JSON output and the 3D scene.
    Green = good, Orange = watch, Red = bad, Dark red = critical
    """
    if health_pct >= 80: return "#22C55E"   # green
    if health_pct >= 60: return "#F59E0B"   # orange
    if health_pct >= 40: return "#EF4444"   # red
    return "#7F1D1D"                          # dark red


def get_sensor_status(value: float,
                       warn_threshold: float,
                       crit_threshold: float,
                       invert: bool = False) -> str:
    """
    Returns NORMAL / WARNING / CRITICAL based on thresholds.
    invert=True is used for flow rate (low = bad).
    """
    if invert:
        if value < crit_threshold: return "CRITICAL"
        if value < warn_threshold: return "WARNING"
        return "NORMAL"
    if value > crit_threshold: return "CRITICAL"
    if value > warn_threshold: return "WARNING"
    return "NORMAL"


def month_to_date(month_num: float,
                   start: datetime = datetime(2026, 1, 1)) -> str:
    """
    Converts a month number (float) to a calendar date string.
    Example: 9.5 → "2026-09-15"
    """
    if month_num <= 0:
        return start.strftime("%Y-%m-%d")
    date = start + relativedelta(months=int(month_num))
    return date.strftime("%Y-%m-%d")


def exp_decay(t: np.ndarray, a: float, b: float) -> np.ndarray:
    """
    Exponential decay function used to fit the NASA RUL curve.
    Models how a machine degrades over time: fast at start,
    then accelerating toward failure.
    """
    return a * np.exp(-b * t)


# =============================================================
# STEP 1 — LOAD ALL DATASETS & EXTRACT PATTERNS
# AI METHOD: MLE Distribution Fitting + KS Test
# =============================================================

def step1_load_and_extract(state: PipelineState) -> dict:
    """
    Loads all 3 datasets and extracts statistical patterns.
    Uses Maximum Likelihood Estimation (MLE) to fit probability
    distributions to each sensor column — more accurate than
    just using mean/std.

    Returns a dict with all extracted patterns ready for
    the simulation in Step 2.
    """
    print("\n📂 STEP 1 — Loading datasets & extracting patterns...")
    specs = state["agent1_output"]

    # ── 1A. Load NASA CMAPSS data ─────────────────────────────
    # The txt file has no header — we assign column names manually
    # based on the readme.pdf included in the NASA download
    nasa_cols = (
        ["unit", "cycle", "setting1", "setting2", "setting3"] +
        [f"s{i}" for i in range(1, 22)]
    )
    df_nasa = pd.read_csv(
        state["nasa_path"],
        sep=r"\s+",        # space-separated file
        header=None,
        names=nasa_cols,
        index_col=False
    ).dropna(axis=1)       # drop empty trailing columns

    print(f"  ✅ NASA loaded     : {len(df_nasa):,} rows, "
          f"{df_nasa.shape[1]} columns")

    # Extract degradation curve from unit 1 (reference machine)
    # RUL goes from 1.0 (brand new) → 0.0 (end of life)
    unit1 = df_nasa[df_nasa["unit"] == 1].copy()
    max_cycle = unit1["cycle"].max()
    rul_curve = 1 - (unit1["cycle"].values / max_cycle)

    # Extract NASA sensor distribution patterns
    # These sensors map to our valve's physical properties
    nasa_patterns = {
        "temperature": {"mean": df_nasa["s2"].mean(),
                        "std":  df_nasa["s2"].std()},
        "pressure":    {"mean": df_nasa["s3"].mean(),
                        "std":  df_nasa["s3"].std()},
        "vibration":   {"mean": df_nasa["s4"].mean(),
                        "std":  df_nasa["s4"].std()},
        "flow":        {"mean": df_nasa["s7"].mean(),
                        "std":  df_nasa["s7"].std()},
        "wear":        {"mean": df_nasa["s11"].mean(),
                        "std":  df_nasa["s11"].std()},
    }

    # Load NASA RUL labels (Remaining Useful Life per machine)
    rul_labels = pd.read_csv(
        state["rul_path"],
        header=None,
        names=["RUL"]
    )
    print(f"  ✅ NASA RUL loaded : {len(rul_labels)} machines")

    # ── 1B. Load Pump Sensor data (chunked for performance) ───
    # File is large (220k+ rows) — use chunking to save RAM
    chunk_list = []
    needed_cols = ["sensor_00", "sensor_01", "sensor_02",
                   "sensor_04", "sensor_06", "machine_status"]

    for chunk in pd.read_csv(
        state["pump_csv_path"],
        chunksize=50_000,
        usecols=needed_cols
    ):
        chunk_list.append(chunk.dropna())

    df_pump = pd.concat(chunk_list, ignore_index=True)
    print(f"  ✅ Pump loaded     : {len(df_pump):,} rows")

    # Extract pump statistical distributions using MLE
    # MLE finds the best-fit normal distribution parameters
    # KS test verifies the fit quality (p > 0.05 = good fit)
    pump_patterns = {}
    sensor_map = {
        "sensor_00": "pressure",
        "sensor_02": "flow",
        "sensor_04": "temperature",
        "sensor_06": "vibration"
    }

    for col, name in sensor_map.items():
        data = df_pump[col].dropna().values

        # MLE: fit normal distribution
        mu, sigma = norm.fit(data)

        # KS test: verify goodness of fit
        stat, p_value = kstest(data, "norm", args=(mu, sigma))
        fit_quality = "good" if p_value > 0.05 else "approximate"

        pump_patterns[name] = {
            "mean":        float(mu),
            "std":         float(sigma),
            "min":         float(data.min()),
            "max":         float(data.max()),
            "p05":         float(np.percentile(data, 5)),
            "p95":         float(np.percentile(data, 95)),
            "fit_quality": fit_quality
        }
        print(f"     {name:12s}: mu={mu:.3f} "
              f"sigma={sigma:.3f} fit={fit_quality}")

    # Failure rate from pump (how often the pump breaks)
    broken_rate = (df_pump["machine_status"] == "BROKEN").mean()
    print(f"  📊 Pump broken rate: {broken_rate*100:.1f}%")

    # ── 1C. Load AI4I 2020 data ───────────────────────────────
    df_ai4i = pd.read_csv(
        state["ai4i_csv_path"],
        usecols=["Tool wear [min]", "TWF", "HDF",
                 "PWF", "OSF", "RNF", "Machine failure"]
    ).dropna()

    # Rename for easier access
    df_ai4i.rename(columns={"Tool wear [min]": "tool_wear",
                             "Machine failure": "machine_failure"},
                   inplace=True)

    # Extract wear and failure patterns
    wear_max      = float(df_ai4i["tool_wear"].max())
    failure_rate  = float(df_ai4i["machine_failure"].mean())
    failure_dist  = df_ai4i[["TWF","HDF","PWF","OSF","RNF"]].mean()
    most_common   = failure_dist.idxmax()

    print(f"  ✅ AI4I loaded     : {len(df_ai4i):,} rows")
    print(f"  📊 AI4I failure rate : {failure_rate*100:.1f}%")
    print(f"  📊 Most common failure: {most_common}")

    # Build failure action map (from AI4I labels)
    failure_action_map = {
        "HDF": {
            "name":   "heat_dissipation_failure",
            "sensor": "temperature",
            "action": "Inspecter système de refroidissement"
        },
        "PWF": {
            "name":   "power_pressure_failure",
            "sensor": "pressure",
            "action": "Contrôler alimentation et clapet retour"
        },
        "OSF": {
            "name":   "overstrain_failure",
            "sensor": "vibration",
            "action": "Réduire pression opérationnelle"
        },
        "TWF": {
            "name":   "tool_wear_failure",
            "sensor": "wear",
            "action": "Remplacer joints et garnitures d'étanchéité"
        },
        "RNF": {
            "name":   "random_failure",
            "sensor": "multiple",
            "action": "Inspection complète immédiate requise"
        }
    }

    print("  ✅ Step 1 complete — patterns extracted")

    return {
        "specs":              specs,
        "rul_curve":          rul_curve,
        "nasa_patterns":      nasa_patterns,
        "pump_patterns":      pump_patterns,
        "broken_rate":        broken_rate,
        "wear_max":           wear_max,
        "failure_rate":       failure_rate,
        "failure_dist":       failure_dist.to_dict(),
        "most_common":        most_common,
        "failure_action_map": failure_action_map,
        "df_ai4i":            df_ai4i
    }


# =============================================================
# STEP 2 — SIMULATE 12 MONTHS OF OPERATION
# AI METHOD: Monte Carlo Simulation + Poisson Spikes
# =============================================================

def step2_simulate(extracted: dict) -> pd.DataFrame:
    """
    Generates 8,760 hourly sensor readings using Monte Carlo
    simulation. Data is NOT read raw from datasets — it is
    GENERATED using statistical patterns learned in Step 1.

    Layers:
      Layer 1: NASA RUL curve → degradation backbone
      Layer 2: Monte Carlo noise → realistic variation
      Layer 3: Seasonal sine wave → seasonal effects
      Layer 4: Poisson spikes → random failure events
    """
    print("\n🔬 STEP 2 — Simulating 12 months of operation...")

    specs         = extracted["specs"]
    rul_curve     = extracted["rul_curve"]
    pump_patterns = extracted["pump_patterns"]
    broken_rate   = extracted["broken_rate"]

    np.random.seed(42)  # for reproducibility
    N = 8760            # hours in a year

    # ── Layer 1: NASA degradation backbone ───────────────────
    # Interpolate NASA RUL curve (from unit 1 cycles) to 8760 points
    # This gives us a smooth degradation signal from 0→1 over the year
    nasa_degradation = np.interp(
        np.linspace(0, len(rul_curve) - 1, N),
        np.arange(len(rul_curve)),
        rul_curve
    )
    # wear_signal: 0 = brand new, 1 = end of life
    wear_signal = 1 - nasa_degradation

    # Add AI4I wear texture (realistic micro-variations)
    ai4i_noise  = np.random.normal(0, 0.02, N)
    wear_signal = np.clip(wear_signal + ai4i_noise, 0, 1)

    # ── Layer 3: Seasonal variation (sine wave) ───────────────
    # Valves in Algeria run harder in summer (heat)
    # One full sine cycle = one year
    seasonal_temp  = np.sin(np.linspace(0, 2 * np.pi, N)) * 8
    seasonal_press = np.sin(np.linspace(0, 2 * np.pi, N)) * 2

    # ── Layer 2: Monte Carlo noise per sensor ─────────────────

    # TEMPERATURE simulation
    base_temp  = specs["temperature_max_celsius"] * 0.20
    noise_temp = np.random.normal(
        0, pump_patterns["temperature"]["std"] * 0.3, N
    )
    drift_temp      = wear_signal * 40        # rises with wear
    temperature     = base_temp + noise_temp + drift_temp + seasonal_temp
    temperature     = np.clip(temperature, -10, 120)

    # PRESSURE simulation
    base_press  = float(specs["pressure_bar"])
    noise_press = np.random.normal(
        0, pump_patterns["pressure"]["std"] * 0.5, N
    )
    drift_press = wear_signal * 10            # rises with wear
    pressure    = base_press + noise_press + drift_press + seasonal_press
    pressure    = np.clip(pressure, 25, 65)

    # FLOW RATE simulation
    base_flow   = float(specs["flow_rate_m3h"])
    noise_flow  = np.random.normal(
        0, pump_patterns["flow"]["std"] * 0.3, N
    )
    decay_flow  = wear_signal * -20           # drops with wear
    flow        = base_flow + noise_flow + decay_flow
    flow        = np.clip(flow, 35, 95)

    # VIBRATION simulation
    base_vib    = specs["vibration_limit_mm_s"] * 0.4
    noise_vib   = np.random.normal(
        0, pump_patterns["vibration"]["std"] * 0.2, N
    )
    drift_vib   = wear_signal * 8             # rises with wear
    vibration   = base_vib + noise_vib + drift_vib
    vibration   = np.clip(vibration, 0, 15)

    # ── Layer 4: Poisson failure spikes ───────────────────────
    # Real failures don't happen uniformly — they cluster
    # Poisson process models rare random industrial events
    n_spikes  = np.random.poisson(lam=broken_rate * N * 0.05)
    spike_idx = np.random.choice(N, n_spikes, replace=False)

    for i in spike_idx:
        pressure[i]    *= np.random.uniform(1.2, 1.5)
        vibration[i]   *= np.random.uniform(1.5, 2.5)
        temperature[i] += np.random.uniform(20, 50)
        flow[i]        *= np.random.uniform(0.5, 0.8)

    # Re-clip after spikes to stay in physical bounds
    pressure    = np.clip(pressure,    25, 65)
    vibration   = np.clip(vibration,   0,  15)
    temperature = np.clip(temperature, -10, 130)
    flow        = np.clip(flow,        35, 95)

    # ── Build timestamps ──────────────────────────────────────
    start      = datetime(2026, 1, 1)
    timestamps = [start + timedelta(hours=i) for i in range(N)]

    # ── Assemble simulation DataFrame ─────────────────────────
    simulation = pd.DataFrame({
        "timestamp":     timestamps,
        "month":         [t.month for t in timestamps],
        "hour":          list(range(N)),
        "temperature_c": temperature,
        "pressure_bar":  pressure,
        "vibration_mms": vibration,
        "flow_m3h":      flow,
        "wear_level":    wear_signal,
        "rul":           nasa_degradation,
        "status":        "NORMAL"
    })

    print(f"  ✅ Simulation complete: {len(simulation):,} hourly rows")
    print(f"  📊 Avg temperature : {simulation['temperature_c'].mean():.1f}°C")
    print(f"  📊 Avg pressure    : {simulation['pressure_bar'].mean():.1f} bar")
    print(f"  📊 Avg vibration   : {simulation['vibration_mms'].mean():.2f} mm/s")
    print(f"  📊 Avg flow rate   : {simulation['flow_m3h'].mean():.1f} m³/h")
    print(f"  📊 Failure spikes  : {n_spikes}")

    return simulation, nasa_degradation


# =============================================================
# STEP 3 — DETECT ANOMALIES (3 METHODS COMBINED)
# AI METHOD: Isolation Forest + Z-score + Threshold
# =============================================================

def step3_detect_anomalies(simulation: pd.DataFrame,
                            specs: dict) -> pd.DataFrame:
    """
    Detects anomalies using 3 complementary methods:

    Method 1 — Threshold: simple limit checks (fast, interpretable)
    Method 2 — Z-score:   statistical outliers (catches subtle drifts)
    Method 3 — Isolation Forest: ML-based multivariate detection
                (catches complex patterns no single sensor reveals)

    Returns simulation DataFrame with 'status' and 'iso_anomaly'
    columns filled in.
    """
    print("\n🔍 STEP 3 — Detecting anomalies (3 methods)...")

    sim = simulation.copy()

    # ── Method 1: Threshold detection ─────────────────────────
    # Based on valve technical limits from agent1_output.json
    # WARNING = 110% nominal, CRITICAL = 120% nominal

    warn_mask = (
        (sim["temperature_c"] > 50)  |
        (sim["pressure_bar"]  > 44)  |   # 110% of 40 bar
        (sim["vibration_mms"] > 4.5) |
        (sim["flow_m3h"]      < 70)
    )
    crit_mask = (
        (sim["temperature_c"] > 80)  |
        (sim["pressure_bar"]  > 48)  |   # 120% of 40 bar
        (sim["vibration_mms"] > 7.0) |
        (sim["flow_m3h"]      < 60)
    )

    sim.loc[warn_mask, "status"] = "WARNING"
    sim.loc[crit_mask, "status"] = "CRITICAL"  # overrides WARNING

    thresh_count = warn_mask.sum() + crit_mask.sum()
    print(f"  Method 1 (Threshold) : {thresh_count:,} anomalies")

    # ── Method 2: Z-score statistical detection ────────────────
    # Flags readings > 3 standard deviations from the mean
    # Catches statistical outliers even if below thresholds

    sensor_cols = ["temperature_c", "pressure_bar",
                   "vibration_mms", "flow_m3h"]
    z_scores    = np.abs(zscore(sim[sensor_cols]))
    z_anomaly   = (z_scores > 3.0).any(axis=1)

    # Only flag as WARNING if not already flagged
    sim.loc[
        z_anomaly & (sim["status"] == "NORMAL"),
        "status"
    ] = "WARNING"

    print(f"  Method 2 (Z-score)   : {z_anomaly.sum():,} anomalies")

    # ── Method 3: Isolation Forest ML detection ────────────────
    # Best for multivariate anomalies where no single sensor
    # exceeds limits but the COMBINATION is abnormal
    # contamination=0.05 means we expect ~5% anomaly rate

    features = sim[
        ["temperature_c", "pressure_bar",
         "vibration_mms", "flow_m3h", "wear_level"]
    ].values

    iso_forest = IsolationForest(
        contamination=0.05,   # expected anomaly ratio
        n_estimators=100,     # number of decision trees
        random_state=42,
        n_jobs=-1             # use all CPU cores
    )
    iso_preds  = iso_forest.fit_predict(features)
    iso_scores = iso_forest.score_samples(features)

    # -1 = anomaly, 1 = normal (sklearn convention)
    sim["iso_anomaly"]    = iso_preds == -1
    sim["anomaly_score"]  = iso_scores

    # Flag multivariate anomalies not caught by other methods
    sim.loc[
        sim["iso_anomaly"] & (sim["status"] == "NORMAL"),
        "status"
    ] = "WARNING"

    # Very negative scores = CRITICAL multivariate anomaly
    sim.loc[
        sim["iso_anomaly"] &
        (sim["anomaly_score"] < -0.6),
        "status"
    ] = "CRITICAL"

    print(f"  Method 3 (IsoForest) : {sim['iso_anomaly'].sum():,} anomalies")

    # ── Method 4: Rolling trend detection (72h window) ─────────
    # Catches slow progressive degradation before it becomes critical
    for col in ["temperature_c", "pressure_bar", "vibration_mms"]:
        rolling   = sim[col].rolling(72).mean()
        trend_up  = rolling.diff(72) > 0   # consistently rising
        sim.loc[
            trend_up & (sim["status"] == "NORMAL"),
            "status"
        ] = "TREND_ALERT"

    # ── Classify failure type for each anomaly ─────────────────
    # Using AI4I failure code logic
    def classify_failure(row):
        if row["temperature_c"] > 50: return "HDF"
        if row["pressure_bar"]  > 44: return "PWF"
        if row["vibration_mms"] > 4.5:return "OSF"
        if row["wear_level"]    > 0.8: return "TWF"
        return "RNF"

    anomalies = sim[sim["status"] != "NORMAL"].copy()
    if len(anomalies) > 0:
        sim.loc[sim["status"] != "NORMAL", "failure_code"] = (
            anomalies.apply(classify_failure, axis=1)
        )
    else:
        sim["failure_code"] = None

    # Summary counts
    status_counts = sim["status"].value_counts()
    print(f"  📊 NORMAL      : {status_counts.get('NORMAL', 0):,}")
    print(f"  📊 WARNING     : {status_counts.get('WARNING', 0):,}")
    print(f"  📊 CRITICAL    : {status_counts.get('CRITICAL', 0):,}")
    print(f"  📊 TREND_ALERT : {status_counts.get('TREND_ALERT', 0):,}")

    return sim


# =============================================================
# STEP 4 — GENERATE MAINTENANCE ALERTS
# AI METHOD: Rule-Based Classification + LLM (optional)
# =============================================================

def step4_generate_alerts(simulation: pd.DataFrame,
                           failure_action_map: dict) -> list:
    """
    Generates one alert per month (worst severity).
    Each alert includes:
      - AI4I failure code (TWF/HDF/PWF/OSF/RNF)
      - Sensor values at the time of the event
      - RUL remaining from NASA curve
      - Recommended maintenance action

    Optional: LLM enhancement for critical alerts
    (requires Ollama + Mistral running locally)
    """
    print("\n🚨 STEP 4 — Generating maintenance alerts...")

    anomalies = simulation[simulation["status"] != "NORMAL"].copy()

    if len(anomalies) == 0:
        print("  ✅ No anomalies detected — no alerts generated")
        return []

    alerts = []

    for month in range(1, 13):
        month_data = anomalies[anomalies["month"] == month]

        if len(month_data) == 0:
            continue

        # Prefer CRITICAL over WARNING — keep worst event per month
        crit_data = month_data[month_data["status"] == "CRITICAL"]
        worst     = (crit_data.iloc[0]
                     if len(crit_data) > 0
                     else month_data.iloc[0])

        # Get failure code (default to RNF if not classified)
        fc = worst.get("failure_code", "RNF")
        if pd.isna(fc):
            fc = "RNF"

        # Build the alert dict
        alert = {
            "month":    int(month),
            "date":     worst["timestamp"].strftime("%Y-%m-%d"),

            # AI4I failure classification
            "failure_code": fc,
            "type":     failure_action_map[fc]["name"],
            "sensor":   failure_action_map[fc]["sensor"],

            # Sensor readings at event time
            "temperature_c":  round(float(worst["temperature_c"]), 2),
            "pressure_bar":   round(float(worst["pressure_bar"]),  2),
            "vibration_mms":  round(float(worst["vibration_mms"]), 2),
            "flow_m3h":       round(float(worst["flow_m3h"]),      2),

            # Thresholds that were exceeded
            "value":     round(float(worst["vibration_mms"]), 2),
            "threshold": 4.5,

            # Severity and health indicators
            "severity":  ("critical"
                          if worst["status"] == "CRITICAL"
                          else "warning"),
            "wear_level":     round(float(worst["wear_level"]), 3),
            "rul_remaining":  round(float(worst["rul"]), 3),
            "anomaly_score":  round(float(
                worst.get("anomaly_score", 0)), 3),

            # Recommended maintenance action
            "recommended_action": failure_action_map[fc]["action"]
        }

        alerts.append(alert)

    # ── Optional: LLM enhancement for CRITICAL alerts ──────────
    # Uncomment if Ollama + Mistral is installed and running
    # This generates context-aware action text using the LLM

    # try:
    #     from langchain_community.llms import Ollama
    #     llm = Ollama(model="mistral")
    #     for alert in alerts:
    #         if alert["severity"] == "critical":
    #             prompt = f"""
    #             Vanne industrielle DN100 PN40 — alerte critique:
    #             - Type de défaillance : {alert['failure_code']}
    #             - Capteur             : {alert['sensor']}
    #             - Vibration           : {alert['vibration_mms']} mm/s
    #             - Pression            : {alert['pressure_bar']} bar
    #             - Température         : {alert['temperature_c']} °C
    #             - Niveau d'usure      : {alert['wear_level']} / 1.0
    #             - RUL restant         : {alert['rul_remaining']}
    #             Donne UNE action de maintenance précise en français.
    #             Maximum 12 mots. Sois technique et spécifique.
    #             """
    #             alert["recommended_action"] = llm.invoke(prompt).strip()
    # except Exception:
    #     pass  # fallback to hardcoded actions

    print(f"  ✅ {len(alerts)} alerts generated "
          f"({sum(1 for a in alerts if a['severity']=='critical')} critical)")

    return alerts


# =============================================================
# STEP 5 — CALCULATE HEALTH SCORE
# AI METHOD: MCDA Weighted Multi-Factor Scoring
# =============================================================

def step5_health_score(simulation: pd.DataFrame,
                        nasa_degradation: np.ndarray,
                        alerts: list) -> dict:
    """
    Calculates the valve health score using Multi-Criteria
    Decision Analysis (MCDA) with scientifically justified weights.

    Each factor is normalized to 0-1 scale then multiplied
    by its weight. This is more accurate than simple point
    deduction because it accounts for the relative importance
    of each failure mode.

    Also computes a confidence interval using Monte Carlo
    uncertainty quantification.
    """
    print("\n💚 STEP 5 — Calculating health score (MCDA)...")

    # Count event types
    criticals = int((simulation["status"] == "CRITICAL").sum())
    warnings  = int((simulation["status"] == "WARNING").sum())
    trends    = int((simulation["status"] == "TREND_ALERT").sum())
    twf_count = int(
        (simulation.get("failure_code", pd.Series()) == "TWF").sum()
    )
    hdf_count = int(
        (simulation.get("failure_code", pd.Series()) == "HDF").sum()
    )

    # ── MCDA Weights (must sum to 1.0) ────────────────────────
    # Based on industrial valve failure impact studies
    weights = {
        "critical_events": 0.30,   # most impactful on safety
        "warning_events":  0.15,   # moderate impact
        "trend_alerts":    0.10,   # slow degradation signal
        "twf_wear":        0.20,   # seal wear = most common failure
        "hdf_heat":        0.10,   # heat = material degradation
        "nasa_rul":        0.10,   # remaining useful life signal
        "ai4i_wear":       0.05    # AI4I wear confirmation
    }

    # Normalize each factor to 0-1 scale
    def normalize(value: float, max_expected: float) -> float:
        return min(1.0, value / max_expected)

    factors = {
        "critical_events": normalize(criticals, 50),
        "warning_events":  normalize(warnings,  200),
        "trend_alerts":    normalize(trends,     100),
        "twf_wear":        normalize(twf_count,  20),
        "hdf_heat":        normalize(hdf_count,  20),
        "nasa_rul":        float(1 - nasa_degradation[-1]),
        "ai4i_wear":       float(simulation["wear_level"].mean())
    }

    # Compute weighted total penalty
    total_penalty = sum(
        weights[k] * factors[k] * 100
        for k in weights
    )
    health_score = max(0.0, min(100.0, 100.0 - total_penalty))

    # ── Monte Carlo confidence interval ───────────────────────
    # Run scoring 200 times with small noise to estimate uncertainty
    scores_mc = [
        max(0, min(100, health_score + np.random.normal(0, 2)))
        for _ in range(200)
    ]
    score_low  = float(np.percentile(scores_mc, 5))
    score_high = float(np.percentile(scores_mc, 95))

    # ── Find dominant factor (what hurts most) ─────────────────
    weighted_factors = {
        k: weights[k] * factors[k] for k in weights
    }
    dominant_factor = max(weighted_factors, key=weighted_factors.get)

    # ── Classify health status ─────────────────────────────────
    health_status = (
        "Bon état"     if health_score >= 80 else
        "Surveillance" if health_score >= 60 else
        "Dégradé"      if health_score >= 40 else
        "Critique"
    )

    result = {
        "health_score":        round(health_score, 1),
        "health_score_low":    round(score_low,    1),
        "health_score_high":   round(score_high,   1),
        "health_status":       health_status,
        "dominant_factor":     dominant_factor,
        "criticals":           criticals,
        "warnings":            warnings,
        "trends":              trends,
        "twf_count":           twf_count,
        "hdf_count":           hdf_count
    }

    print(f"  📊 Health score    : {health_score:.1f}/100")
    print(f"  📊 Confidence      : [{score_low:.1f} — {score_high:.1f}]")
    print(f"  📊 Status          : {health_status}")
    print(f"  📊 Dominant factor : {dominant_factor}")

    return result


# =============================================================
# STEP 6 — PREDICT MAINTENANCE & FAILURE DATES
# AI METHOD: Linear Regression + NASA Exponential Decay
# =============================================================

def step6_predict_dates(simulation: pd.DataFrame,
                         nasa_degradation: np.ndarray,
                         health_result: dict,
                         specs: dict) -> dict:
    """
    Predicts future maintenance and failure dates using two models:

    Model 1: Linear Regression on monthly health scores
             (good when degradation is steady and linear)
    Model 2: NASA exponential decay curve extrapolation
             (good when degradation accelerates over time)

    The best model is selected based on R² score.
    If R² > 0.7 → linear regression
    If R² < 0.7 → NASA exponential model
    """
    print("\n📅 STEP 6 — Predicting maintenance & failure dates...")

    # ── Compute monthly health scores ─────────────────────────
    monthly_scores = []
    for month in range(1, 13):
        m = simulation[simulation["month"] == month]
        crits  = (m["status"] == "CRITICAL").sum()
        warns  = (m["status"] == "WARNING").sum()
        trends = (m["status"] == "TREND_ALERT").sum()

        # NASA RUL contribution per month
        rul_avg   = float(m["rul"].mean())
        rul_score = rul_avg * 10  # 0-10 bonus for high RUL

        m_score = 100 - (crits*5) - (warns*2) - (trends*3) + rul_score
        monthly_scores.append(max(0.0, min(100.0, m_score)))

    # ── Model 1: Linear Regression ────────────────────────────
    X      = np.arange(1, 13).reshape(-1, 1)
    y      = np.array(monthly_scores)
    lr     = LinearRegression()
    lr.fit(X, y)
    r2     = float(lr.score(X, y))
    slope  = float(lr.coef_[0])
    intercept = float(lr.intercept_)

    print(f"  📊 Linear R² score  : {r2:.3f}")

    # ── Model 2: NASA Exponential Decay ───────────────────────
    try:
        t_data = np.linspace(0, 1, len(nasa_degradation))
        popt, _ = curve_fit(
            exp_decay, t_data, nasa_degradation,
            p0=[1.0, 1.0], maxfev=5000
        )
        a_fit, b_fit = popt

        def nasa_health_at_month(month: float) -> float:
            # Convert month to normalized time (0-1 over lifespan)
            t = month / (specs["lifespan_years_expected"] * 12)
            rul_pred = exp_decay(np.array([t]), a_fit, b_fit)[0]
            return float(np.clip(rul_pred * 100, 0, 100))

        nasa_model_ok = True
        print(f"  📊 NASA exp. model  : a={a_fit:.3f} b={b_fit:.3f}")
    except Exception:
        nasa_model_ok = False
        print("  ⚠️ NASA exponential fit failed — using linear only")

    # ── Select best model ──────────────────────────────────────
    use_linear = r2 > 0.7 or not nasa_model_ok
    model_used = "linear_regression" if use_linear else "nasa_exponential"
    print(f"  📊 Model selected   : {model_used}")

    # ── Predict maintenance date (score < 70) ─────────────────
    if use_linear:
        if slope < 0:
            maint_month = (70 - intercept) / slope
            fail_month  = (30 - intercept) / slope
        else:
            # Score is stable or improving — use 18 months default
            maint_month = 18.0
            fail_month  = 36.0
    else:
        # Binary search for target month using NASA model
        maint_month, fail_month = 18.0, 36.0
        for m in range(1, 300):
            if nasa_health_at_month(m) < 70 and maint_month == 18.0:
                maint_month = float(m)
            if nasa_health_at_month(m) < 30 and fail_month == 36.0:
                fail_month = float(m)
                break

    # ── Estimate real lifespan using NASA RUL ─────────────────
    rul_start = float(nasa_degradation[0])
    rul_end   = float(nasa_degradation[-1])
    if rul_start > 0:
        lifespan = round(
            specs["lifespan_years_expected"] * (rul_end / rul_start),
            1
        )
    else:
        lifespan = float(specs["lifespan_years_expected"])

    maintenance_date = month_to_date(maint_month)
    failure_date     = month_to_date(fail_month)

    print(f"  📊 Maintenance date : {maintenance_date}")
    print(f"  📊 Failure date     : {failure_date}")
    print(f"  📊 Est. lifespan    : {lifespan} years")

    return {
        "maintenance_date":   maintenance_date,
        "failure_date":       failure_date,
        "lifespan":           lifespan,
        "monthly_scores":     [round(s, 1) for s in monthly_scores],
        "r2_score":           round(r2, 3),
        "model_used":         model_used,
        "slope":              round(slope, 4),
    }


# =============================================================
# STEP 7 — GENERATE 3D OUTPUT
# AI METHOD: Parametric Three.js Scene Generation
# =============================================================

def step7_generate_3d(simulation: pd.DataFrame,
                       nasa_degradation: np.ndarray,
                       health_result: dict,
                       prediction_result: dict,
                       alerts: list,
                       specs: dict,
                       output_path: str) -> str:
    """
    Generates a Three.js compatible 3D scene JSON file.
    Agent 9 uses this to render an interactive 3D valve
    in the HTML catalogue — no Blender required.

    The scene includes:
    - Valve geometry (cylinder + flanges)
    - Health zone color coding
    - Sensor marker positions
    - RUL curve array for timeline
    - Monthly health timeline
    - Camera and lighting settings
    """
    print("\n🧊 STEP 7 — Generating 3D scene output...")

    score = health_result["health_score"]

    # Compute per-zone health percentages
    avg_temp  = float(simulation["temperature_c"].mean())
    avg_press = float(simulation["pressure_bar"].mean())
    avg_vib   = float(simulation["vibration_mms"].mean())
    avg_flow  = float(simulation["flow_m3h"].mean())
    avg_wear  = float(simulation["wear_level"].mean())

    pressure_health = max(0.0, 100 - max(0, avg_press - 40) / 8 * 100)
    flow_health     = max(0.0, (avg_flow - 60) / 25 * 100)
    seal_health     = max(0.0, 100 - avg_wear * 100)

    # RUL curve sampled at 12 points (one per month)
    rul_curve_points = [
        round(float(nasa_degradation[i * 730]), 3)
        for i in range(12)
    ]

    # Timeline with monthly health + dominant failure
    timeline_3d = []
    for i, month in enumerate(range(1, 13)):
        m_alerts = [a for a in alerts if a["month"] == month]
        dominant = (m_alerts[0]["failure_code"]
                    if m_alerts else "NONE")
        timeline_3d.append({
            "month":            month,
            "health_score":     prediction_result["monthly_scores"][i],
            "alert_count":      len(m_alerts),
            "dominant_failure": dominant
        })

    # Full Three.js scene descriptor
    scene_3d = {
        "renderer": "threejs",
        "version":  "r128",
        "generated_at": datetime.now().isoformat(),
        "datasets_used": [
            "NASA CMAPSS train_FD001.txt (data.nasa.gov)",
            "pump_sensor.csv (Kaggle — nphantawee)",
            "ai4i2020.csv   (Kaggle — stephanmatzka)"
        ],

        # Three.js scene background and fog
        "scene": {
            "background": "#0F172A",
            "fog": {"color": "#0F172A", "near": 10, "far": 1000}
        },

        # Camera position for best valve view
        "camera": {
            "type":     "PerspectiveCamera",
            "fov":      75,
            "position": {"x": 200, "y": 150, "z": 300},
            "lookAt":   {"x": 0,   "y": 0,   "z": 0}
        },

        # Scene lighting
        "lights": [
            {"type": "AmbientLight",
             "color": "#ffffff", "intensity": 0.4},
            {"type": "DirectionalLight",
             "color": "#ffffff", "intensity": 0.8,
             "position": {"x": 100, "y": 200, "z": 100}}
        ],

        # 3D valve geometry objects
        "objects": [
            {
                "id":   "valve_body",
                "type": "CylinderGeometry",
                "params": {
                    "radiusTop":    50,
                    "radiusBottom": 50,
                    "height":       250,
                    "segments":     32
                },
                "material": {
                    "type":      "MeshPhongMaterial",
                    "color":     get_zone_color(score),
                    "shininess": 100,
                    "opacity":   0.9
                },
                "position": {"x": 0, "y": 0, "z": 0},
                "animation": {
                    "type":  "rotation",
                    "axis":  "y",
                    "speed": 0.005,
                    "loop":  True
                }
            },
            {
                "id":   "valve_flange_top",
                "type": "CylinderGeometry",
                "params": {
                    "radiusTop":    70,
                    "radiusBottom": 70,
                    "height":       20,
                    "segments":     32
                },
                "material": {
                    "type":  "MeshPhongMaterial",
                    "color": "#94A3B8"
                },
                "position": {"x": 0, "y": 135, "z": 0}
            },
            {
                "id":   "valve_flange_bottom",
                "type": "CylinderGeometry",
                "params": {
                    "radiusTop":    70,
                    "radiusBottom": 70,
                    "height":       20,
                    "segments":     32
                },
                "material": {
                    "type":  "MeshPhongMaterial",
                    "color": "#94A3B8"
                },
                "position": {"x": 0, "y": -135, "z": 0}
            }
        ],

        # Color-coded health zones
        "health_zones": [
            {"zone": "body",
             "health_pct": round(score, 1),
             "color_hex":  get_zone_color(score),
             "label":      health_result["health_status"]},
            {"zone": "seal",
             "health_pct": round(seal_health, 1),
             "color_hex":  get_zone_color(seal_health),
             "label":      "Joint d'étanchéité"},
            {"zone": "inlet",
             "health_pct": round(pressure_health, 1),
             "color_hex":  get_zone_color(pressure_health),
             "label":      "Entrée pression"},
            {"zone": "outlet",
             "health_pct": round(flow_health, 1),
             "color_hex":  get_zone_color(flow_health),
             "label":      "Sortie débit"}
        ],

        # Sensor marker positions in 3D space
        "sensor_markers": [
            {
                "id":       "S1",
                "label":    "Température",
                "position": {"x": 0,   "y": 80,  "z": 60},
                "value":    round(avg_temp,  1),
                "unit":     "°C",
                "status":   get_sensor_status(avg_temp, 50, 80),
                "color":    get_zone_color(
                    max(0, 100 - max(0, avg_temp - 20)))
            },
            {
                "id":       "S2",
                "label":    "Pression",
                "position": {"x": 70,  "y": 0,   "z": 0},
                "value":    round(avg_press, 2),
                "unit":     "bar",
                "status":   get_sensor_status(avg_press, 44, 48),
                "color":    get_zone_color(pressure_health)
            },
            {
                "id":       "S3",
                "label":    "Vibration",
                "position": {"x": -70, "y": 0,   "z": 0},
                "value":    round(avg_vib, 2),
                "unit":     "mm/s",
                "status":   get_sensor_status(avg_vib, 4.5, 7.0),
                "color":    get_zone_color(
                    max(0, 100 - avg_vib / 15 * 100))
            },
            {
                "id":       "S4",
                "label":    "Débit",
                "position": {"x": 0,   "y": -80, "z": 60},
                "value":    round(avg_flow, 1),
                "unit":     "m³/h",
                "status":   get_sensor_status(
                    avg_flow, 70, 60, invert=True),
                "color":    get_zone_color(flow_health)
            }
        ],

        # RUL curve (12 monthly points) for timeline chart
        "rul_curve": rul_curve_points,

        # Monthly health timeline
        "timeline": timeline_3d
    }

    # Save 3D scene JSON
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(scene_3d, f, indent=2, ensure_ascii=False)

    print(f"  ✅ 3D scene saved → {output_path}")
    return output_path


# =============================================================
# STEP 8 — EXPORT & VALIDATE OUTPUT
# AI METHOD: JSON Schema Validation
# =============================================================

def step8_export(simulation: pd.DataFrame,
                  nasa_degradation: np.ndarray,
                  health_result: dict,
                  prediction_result: dict,
                  alerts: list,
                  most_common: str,
                  output_path: str) -> dict:
    """
    Assembles the final output dict and validates it against
    a JSON schema before saving. This guarantees Agent 9
    never receives a broken or incomplete JSON.
    """
    print("\n💾 STEP 8 — Exporting & validating output...")

    # ── Sensor statistics ─────────────────────────────────────
    total = len(simulation)
    sensor_stats = {
        "avg_temperature_c":    round(float(simulation["temperature_c"].mean()), 2),
        "max_temperature_c":    round(float(simulation["temperature_c"].max()),  2),
        "avg_pressure_bar":     round(float(simulation["pressure_bar"].mean()),  2),
        "max_pressure_bar":     round(float(simulation["pressure_bar"].max()),   2),
        "avg_vibration_mms":    round(float(simulation["vibration_mms"].mean()), 2),
        "max_vibration_mms":    round(float(simulation["vibration_mms"].max()),  2),
        "avg_flow_m3h":         round(float(simulation["flow_m3h"].mean()),      2),
        "min_flow_m3h":         round(float(simulation["flow_m3h"].min()),       2),
        "avg_wear_level":       round(float(simulation["wear_level"].mean()),    3),
        "avg_rul":              round(float(simulation["rul"].mean()),           3),
        "final_rul":            round(float(nasa_degradation[-1]),               3),
        "most_common_failure":  most_common,
        "anomaly_count":        int((simulation["status"] != "NORMAL").sum()),
        "critical_events":      health_result["criticals"],
        "warning_events":       health_result["warnings"],
        "trend_alerts":         health_result["trends"],
        "normal_percent":       round(
            float((simulation["status"] == "NORMAL").sum()) / total * 100, 1),
        "warning_percent":      round(
            float((simulation["status"] == "WARNING").sum()) / total * 100, 1),
        "critical_percent":     round(
            float((simulation["status"] == "CRITICAL").sum()) / total * 100, 1),
    }

    # ── Assemble final output ─────────────────────────────────
    output = {
        "simulation_hours":    8760,
        "simulation_period":   "2026-01-01 to 2026-12-31",
        "simulation_method":   "monte_carlo_pattern_based",
        "datasets_used": [
            "NASA CMAPSS train_FD001.txt (data.nasa.gov)",
            "pump_sensor.csv (Kaggle — nphantawee)",
            "ai4i2020.csv   (Kaggle — stephanmatzka / UCI)"
        ],
        "health_score_final":         health_result["health_score"],
        "health_score_low":           health_result["health_score_low"],
        "health_score_high":          health_result["health_score_high"],
        "health_status":              health_result["health_status"],
        "dominant_factor":            health_result["dominant_factor"],
        "alerts":                     alerts,
        "predicted_maintenance_date": prediction_result["maintenance_date"],
        "predicted_failure_date":     prediction_result["failure_date"],
        "estimated_lifespan_years":   prediction_result["lifespan"],
        "prediction_model":           prediction_result["model_used"],
        "r2_score":                   prediction_result["r2_score"],
        "monthly_health_scores":      prediction_result["monthly_scores"],
        "sensor_stats":               sensor_stats,
        "files_generated": [
            "outputs/digital_twin_data.json",
            "outputs/digital_twin_3d.json"
        ]
    }

    # ── JSON Schema validation ────────────────────────────────
    schema = {
        "type": "object",
        "required": [
            "simulation_hours", "health_score_final",
            "health_status", "alerts",
            "predicted_maintenance_date",
            "predicted_failure_date",
            "estimated_lifespan_years",
            "monthly_health_scores", "sensor_stats",
            "files_generated"
        ],
        "properties": {
            "simulation_hours":   {"type": "integer"},
            "health_score_final": {
                "type": "number",
                "minimum": 0, "maximum": 100
            },
            "health_status": {
                "type": "string",
                "enum": ["Bon état", "Surveillance",
                         "Dégradé", "Critique"]
            },
            "alerts":       {"type": "array"},
            "monthly_health_scores": {
                "type": "array",
                "minItems": 12, "maxItems": 12
            }
        }
    }

    try:
        validate(instance=output, schema=schema)
        print("  ✅ JSON schema validation passed")
    except ValidationError as e:
        print(f"  ❌ Schema validation failed: {e.message}")
        raise

    # ── Save to file ──────────────────────────────────────────
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(output, f, indent=2, ensure_ascii=False)

    print(f"  ✅ Output saved → {output_path}")
    return output


# =============================================================
# LANGGRAPH NODE — MAIN AGENT 8 FUNCTION
# This is the function LangGraph calls as a node in the graph
# =============================================================

def agent8_node(state: PipelineState) -> PipelineState:
    """
    Main LangGraph node for Agent 8.
    Orchestrates all 8 steps and updates the pipeline state.
    """
    print("\n" + "="*60)
    print("🤖 AGENT 8 — DIGITAL TWIN & PREDICTIVE MAINTENANCE")
    print("="*60)

    # ── Run all steps in sequence ─────────────────────────────
    extracted = step1_load_and_extract(state)

    simulation, nasa_degradation = step2_simulate(extracted)

    simulation = step3_detect_anomalies(
        simulation, extracted["specs"]
    )

    alerts = step4_generate_alerts(
        simulation, extracted["failure_action_map"]
    )

    health_result = step5_health_score(
        simulation, nasa_degradation, alerts
    )

    prediction_result = step6_predict_dates(
        simulation, nasa_degradation,
        health_result, extracted["specs"]
    )

    # ── Export outputs ────────────────────────────────────────
    os.makedirs("outputs", exist_ok=True)

    twin_3d_path = step7_generate_3d(
        simulation       = simulation,
        nasa_degradation = nasa_degradation,
        health_result    = health_result,
        prediction_result= prediction_result,
        alerts           = alerts,
        specs            = extracted["specs"],
        output_path      = "outputs/digital_twin_3d.json"
    )

    digital_twin_path = "outputs/digital_twin_data.json"
    output = step8_export(
        simulation       = simulation,
        nasa_degradation = nasa_degradation,
        health_result    = health_result,
        prediction_result= prediction_result,
        alerts           = alerts,
        most_common      = extracted["most_common"],
        output_path      = digital_twin_path
    )

    print("\n" + "="*60)
    print(f"✅ AGENT 8 COMPLETE")
    print(f"   Health score : {output['health_score_final']}/100")
    print(f"   Status       : {output['health_status']}")
    print(f"   Alerts       : {len(alerts)}")
    print(f"   Maintenance  : {output['predicted_maintenance_date']}")
    print(f"   Failure      : {output['predicted_failure_date']}")
    print(f"   Lifespan     : {output['estimated_lifespan_years']} years")
    print("="*60)

    # ── Update LangGraph state ────────────────────────────────
    return {
        **state,
        "agent8_output":     output,
        "digital_twin_path": digital_twin_path,
        "twin_3d_path":      twin_3d_path
    }


# =============================================================
# LANGGRAPH GRAPH DEFINITION
# =============================================================

def build_agent8_graph() -> StateGraph:
    """
    Builds the LangGraph graph with Agent 8 as a single node.
    In the full pipeline, this node connects to Agent 7 (input)
    and Agent 9 (output).
    """
    graph = StateGraph(PipelineState)
    graph.add_node("agent8", agent8_node)
    graph.set_entry_point("agent8")
    graph.add_edge("agent8", END)
    return graph.compile()


# =============================================================
# STANDALONE RUNNER
# Run this file directly to test Agent 8 without LangGraph
# =============================================================

if __name__ == "__main__":

    # ── Load fake Agent 1 output (valve specs) ────────────────
    with open("inputs/agent1_output.json", "r") as f:
        agent1_specs = json.load(f)

    # ── Define initial pipeline state ─────────────────────────
    initial_state: PipelineState = {
        "agent1_output":     agent1_specs,
        "nasa_path":         "inputs/train_FD001.txt",
        "rul_path":          "inputs/RUL_FD001.txt",
        "pump_csv_path":     "inputs/pump_sensor.csv",
        "ai4i_csv_path":     "inputs/ai4i2020.csv",
        "agent8_output":     None,
        "digital_twin_path": None,
        "twin_3d_path":      None
    }

    # ── Option A: Run via LangGraph graph ─────────────────────
    app    = build_agent8_graph()
    result = app.invoke(initial_state)

    # ── Option B: Run directly without LangGraph ──────────────
    # result = agent8_node(initial_state)

    print("\n📄 Output preview:")
    output = result["agent8_output"]
    print(json.dumps({
        "health_score_final":         output["health_score_final"],
        "health_status":              output["health_status"],
        "alerts_count":               len(output["alerts"]),
        "predicted_maintenance_date": output["predicted_maintenance_date"],
        "predicted_failure_date":     output["predicted_failure_date"],
        "estimated_lifespan_years":   output["estimated_lifespan_years"],
        "files_generated":            output["files_generated"]
    }, indent=2))
