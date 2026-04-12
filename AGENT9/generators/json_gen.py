# =============================================================================
# generators/json_gen.py
# Génération du fichier JSON catalogue
#
# On produit deux versions :
#   - Version "hiérarchique" : même structure que le PipelineData Pydantic
#   - Version "flat" : tout à plat, pratique pour les outils BI / dashboards
#
# Les deux sont exportées dans le même fichier JSON avec des clés séparées.
# =============================================================================

import json
from models import PipelineData


def generate_json(data: PipelineData, output_path: str) -> str:
    """
    Génère le catalogue en JSON.

    Args:
        data: PipelineData validé
        output_path: chemin du fichier .json à créer

    Returns:
        Chemin du fichier créé
    """

    # ── Version hiérarchique : dump complet via Pydantic ─────────────────────
    # model_dump() sérialise tous les champs Pydantic en dict Python natif
    hierarchical = data.model_dump()

    # ── Version flat : métriques clés à plat pour BI tools ──────────────────
    flat = {
        # Produit (Agent 1)
        "part_name":                data.agent1.part_name,
        "part_id":                  data.agent1.part_id,
        "material":                 data.agent1.material,
        "diameter_mm":              data.agent1.diameter_mm,
        "pressure_bar":             data.agent1.pressure_bar,
        "weight_kg":                data.agent1.weight_kg,

        # Fournisseur retenu (Agents 4 & 5)
        "supplier_selected":        data.agent5.winner,
        "supplier_country":         data.agent5.winner_country,
        "price_initial_usd":        data.agent5.initial_price_per_kg,
        "price_final_usd":          data.agent5.final_price_per_kg,
        "discount_percent":         data.agent5.discount_percent,
        "delivery_days":            data.agent5.delivery_days,

        # TCO (Agent 6)
        "quantity_units":           data.agent6.quantity_units,
        "tco_total_usd":            data.agent6.inflation_adjusted_total_usd,
        "tco_per_unit_usd":         data.agent6.tco_per_unit_usd,
        "inflation_rate_dz":        data.agent6.inflation_rate_dz_percent,

        # Business Plan (Agent 7)
        "roi_percent":              data.agent7.financials.roi_percent,
        "npv_usd":                  data.agent7.financials.npv_usd,
        "break_even_months":        data.agent7.financials.break_even_months,
        "revenue_year1_usd":        data.agent7.financials.revenue_year1_usd,
        "profit_year1_usd":         data.agent7.financials.profit_year1_usd,

        # Jumeau Numérique (Agent 8)
        "health_score_final":       data.agent8.health_score_final,
        "predicted_maintenance":    data.agent8.predicted_maintenance_date,
        "estimated_lifespan_years": data.agent8.estimated_lifespan_years,
        "critical_alerts_count":    sum(1 for a in data.agent8.alerts if a.severity == "critical"),
    }

    # ── Assembler les deux versions dans un seul fichier ──────────────────────
    output = {
        "catalogue_version": "1.0",
        "pipeline": "INDUSTRIE_IA",
        "agent": 9,
        "summary": flat,           # Vue simplifiée — accès rapide aux KPIs
        "full_data": hierarchical  # Données complètes — tous les agents
    }

    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(output, f, ensure_ascii=False, indent=2)

    print(f"  [JSON] ✓ Généré → {output_path}")
    return output_path