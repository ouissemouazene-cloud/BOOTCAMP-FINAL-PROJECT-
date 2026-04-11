import os
from typing import Dict, Any, List
# from langchain_openai import ChatOpenAI

# --- Agent 5 : Négociateur IA (Procurement) ---
class NegotiatorAgent:
    def __init__(self, target_discount: float = 0.15):
        self.target_discount = target_discount

    def negotiate_prices(self, state: Dict[str, Any]) -> Dict[str, Any]:
        """
        Simule une négociation avec les fournisseurs pour un volume de 200 unités.
        """
        suppliers = state.get("suppliers_data", [])
        if not suppliers:
            state["error"] = "Aucun fournisseur identifié pour la négociation."
            return state

        print("--- NEGOCIATION IA : Simulation d'échanges (VHP-200) ---")
        
        # Simulation d'application de remise volume (Négociation réussie)
        negotiated_prices = {}
        for s in suppliers:
            negotiated_prices[s["name"]] = {
                "base_price": s["price_unit"], 
                "discounted_price": s["price_unit"] * (1 - self.target_discount), 
                "status": "Negotiated - OK"
            }
        
        # Transcription simulée
        transcript = (
            "Acheteur: Bonjour, nous commandons 200 unités de votre Inox 316L. Quel est votre meilleur prix ?\n"
            "Vendeur: Pour ce volume, nous pouvons faire une remise de 15% immédiate.\n"
            "Acheteur: Accepté. Préparez le bon de commande."
        )
        
        # Mise à jour de l'état
        state["negotiated_prices"] = {
            "summary": negotiated_prices,
            "transcript": transcript,
            "negotiation_audio": "negotiation_summary.mp3"
        }
        return state

if __name__ == "__main__":
    mock_state = {
        "suppliers_data": [{"name": "Alger Steel Works", "price_unit": 4500}],
        "negotiated_prices": {}
    }
    agent = NegotiatorAgent()
    print(agent.negotiate_prices(mock_state))
