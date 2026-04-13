import json
import urllib.request
import urllib.parse
import random
from typing import Dict, Any, List

# --- Agent 4 : Agent Sourcing (Supply Chain) ---
class SourcingAgent:
    def __init__(self, location: str = "Algeria"):
        self.location = location

    def query_wikidata(self):
        """
        Interroge Wikidata pour récupérer des entreprises fabriquant de l'acier (Q11427).
        """
        query = """
        SELECT ?itemLabel ?countryLabel WHERE {
          ?item wdt:P31 wd:Q4830453.
          ?item wdt:P17 ?country.
          ?item wdt:P1056 wd:Q11427.
          SERVICE wikibase:label { bd:serviceParam wikibase:language "fr,en". }
        }
        LIMIT 20
        """
        url = 'https://query.wikidata.org/sparql?query=' + urllib.parse.quote(query) + '&format=json'
        
        try:
            req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'})
            with urllib.request.urlopen(req, timeout=10) as response:
                data = json.loads(response.read().decode('utf-8'))
                
            suppliers = []
            for result in data.get('results', {}).get('bindings', []):
                name = result.get('itemLabel', {}).get('value', 'Inconnu')
                country = result.get('countryLabel', {}).get('value', 'Inconnu')
                if name != 'Inconnu':
                    suppliers.append({"name": name, "country": country})
            return suppliers
        except Exception as e:
            print(f"Erreur API Wikidata: {e}")
            return []

    def fetch_comtrade_stats(self):
        """
        Interroge l'API UN Comtrade pour vérifier les flux commerciaux de l'Acier (HS Code 72)
        """
        try:
            url = "https://comtradeapi.un.org/public/v1/preview/C/A/HS?cmdCode=72&flowCode=M&period=2022"
            req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
            with urllib.request.urlopen(req, timeout=10) as response:
                data = json.loads(response.read().decode('utf-8'))
                return data.get("count", 0) > 0
        except Exception as e:
            print(f"Erreur API Comtrade: {e}")
            return False

    def search_suppliers(self, state: Dict[str, Any]) -> Dict[str, Any]:
        """
        Scan les annuaires via API pour trouver des fournisseurs de matières premières (Inox 316L).
        """
        print(f"--- RECHERCHE FOURNISSEURS : Localisation {self.location} ---")
        
        print(">> Analyse des flux d'Acier (HS 72) via UN Comtrade API...")
        if self.fetch_comtrade_stats():
            print(">> Flux massifs d'acier détectés à l'international.")
            
        print(">> Ciblage des aciéries via Wikidata (Knowledge Graph)...")
        wikidata_suppliers = self.query_wikidata()
        
        simulated_suppliers = []
        if wikidata_suppliers:
            for ws in wikidata_suppliers:
                price = random.randint(150, 800)
                curr = "USD"
                if "France" in ws['country'] or "Netherlands" in ws['country']:
                    curr = "EUR"
                elif "Alg" in ws['country']:
                    curr = "DZD"
                    price *= 140

                simulated_suppliers.append({
                    "name": ws['name'],
                    "location": ws['country'],
                    "item": "Inox 316L",
                    "price_unit": round(price, 2),
                    "currency": curr
                })
        else:
            print(">> Utilisation des fournisseurs locaux de secours.")
            simulated_suppliers = [
                {"name": "Alger Steel Works", "location": "Alger", "item": "Inox 316L", "price_unit": 4500, "currency": "DZD"},
                {"name": "Global Gaskets Intl", "location": "International", "item": "Joint Viton", "price_unit": 12, "currency": "USD"},
                {"name": "Standard Fasteners Algérie", "location": "Oran", "item": "Boulonnerie M12", "price_unit": 85, "currency": "DZD"}
            ]
        
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
    
    with open("suppliers_data.json", "w", encoding="utf-8") as f:
        f.write(json_data)
    print("\nLe fichier 'suppliers_data.json' a été généré avec succès !")
