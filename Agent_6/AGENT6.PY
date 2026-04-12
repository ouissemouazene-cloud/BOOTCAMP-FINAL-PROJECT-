import os
import json
from typing import Dict, Any, List
# import pandas as pd # Pour Excel

# --- Agent 6 : Analyste Coûts (TCO) ---
class CostAnalystAgent:
    def __init__(self, machining_cost_per_hour: float = 7500):
        self.machining_cost_per_hour = machining_cost_per_hour

    def calculate_tco(self, state: Dict[str, Any]) -> Dict[str, Any]:
        """
        Calcule le Coût Total de Possession (Total Cost of Ownership).
        """
        negotiated = state.get("negotiated_prices", {})
        if not negotiated:
            state["error"] = "Aucun prix négocié trouvé pour le calcul des coûts."
            return state

        print("--- ANALYSE DE COÛTS : Calcul du TCO (Énergie + Logistique + Fabrication) ---")
        
        # Simulation du calcul pour 200 unités
        total_costs = {
            "materials_subtotal": 200 * 4500 * (1 - 0.15),
            "machining_total": 400 * self.machining_cost_per_hour, # 2 heures par vanne x 200 vannes
            "energy_estimate": 150000, # DZD
            "logistics_delivery": 50000, # DZD
            "total_production_cost": (200 * 4500 * 0.85) + (400 * 7500) + 150000 + 50000,
            "unit_cost": ((200 * 4500 * 0.85) + (400 * 7500) + 150000 + 50000) / 200
        }
        
        # Mise à jour de l'état
        state["financial_data"] = total_costs
        return state

if __name__ == "__main__":
    mock_state = {
        "negotiated_prices": {"summary": {"Alger Steel Works": {"base_price": 4500, "discounted_price": 3825}}},
        "financial_data": {}
    }
    agent = CostAnalystAgent()
    print(agent.calculate_tco(mock_state))
