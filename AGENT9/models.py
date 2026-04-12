# =============================================================================
# models.py
# Schémas Pydantic pour valider les données reçues des Agents 1 à 8
# Pydantic v2 — vérifie les types, les valeurs manquantes et les ranges
# =============================================================================

from pydantic import BaseModel, Field
from typing import List, Optional


# ─────────────────────────────────────────────
# Agent 1 — Spécifications du produit
# ─────────────────────────────────────────────
class ProductSpecs(BaseModel):
    part_name: str
    part_id: str
    diameter_mm: float
    pressure_bar: float
    material: str
    weight_kg: float
    tolerance_mm: float
    temperature_max_celsius: float
    flow_rate_m3h: float
    lifespan_years_expected: int


# ─────────────────────────────────────────────
# Agent 2 — Plans CAD générés
# ─────────────────────────────────────────────
class CADOutput(BaseModel):
    files_generated: List[str]
    views: List[str]
    scale: str
    software: str
    generated_at: str


# ─────────────────────────────────────────────
# Agent 3 — Vidéo de présentation
# ─────────────────────────────────────────────
class VideoOutput(BaseModel):
    files_generated: List[str]
    duration_seconds: int
    resolution: str
    fps: int
    software: str
    generated_at: str


# ─────────────────────────────────────────────
# Agent 4 — Sourcing fournisseurs
# ─────────────────────────────────────────────
class Supplier(BaseModel):
    rank: int
    name: str
    country: str
    country_name: str
    material: str
    price_per_kg_usd: float
    lead_time_days: int
    min_order_kg: int
    reliability_score: int = Field(ge=0, le=100)  # doit être entre 0 et 100


class SourcingOutput(BaseModel):
    material_searched: str
    suppliers_found: int
    top_suppliers: List[Supplier]
    data_sources: List[str]


# ─────────────────────────────────────────────
# Agent 5 — Négociation IA
# ─────────────────────────────────────────────
class NegotiationOutput(BaseModel):
    negotiation_rounds: int
    winner: str
    winner_country: str
    initial_price_per_kg: float
    final_price_per_kg: float
    discount_percent: float
    delivery_days: int
    contract_quantity_kg: int
    total_material_cost_usd: float
    transcript_summary: str
    negotiation_status: str


# ─────────────────────────────────────────────
# Agent 6 — TCO (Total Cost of Ownership)
# ─────────────────────────────────────────────
class TCOOutput(BaseModel):
    quantity_units: int
    unit_cost_usd: float
    total_purchase_usd: float
    maintenance_cost_per_year_usd: float
    maintenance_10y_usd: float
    energy_cost_per_year_usd: float
    energy_10y_usd: float
    inflation_rate_dz_percent: float
    inflation_source: str
    subtotal_before_inflation_usd: float
    inflation_adjusted_total_usd: float
    tco_per_unit_usd: float
    currency: str
    horizon_years: int
    files_generated: List[str]


# ─────────────────────────────────────────────
# Agent 7 — Business Plan
# ─────────────────────────────────────────────
class SWOT(BaseModel):
    strengths: List[str]
    weaknesses: List[str]
    opportunities: List[str]
    threats: List[str]


class Financials(BaseModel):
    revenue_year1_usd: float
    revenue_year2_usd: float
    revenue_year3_usd: float
    costs_year1_usd: float
    costs_year2_usd: float
    costs_year3_usd: float
    profit_year1_usd: float
    profit_year2_usd: float
    profit_year3_usd: float
    roi_percent: float
    npv_usd: float
    break_even_months: int
    margin_percent_year1: float


class BusinessPlanOutput(BaseModel):
    company_name: str
    product: str
    swot: SWOT
    financials: Financials
    files_generated: List[str]


# ─────────────────────────────────────────────
# Agent 8 — Jumeau numérique & maintenance
# ─────────────────────────────────────────────
class Alert(BaseModel):
    month: int
    date: str
    type: str
    value: float
    threshold: float
    severity: str  # "critical" | "warning"
    recommended_action: str


class SensorStats(BaseModel):
    avg_temperature_c: float
    avg_pressure_bar: float
    avg_vibration_mm_s: float
    avg_flow_rate_m3h: float
    anomaly_count: int
    critical_events: int


class DigitalTwinOutput(BaseModel):
    simulation_hours: int
    simulation_period: str
    health_score_final: float
    alerts: List[Alert]
    predicted_maintenance_date: str
    predicted_failure_date: str
    estimated_lifespan_years: float
    sensor_stats: SensorStats
    files_generated: List[str]


# ─────────────────────────────────────────────
# Modèle global — agrège tout le pipeline
# C'est ce que reçoit Agent 9 en entrée
# ─────────────────────────────────────────────
class PipelineData(BaseModel):
    agent1: ProductSpecs
    agent2: CADOutput
    agent3: VideoOutput
    agent4: SourcingOutput
    agent5: NegotiationOutput
    agent6: TCOOutput
    agent7: BusinessPlanOutput
    agent8: DigitalTwinOutput