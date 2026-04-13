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


def generate_json(data: PipelineData, output_path: str, extra_meta: dict = None) -> str:
    """
    Génère le catalogue en JSON.

    Args:
        data: PipelineData validé
        output_path: chemin du fichier .json à créer
        extra_meta: métadonnées supplémentaires (LLM)
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

    # ── Version Client-Facing (Améliorée avec Points & Tables) ─────────────────
    client_facing = {
        "1_executive_summary": {
            "product_name": data.agent1.part_name,
            "commercial_highlights": extra_meta.get("description_points") if extra_meta else ["Industrial quality"],
            "final_total_price_usd": data.agent6.total_purchase_usd,
            "delivery_time": f"{data.agent5.delivery_days} Days",
            "strategic_value": extra_meta.get("value_points") if extra_meta else ["High ROI"]
        },
        "2_product_overview": {
            "use_cases_and_context": extra_meta.get("explanation_points") if extra_meta else ["Fluid control"],
            "operational_context": "Validated for heavy-duty industrial integration."
        },
        "3_detailed_specifications": {
            "material": data.agent1.material,
            "dimensions": {
                "diameter_mm": data.agent1.diameter_mm,
                "weight_kg": data.agent1.weight_kg,
                "tolerance_mm": data.agent1.tolerance_mm
            },
            "performance_limits": {
                "max_pressure_bar": data.agent1.pressure_bar,
                "max_temp_celsius": data.agent1.temperature_max_celsius,
                "max_flow_m3h": data.agent1.flow_rate_m3h
            },
            "expected_service_life_years": data.agent1.lifespan_years_expected
        },
        "4_visual_and_media": {
            "media_assets": [
                data.agent3.files_generated[0] if data.agent3 and data.agent3.files_generated else "",
                data.agent2.files_generated[0] if data.agent2 and data.agent2.files_generated else ""
            ]
        },
        "5_pricing": {
            "unit_price_usd": data.agent6.unit_cost_usd,
            "quantity": data.agent6.quantity_units,
            "final_total_price_usd": data.agent6.total_purchase_usd,
            "pricing_statement": "All inclusive (materials, manufacturing, logistics)"
        },
        "6_production_and_delivery": {
            "timeline_days": data.agent5.delivery_days,
            "fulfillment_status": "Priority scheduling upon validation."
        },
        "7_supplier_decision": {
            "assigned_network": "Certified high-reliability industrial manufacturing network"
        },
        "8_maintenance_summary": {
            "standard_interval_months": "6-9 months",
            "lifecycle_recommendation": "Engineered for minimal downtime and predictive maintenance compatibility."
        },
        "9_client_value_justification": {
            "benefits": extra_meta.get("value_points") if extra_meta else ["Quality assurance"]
        },
        "10_next_step": {
            "call_to_action": "Confirm procurement to initiate immediate manufacturing cycle"
        }
    }

    # ── Assembler les versions dans un seul fichier ──────────────────────
    output = {
        "catalogue_version": "1.1",
        "generated_at": data.agent8.simulation_period.split(" to ")[0] if data.agent8 else "2026-01-01",
        "product_id": data.agent1.part_id,
        "commercial_catalogue": client_facing
    }

    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(output, f, ensure_ascii=False, indent=2)

    print(f"  [JSON] ✓ Généré → {output_path}")
    return output_path