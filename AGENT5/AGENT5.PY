import json
from typing import Dict, Any

# --- Agent 5 : Sélection du meilleur fournisseur ---
class NegotiatorAgent:
    def __init__(self):
        pass

    def negotiate_prices(self, state: Dict[str, Any]) -> Dict[str, Any]:
        """
        Analyse les fournisseurs de l'Agent 4 et sélectionne le meilleur.
        """
        suppliers = state.get("suppliers_data", [])
        if not suppliers:
            state["error"] = "Aucun fournisseur identifié pour la sélection."
            return state

        print("--- SELECTION FOURNISSEUR OPTIMAL ---")
        
        # Logique de sélection : On prend celui avec le meilleur "score"
        best_supplier = None
        highest_score = -1

        for s in suppliers:
            if s.get("score", 0) > highest_score:
                highest_score = s.get("score", 0)
                best_supplier = s

        if best_supplier:
            # On suit la structure demandée par l'utilisateur
            state["selected_supplier"] = best_supplier
            state["reason"] = "Meilleur équilibre entre coût, délai et qualité selon le score."
        else:
            state["error"] = "Impossible de sélectionner un fournisseur."

        return state

if __name__ == "__main__":
    mock_state = {
        "suppliers_data": [
            {"name": "Maschinenfabrik Christian Hagans", "country": "Germany", "price_per_kg": 7.5, "lead_days": 12, "rating": 4.8, "score": 0.81}
        ]
    }
    agent = NegotiatorAgent()
    print(json.dumps(agent.negotiate_prices(mock_state), indent=2))
