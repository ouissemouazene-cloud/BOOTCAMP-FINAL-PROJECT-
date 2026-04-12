import json
from typing import Dict, Any, List
# from langchain.tools.tavily_search import TavilySearchResults

# --- Agent 4 : Agent Sourcing (Supply Chain) ---
class SourcingAgent:
    def __init__(self, location: str = "Algeria"):
        self.location = location

    def search_suppliers(self, state: Dict[str, Any]) -> Dict[str, Any]:
        """
        Scan les annuaires publics pour trouver des fournisseurs de matières premières.
        """
        print(f"--- RECHERCHE FOURNISSEURS : Localisation {self.location} ---")
        
        # Simulation de recherche SERP/Annuaires pour Inox 316L et Joints Viton
        simulated_suppliers = [
            {"name": "Alger Steel Works", "location": "Alger", "item": "Inox 316L", "price_unit": 4500, "currency": "DZD"},
            {"name": "Global Gaskets Intl", "location": "International", "item": "Joint Viton", "price_unit": 12, "currency": "USD"},
            {"name": "Standard Fasteners Algérie", "location": "Oran", "item": "Boulonnerie M12", "price_unit": 85, "currency": "DZD"}
        ]
        
        # Mise à jour de l'état
        state["suppliers_data"] = simulated_suppliers
        return state

if __name__ == "__main__":
    mock_state = {"suppliers_data": []}
    agent = SourcingAgent()
    state = agent.search_suppliers(mock_state)
    
    print("\nFournisseurs trouvés :")
    for supplier in state.get("suppliers_data", []):
        print(f"- {supplier['name']} ({supplier['location']}) : {supplier['item']} - {supplier['price_unit']} {supplier['currency']}")
        
    print("\nContenu de state[\"suppliers_data\"] :")
    json_data = json.dumps(state.get("suppliers_data", []), indent=4, ensure_ascii=False)
    print(json_data)
    
    # Génération du fichier JSON
    with open("suppliers_data.json", "w", encoding="utf-8") as f:
        f.write(json_data)
    print("\n✅ Le fichier 'suppliers_data.json' a été généré avec succès !")
