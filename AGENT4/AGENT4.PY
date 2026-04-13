import json
from typing import Dict, Any, List

# --- Agent 4 : Agent Sourcing (Fournisseurs Internationaux) ---
class SourcingAgent:
    def __init__(self, location: str = "Germany"):
        self.location = location

    def search_suppliers(self, state: Dict[str, Any]) -> Dict[str, Any]:
        """
        Recherche des fournisseurs de matières premières (Inox, etc.)
        """
        print(f"--- RECHERCHE FOURNISSEURS : {self.location} ---")
        
        # Liste simulée demandée :
        suppliers_list = [
          {
            "name": "Gerresheimer",
            "country": "Germany",
            "price_per_kg": 7.0,
            "lead_days": 10,
            "rating": 4.9,
            "score": 0.99,
            "contact": {
                "email": "info@gerresheimer.com",
                "phone": "+49 111 222 333",
                "website": "https://gerresheimer.com"
            }
          },
          {
            "name": "Maschinenfabrik Christian Hagans",
            "country": "Germany",
            "price_per_kg": 7.5,
            "lead_days": 12,
            "rating": 4.8,
            "score": 0.81,
            "contact": {
                "email": "contact@hagans.de",
                "phone": "+49 123 456 789",
                "website": "https://hagans.de"
            }
          },
          {
            "name": "Pfeiffer Vacuum",
            "country": "Germany",
            "price_per_kg": 8.0,
            "lead_days": 14,
            "rating": 4.7,
            "score": 0.63,
            "contact": {
                "email": "sales@pfeiffer-vacuum.com",
                "phone": "+49 987 654 321",
                "website": "https://pfeiffer-vacuum.com"
            }
          }
        ]
        
        # Mise à jour de l'état
        state["suppliers_data"] = suppliers_list
        return state

if __name__ == "__main__":
    mock_state = {"suppliers_data": []}
    agent = SourcingAgent()
    print(json.dumps(agent.search_suppliers(mock_state), indent=2))
