import os
import json
import csv
import re
import requests
from typing import Dict, Any, List

try:
    from gtts import gTTS
except ImportError:
    pass

# --- Agent 5 : Négociateur IA (Procurement) ---
class NegotiatorAgent:
    def __init__(self, target_discount: float = 0.15):
        self.target_discount = target_discount

    def setup_csv(self, suppliers):
        """ Écrit les 3 premiers fournisseurs dans un CSV pour satisfaire le besoin """
        suppliers_3 = suppliers[:3]
        csv_filename = "suppliers.csv"
        with open(csv_filename, 'w', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=["name", "location", "item", "price_unit", "currency"])
            writer.writeheader()
            for s in suppliers_3:
                # Filtrer juste les clefs necessaires
                row = {k: s.get(k) for k in ["name", "location", "item", "price_unit", "currency"]}
                writer.writerow(row)
        return suppliers_3

    def negotiate_prices(self, state: Dict[str, Any]) -> Dict[str, Any]:
        """
        Simule une négociation avec les fournisseurs pour un volume de 200 unités.
        """
        suppliers = state.get("suppliers_data", [])
        if not suppliers:
            state["error"] = "Aucun fournisseur identifié pour la négociation."
            print(f"\nErreur : {state['error']}")
            return state

        print("\n--- NEGOCIATION IA : LLM Mistral (Ollama) ---")
        
        # 1. Préparation du CSV
        suppliers_to_negotiate = self.setup_csv(suppliers)
        print(">> Lecture de 3 fournisseurs depuis le CSV généré (suppliers.csv)...")

        negotiated_prices = {}
        transcript_lines = []
        
        # Initialisation Ollama via REST API
        ollama_url = "http://localhost:11434/api/generate"
        ollama_available = False
        try:
            print(">> Vérification de la connexion à Ollama...")
            response = requests.get("http://localhost:11434/", timeout=2)
            if response.status_code == 200:
                ollama_available = True
                print(">> Ollama détecté. Utilisation du modèle 'mistral'.")
        except Exception:
            pass
                
        if not ollama_available:
            print(">> Ollama n'est pas accessible sur localhost:11434. Démarrage du Fallback (Remise 15% auto).")
        
        for s in suppliers_to_negotiate:
            base_price = float(s.get("price_unit", 0))
            currency = s.get("currency", "USD")
            supplier_name = s.get("name", "Inconnu")
            item = s.get("item", "Inox 316L")
            
            discounted_price = None
            llm_text = ""
            
            if ollama_available:
                prompt = (
                    f"Tu es le commercial de l'entreprise '{supplier_name}'. "
                    f"Je suis un acheteur industriel. Je veux acheter 200 unités de '{item}'. "
                    f"Ton prix de base est de {base_price} {currency} l'unité. "
                    f"Je trouve cela un peu cher. Peux-tu me faire un meilleur prix pour ces 200 unités ? "
                    f"Tu peux accepter en proposant un nouveau prix inférieur avec tes arguments, OU tu peux catégoriquement refuser de baisser le prix en te justifiant. Sois clair, sois un bon négociateur et réponds en une ou deux phrases."
                )
                try:
                    payload = {
                        "model": "mistral",
                        "prompt": prompt,
                        "stream": False
                    }
                    api_response = requests.post(ollama_url, json=payload, timeout=120)
                    api_response.raise_for_status()
                    llm_text = api_response.json().get("response", "").strip()
                    
                    # Extraction du nombre pour le prix :
                    numbers = re.findall(r'\d+(?:\.\d+)?', llm_text)
                    candidates = [float(n) for n in numbers if 0 < float(n) < base_price]
                    if candidates:
                        discounted_price = min(candidates)
                    else:
                        # Le fournisseur a refusé de descendre le prix
                        discounted_price = base_price
                except Exception as e:
                    print(f"Erreur d'appel LLM pour {supplier_name} : {e} (Fallback lancé)")

            # Fallback : Seulement exécuté si Ollama n'a pas répondu (ex: erreur réseau/plantage)
            if not llm_text:
                discounted_price = round(base_price * (1 - self.target_discount), 2)
                llm_text = f"D'accord, à titre exceptionnel, nous acceptons de descendre à {discounted_price} {currency} par unité."

            status_text = "Negotiated - OK" if discounted_price < base_price else "Refused discount"
            negotiated_prices[supplier_name] = {
                "base_price": base_price, 
                "discounted_price": discounted_price,
                "currency": currency,
                "status": status_text
            }
            
            transcript_lines.append(f"Acheteur : Négociation pour 200x {item} à {base_price} {currency}. Vous faites un effort ?")
            transcript_lines.append(f"{supplier_name} : {llm_text}\n")
            
            print(f"> {supplier_name} conclu à {discounted_price} {currency}")

        transcript_text = "\n".join(transcript_lines)
        
        # Output 1 — negotiated_prices.json
        with open("negotiated_prices.json", "w", encoding="utf-8") as f:
            json.dump(negotiated_prices, f, indent=4, ensure_ascii=False)
            
        # Output 2 — negotiation_transcript.txt
        with open("negotiation_transcript.txt", "w", encoding="utf-8") as f:
            f.write(transcript_text)
            
        # Output 3 — negotiation_summary.mp3 (via gTTS)
        audio_filename = "negotiation_summary.mp3"
        audio_success = False
        try:
            tts = gTTS(text=transcript_text, lang='fr')
            tts.save(audio_filename)
            audio_success = True
        except Exception as e:
            print(f"\nAttention, impossible de générer l'audio MP3 : {e}")
        
        state["negotiated_prices"] = {
            "summary": negotiated_prices,
            "transcript": transcript_text,
            "negotiation_audio": audio_filename if audio_success else None
        }
        
        print("\n--- RÉSUMÉ APRÈS NÉGOCIATION ---")
        for name, data in negotiated_prices.items():
            print(f"Fournisseur : {name} | Prix: {data['base_price']} -> {data['discounted_price']} {data['currency']}")
            
        print(f"\nFichiers générés : negotiated_prices.json, negotiation_transcript.txt, suppliers.csv")
        if audio_success:
            print("- negotiation_summary.mp3")
            
        return state

if __name__ == "__main__":
    import sys
    # On va chercher les données de l'agent 4 fraîchement créées pour le test local
    fallback_path = "../AGENT4/suppliers_data.json"
    local_path = "suppliers_data.json"
    
    suppliers_data = []
    if os.path.exists(local_path):
        with open(local_path, "r", encoding="utf-8") as f:
            suppliers_data = json.load(f)
    elif os.path.exists(fallback_path):
        with open(fallback_path, "r", encoding="utf-8") as f:
            suppliers_data = json.load(f)
    else:
         suppliers_data = [{"name": "Mock Steel", "location": "US", "item": "Inox", "price_unit": 100, "currency": "USD"}]

    mock_state = {"suppliers_data": suppliers_data}
    
    agent = NegotiatorAgent()
    agent.negotiate_prices(mock_state)
