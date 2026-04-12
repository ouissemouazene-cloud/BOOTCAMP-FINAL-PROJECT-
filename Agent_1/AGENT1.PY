import os
import json
from typing import TypedDict, List, Dict, Any
from langgraph.graph import StateGraph, END
from langchain_core.messages import HumanMessage, SystemMessage
from langchain_google_genai import ChatGoogleGenerativeAI
# import fitz  # PyMuPDF for PDF processing

# --- Définition de l'Etat (State) ---
class AgentState(TypedDict):
    project_id: str
    file_path: str
    raw_images: List[str]
    technical_specs: Dict[str, Any]      # Agent 1
    cad_files: List[str]               # Agent 2
    media_files: List[str]             # Agent 3
    suppliers_data: List[Dict]         # Agent 4
    negotiated_prices: Dict[str, Any]  # Agent 5
    financial_data: Dict[str, Any]     # Agent 6
    business_plan: Dict[str, Any]      # Agent 7
    maintenance_data: Dict[str, Any]   # Agent 8
    catalog_pack: List[str]            # Agent 9
    error: str

# --- Agent 1 : Analyseur Technique ---
class TechnicalAnalysisAgent:
    def __init__(self, model_name: str = "gemini-1.5-flash"):
        self.llm = ChatGoogleGenerativeAI(model=model_name)

    def process_pdf(self, state: AgentState) -> AgentState:
        """
        Simule la conversion PDF en Images et l'analyse visuelle.
        Dans une version réelle, on utiliserait PyMuPDF (fitz).
        """
        print(f"--- ANALYSE TECHNIQUE : {state['file_path']} ---")
        
        # Simulation d'extraction de données techniques via Vision LLM
        # Ici on prépare le prompt pour l'extraction structurée
        system_prompt = (
            "Vous êtes un ingénieur expert en fabrication mécanique (Industrie 4.0). "
            "Analysez le plan technique fourni et extrayez : "
            "1. Nom de la pièce, 2. Matériau, 3. Dimensions critiques, 4. Nomenclature (BOM)."
        )
        
        # Simulation de la réponse JSON structurée
        simulated_output = {
            "part_name": "Vanne Haute Pression VHP-200",
            "material": "Inox 316L",
            "dimensions": {
                "overall_height": "250mm",
                "flange_diameter": "150mm",
                "port_size": "2 inch"
            },
            "bom": [
                {"item": "Corps de vanne", "qty": 1, "source": "machined"},
                {"item": "Tige filetée", "qty": 1, "source": "machined"},
                {"item": "Joint d'étanchéité Viton", "qty": 2, "source": "standard_purchase"},
                {"item": "Boulonnerie M12", "qty": 8, "source": "standard_purchase"}
            ],
            "manufacturing_steps": [
                "Débitage Inox 316L",
                "Tournage CNC (Flasques)",
                "Fraisage CNC (Corps)",
                "Rectification des portées",
                "Test d'épreuve 200 Bars"
            ]
        }
        
        state["technical_specs"] = simulated_output
        return state

# --- Orchestration LangGraph ---
def build_agent1_graph():
    agent = TechnicalAnalysisAgent()
    
    workflow = StateGraph(AgentState)
    
    # Ajout du noeud
    workflow.add_node("analyze_plan", agent.process_pdf)
    
    # Configuration du flux
    workflow.set_entry_point("analyze_plan")
    workflow.add_edge("analyze_plan", END)
    
    return workflow.compile()

# --- Exécution de Test ---
if __name__ == "__main__":
    # Initialisation de l'état
    initial_state: AgentState = {
        "project_id": "PME-ALG-001",
        "file_path": "vanne_haute_pression.pdf",
        "raw_images": [],
        "technical_specs": {},
        "error": ""
    }
    
    app = build_agent1_graph()
    result = app.invoke(initial_state)
    
    print("\n--- RESULTAT FINAL AGENT 1 ---")
    print(json.dumps(result["technical_specs"], indent=4, ensure_ascii=False))
