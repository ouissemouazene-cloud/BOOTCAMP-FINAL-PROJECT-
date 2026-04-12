# -*- coding: utf-8 -*-
"""
AGENT 6 : Analyste Couts -- Simplifié
Role : Calcule les coûts de production (TCO) et génère les rapports.
"""
import os, json, pandas as pd
import matplotlib.pyplot as plt

# Dossier pour enregistrer les fichiers
OUTPUT_DIR = os.path.join(os.path.dirname(__file__), "outputs")
os.makedirs(OUTPUT_DIR, exist_ok=True)

class CostAnalystAgent:
    def __init__(self, quantity=200):
        # Paramètres de base de l'usine
        self.quantity = quantity
        self.machining_rate = 7500  # DZD par heure machine
        self.hours_per_unit = 2     # Heures nécessaires par vanne
        self.energy_rate = 750      # Électricité par vanne
        self.logistics_fixed = 50000# Frais de transport fixes

    def calculate_tco(self, state):
        """Calcul du coût total et création des rapports."""
        
        # 1. Récupération du prix négocié par l'Agent 5
        negotiated = state.get("negotiated_prices", {})
        if not negotiated:
            state["error"] = "Agent 6 -- Prix non trouvé. Agent 5 a-t-il fini ?"
            return state

        # On prend le prix remisé (ce qu'on paie réellement)
        summary = negotiated.get("summary", negotiated)
        unit_mat_price = next(iter(summary.values())).get("discounted_price", 4500)

        # 2. Calcul des 4 types de coûts
        mat_total = self.quantity * unit_mat_price
        mac_total = self.quantity * self.hours_per_unit * self.machining_rate
        ene_total = self.quantity * self.energy_rate
        log_total = self.logistics_fixed
        
        # Somme totale et coût par unité
        total_cost = mat_total + mac_total + ene_total + log_total
        unit_cost  = total_cost / self.quantity

        # 3. Organisation des données pour les autres agents
        breakdown = {
            "Matières": mat_total, "Usinage": mac_total,
            "Énergie": ene_total, "Logistique": log_total
        }
        financial_data = {
            "total_production_cost": round(total_cost, 2),
            "unit_cost": round(unit_cost, 2),
            "quantity": self.quantity,
            "breakdown": breakdown
        }

        # 4. Génération des fichiers (JSON, Excel, Image)
        self._export_files(financial_data, breakdown)
        
        state["financial_data"] = financial_data
        print(f"Agent 6 fini ! Coût total : {total_cost:,.0f} DZD")
        return state

    def _export_files(self, data, breakdown):
        # Sauvegarde JSON (pour l'ordinateur)
        with open(os.path.join(OUTPUT_DIR, "cost_analysis.json"), "w") as f:
            json.dump(data, f, indent=4)

        # Sauvegarde EXCEL (pour l'humain)
        df = pd.DataFrame(list(breakdown.items()), columns=["Poste de dépense", "Montant (DZD)"])
        df.to_excel(os.path.join(OUTPUT_DIR, "cost_analysis.xlsx"), index=False)

        # Sauvegarde GRAPHIQUE (visuel)
        plt.figure(figsize=(10, 5))
        plt.bar(breakdown.keys(), breakdown.values(), color=['skyblue', 'salmon', 'lightgreen', 'gold'])
        plt.title(f"Répartition des Coûts (Total: {data['total_production_cost']:,.0f} DZD)")
        plt.ylabel("Dinars (DZD)")
        plt.savefig(os.path.join(OUTPUT_DIR, "tco_breakdown.png"))
        plt.close()

if __name__ == "__main__":
    # Test pour vérifier que tout marche sans le reste du projet
    mock_state = {"negotiated_prices": {"summary": {"Fournisseur": {"discounted_price": 3825}}}}
    agent = CostAnalystAgent()
    agent.calculate_tco(mock_state)
