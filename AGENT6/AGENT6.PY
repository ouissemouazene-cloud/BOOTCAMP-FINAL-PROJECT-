# -*- coding: utf-8 -*-
"""
AGENT 6 : Analyste Couts
Role : Calcule les coûts de production (TCO) et génère les rapports.
"""
import os, json, pandas as pd
import matplotlib.pyplot as plt

OUTPUT_DIR = os.path.join(os.path.dirname(__file__), "outputs")
os.makedirs(OUTPUT_DIR, exist_ok=True)

class CostAnalystAgent:
    def __init__(self, quantity=200):
        self.quantity = quantity
        self.machining_rate = 7500  # DZD par heure machine
        self.hours_per_unit = 2     
        self.energy_rate = 750      
        self.logistics_fixed = 50000
        self.weight_per_valve_kg = 510  # Pour atteindre environ ~3800 DZD avec le prix fournisseur

    def calculate_tco(self, state):
        
        # 1. Récupération du fournisseur sélectionné (Agent 5)
        selected = state.get("selected_supplier", {})
        if not selected:
            state["error"] = "Agent 6 -- Fournisseur sélectionné non trouvé."
            return state

        # Prix au kg fourni par l'Agent 5
        price_per_kg = selected.get("price_per_kg", 7.5)
        
        # On calcule le prix matière par vanne
        unit_mat_price = price_per_kg * self.weight_per_valve_kg

        # 2. Calcul des coûts
        mat_total = self.quantity * unit_mat_price
        mac_total = self.quantity * self.hours_per_unit * self.machining_rate
        ene_total = self.quantity * self.energy_rate
        log_total = self.logistics_fixed
        
        total_cost = mat_total + mac_total + ene_total + log_total
        unit_cost  = total_cost / self.quantity

        # 3. Préparation des données -> Structuré pour Agent 7
        breakdown = {
            "Matières": mat_total, 
            "Usinage": mac_total,
            "Énergie": ene_total, 
            "Logistique": log_total
        }
        
        financial_data = {
            "total_production_cost": round(total_cost, 2),
            "unit_cost": round(unit_cost, 2),
            "quantity": self.quantity,
            "breakdown": breakdown
        }

        self._export_files(financial_data, breakdown)
        state["financial_data"] = financial_data
        
        print(f"Agent 6 fini ! Coût total : {total_cost:,.0f} DZD")
        return state

    def _export_files(self, data, breakdown):
        # JSON
        with open(os.path.join(OUTPUT_DIR, "cost_analysis.json"), "w") as f:
            json.dump(data, f, indent=4)

        # EXCEL
        df = pd.DataFrame(list(breakdown.items()), columns=["Poste", "Montant (DZD)"])
        df.to_excel(os.path.join(OUTPUT_DIR, "cost_analysis.xlsx"), index=False)

        # GRAPHIQUE
        plt.figure(figsize=(10, 5))
        plt.bar(breakdown.keys(), breakdown.values(), color=['skyblue', 'salmon', 'lightgreen', 'gold'])
        plt.title(f"Répartition des Coûts (Total: {data['total_production_cost']:,.0f} DZD)")
        plt.savefig(os.path.join(OUTPUT_DIR, "tco_breakdown.png"))
        plt.close()

if __name__ == "__main__":
    mock_state = {"selected_supplier": {"price_per_kg": 7.5}}
    agent = CostAnalystAgent()
    agent.calculate_tco(mock_state)
