import os
import json
from typing import Dict, Any, List
try:
    from gtts import gTTS
except ImportError:
    pass

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
            print(f"\nErreur : {state['error']}")
            return state

        print("\n--- NEGOCIATION IA : Simulation d'échanges (VHP-200) ---")
        
        negotiated_prices = {}
        transcript_lines = []
        
        # Simulation d'application de remise volume
        for s in suppliers:
            base_price = s.get("price_unit", 0)
            currency = s.get("currency", "USD")
            # Arrondir le prix remisé à deux décimales
            discounted_price = round(base_price * (1 - self.target_discount), 2)
            
            negotiated_prices[s["name"]] = {
                "base_price": base_price, 
                "discounted_price": discounted_price,
                "currency": currency,
                "status": "Negotiated - OK"
            }
            
            # Phrase de dialogue pour ce fournisseur
            transcript_lines.append(
                f"Négociation avec {s['name']} pour l'article {s.get('item', 'inconnu')} : "
                f"Le prix de base était de {base_price} {currency}, nous avons négocié un prix final de {discounted_price} {currency}."
            )
        
        # Regrouper le transcript
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
            # On génère le texte global pour l'audio
            tts = gTTS(text=transcript_text, lang='fr')
            tts.save(audio_filename)
            audio_success = True
        except Exception as e:
            print(f"\nAttention, impossible de générer l'audio MP3 (vérifiez votre connexion ou gtts) : {e}")
        
        # Mise à jour de l'état (compatibilité LangGraph)
        state["negotiated_prices"] = {
            "summary": negotiated_prices,
            "transcript": transcript_text,
            "negotiation_audio": audio_filename if audio_success else None
        }
        
        # Affichage d'un résumé lisible dans le terminal
        print("\n--- RÉSUMÉ APRÈS NÉGOCIATION ---")
        for name, data in negotiated_prices.items():
            print(f"Fournisseur : {name}")
            print(f"  Prix initial : {data['base_price']} {data['currency']}")
            print(f"  Prix négocié : {data['discounted_price']} {data['currency']}")
        
        print(f"\nFichiers générés :")
        print("- negotiated_prices.json")
        print("- negotiation_transcript.txt")
        if audio_success:
            print("- negotiation_summary.mp3")
            
        return state

if __name__ == "__main__":
    # Lire suppliers_data.json (ou suppliers_output.json) depuis le disque
    filename = "suppliers_data.json"
    if not os.path.exists(filename) and os.path.exists("suppliers_output.json"):
        filename = "suppliers_output.json"
        
    try:
        with open(filename, "r", encoding="utf-8") as f:
            suppliers_data = json.load(f)
    except Exception as e:
        suppliers_data = []
        print(f"Attention, impossible de charger les fournisseurs : {e}")

    mock_state = {
        "suppliers_data": suppliers_data
    }
    
    agent = NegotiatorAgent()
    agent.negotiate_prices(mock_state)
