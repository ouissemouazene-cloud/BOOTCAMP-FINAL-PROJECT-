# =============================================================================
# fake_data.py
# Données de test simulant les sorties des Agents 1 à 8
# Dans le vrai pipeline LangGraph, ces données arrivent via le State partagé
# =============================================================================

FAKE_PIPELINE_DATA = {
    "agent1": {
        "part_name": "Vanne Industrielle DN100 PN40",
        "part_id": "VLV-DN100-PN40-316L",
        "diameter_mm": 100,
        "pressure_bar": 40,
        "material": "Inox 316L",
        "weight_kg": 12.5,
        "tolerance_mm": 0.05,
        "temperature_max_celsius": 200,
        "flow_rate_m3h": 85,
        "lifespan_years_expected": 15
    },
    "agent2": {
        "files_generated": [
            "vanne_DN100_plan.dxf",
            "vanne_DN100_model.dwg",
            "vanne_DN100_model.ifc"
        ],
        "views": ["face", "coupe_AA", "detail_joint"],
        "scale": "1:5",
        "software": "ezdxf 1.3.2",
        "generated_at": "2026-04-12T08:30:00Z"
    },
    "agent3": {
        "files_generated": ["vanne_DN100_presentation.mp4"],
        "duration_seconds": 45,
        "resolution": "1920x1080",
        "fps": 30,
        "software": "Blender 4.1 headless",
        "generated_at": "2026-04-12T08:45:00Z"
    },
    "agent4": {
        "material_searched": "Inox 316L",
        "suppliers_found": 12,
        "top_suppliers": [
            {
                "rank": 1,
                "name": "AcierPro SARL",
                "country": "FR",
                "country_name": "France",
                "material": "Inox 316L",
                "price_per_kg_usd": 7.20,
                "lead_time_days": 18,
                "min_order_kg": 500,
                "reliability_score": 92
            },
            {
                "rank": 2,
                "name": "MetallurgIA SpA",
                "country": "IT",
                "country_name": "Italie",
                "material": "Inox 316L",
                "price_per_kg_usd": 6.85,
                "lead_time_days": 25,
                "min_order_kg": 300,
                "reliability_score": 87
            },
            {
                "rank": 3,
                "name": "SteelChina Co.",
                "country": "CN",
                "country_name": "Chine",
                "material": "Inox 316L",
                "price_per_kg_usd": 4.50,
                "lead_time_days": 55,
                "min_order_kg": 1000,
                "reliability_score": 74
            }
        ],
        "data_sources": ["Wikidata", "UN Comtrade", "CSV bootcamp"]
    },
    "agent5": {
        "negotiation_rounds": 3,
        "winner": "AcierPro SARL",
        "winner_country": "FR",
        "initial_price_per_kg": 7.20,
        "final_price_per_kg": 6.48,
        "discount_percent": 10.0,
        "delivery_days": 18,
        "contract_quantity_kg": 2500,
        "total_material_cost_usd": 16200.0,
        "transcript_summary": (
            "Tour 1: offre initiale 7.20$/kg refusée. "
            "Tour 2: contre-offre 6.80$, demande volume 2500kg. "
            "Tour 3: accord final 6.48$/kg avec livraison express 18j."
        ),
        "negotiation_status": "success"
    },
    "agent6": {
        "quantity_units": 200,
        "unit_cost_usd": 1296.00,
        "total_purchase_usd": 259200.00,
        "maintenance_cost_per_year_usd": 5800.00,
        "maintenance_10y_usd": 58000.00,
        "energy_cost_per_year_usd": 1200.00,
        "energy_10y_usd": 12000.00,
        "inflation_rate_dz_percent": 6.8,
        "inflation_source": "World Bank API",
        "subtotal_before_inflation_usd": 329200.00,
        "inflation_adjusted_total_usd": 387450.00,
        "tco_per_unit_usd": 1937.25,
        "currency": "USD",
        "horizon_years": 10,
        "files_generated": ["tco_detail.xlsx"]
    },
    "agent7": {
        "company_name": "OpenIndustry Algérie SARL",
        "product": "Vanne DN100 PN40 — Lot de 200 unités",
        "swot": {
            "strengths": [
                "Matériau premium Inox 316L certifié",
                "Délai de livraison compétitif (18 jours)",
                "Fournisseur européen fiable (score 92/100)"
            ],
            "weaknesses": [
                "Coût unitaire élevé vs concurrents asiatiques",
                "Dépendance fournisseur unique"
            ],
            "opportunities": [
                "Marché algérien de la pétrochimie en croissance",
                "Substitution aux importations européennes",
                "Contrats long terme possible avec raffineries"
            ],
            "threats": [
                "Fluctuation du taux de change DZD/USD",
                "Concurrence prix des producteurs chinois"
            ]
        },
        "financials": {
            "revenue_year1_usd": 520000,
            "revenue_year2_usd": 598000,
            "revenue_year3_usd": 687700,
            "costs_year1_usd": 310000,
            "costs_year2_usd": 340000,
            "costs_year3_usd": 372000,
            "profit_year1_usd": 210000,
            "profit_year2_usd": 258000,
            "profit_year3_usd": 315700,
            "roi_percent": 34.2,
            "npv_usd": 412000,
            "break_even_months": 14,
            "margin_percent_year1": 40.4
        },
        "files_generated": ["business_plan.pdf", "financials.xlsx"]
    },
    "agent8": {
        "simulation_hours": 8760,
        "simulation_period": "2026-01-01 to 2026-12-31",
        "health_score_final": 61.5,
        "alerts": [
            {
                "month": 2,
                "date": "2026-02-15",
                "type": "temperature_spike",
                "value": 58.2,
                "threshold": 50.0,
                "severity": "critical",
                "recommended_action": "Inspection joint d'étanchéité"
            },
            {
                "month": 4,
                "date": "2026-04-01",
                "type": "vibration_anomaly",
                "value": 3.8,
                "threshold": 4.5,
                "severity": "warning",
                "recommended_action": "Vérifier fixations et supports"
            },
            {
                "month": 7,
                "date": "2026-07-04",
                "type": "pressure_drop",
                "value": 52.0,
                "threshold": 48.0,
                "severity": "critical",
                "recommended_action": "Contrôle clapet anti-retour"
            },
            {
                "month": 9,
                "date": "2026-09-01",
                "type": "temperature_spike",
                "value": 85.0,
                "threshold": 50.0,
                "severity": "critical",
                "recommended_action": "Remplacement joint haute température"
            }
        ],
        "predicted_maintenance_date": "2026-09-15",
        "predicted_failure_date": "2027-03-10",
        "estimated_lifespan_years": 11.3,
        "sensor_stats": {
            "avg_temperature_c": 32.4,
            "avg_pressure_bar": 42.1,
            "avg_vibration_mm_s": 2.8,
            "avg_flow_rate_m3h": 80.2,
            "anomaly_count": 14,
            "critical_events": 7
        },
        "files_generated": ["digital_twin_data.json"]
    }
}