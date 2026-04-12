import os
import json
from typing import TypedDict, List, Dict, Any
from langgraph.graph import StateGraph, END

# Importation des agents (Squelettes)
from Agent_1.AGENT1 import TechnicalAnalysisAgent
from Agent_2.AGENT2 import CADBIMAgent
from Agent_3.AGENT3 import MultimediaAgent
from Agent_4.AGENT4 import SourcingAgent
from Agent_5.AGENT5 import NegotiatorAgent
from Agent_6.AGENT6 import CostAnalystAgent
from Agent_7.AGENT7 import BusinessStrategistAgent
from Agent_8.AGENT8 import DigitalTwinAgent
from Agent_9.AGENT9 import CatalogueAgent

# --- Définition de l'Etat de INDUSTRIE IA ---
class AgentState(TypedDict):
    project_id: str
    file_path: str
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

# --- Orchestration LangGraph ---
def build_full_orchestrator():
    # Initialisation des agents
    a1 = TechnicalAnalysisAgent()
    a2 = CADBIMAgent()
    a3 = MultimediaAgent()
    a4 = SourcingAgent()
    a5 = NegotiatorAgent()
    a6 = CostAnalystAgent()
    a7 = BusinessStrategistAgent()
    a8 = DigitalTwinAgent()
    a9 = CatalogueAgent()

    # Création du graphe
    workflow = StateGraph(AgentState)

    # Ajout de tous les noeuds (Les 9 Agents)
    workflow.add_node("Agent_1_Technical_Analysis", a1.process_pdf)
    workflow.add_node("Agent_2_CAD_BIM", a2.generate_cad_files)
    workflow.add_node("Agent_3_Multimedia", a3.generate_promotional_content)
    workflow.add_node("Agent_4_Sourcing", a4.search_suppliers)
    workflow.add_node("Agent_5_Negotiator", a5.negotiate_prices)
    workflow.add_node("Agent_6_Cost_Analyst", a6.calculate_tco)
    workflow.add_node("Agent_7_Business_Strategist", a7.generate_business_plan)
    workflow.add_node("Agent_8_Digital_Twin", a8.simulate_maintenance)
    workflow.add_node("Agent_9_Catalogue_Specialist", a9.build_final_catalog)

    # Configuration du flux (Pipeline Linéaire pour INDUSTRIE IA)
    workflow.set_entry_point("Agent_1_Technical_Analysis")
    workflow.add_edge("Agent_1_Technical_Analysis", "Agent_2_CAD_BIM")
    workflow.add_edge("Agent_2_CAD_BIM", "Agent_3_Multimedia")
    workflow.add_edge("Agent_3_Multimedia", "Agent_4_Sourcing")
    workflow.add_edge("Agent_4_Sourcing", "Agent_5_Negotiator")
    workflow.add_edge("Agent_5_Negotiator", "Agent_6_Cost_Analyst")
    workflow.add_edge("Agent_6_Cost_Analyst", "Agent_7_Business_Strategist")
    workflow.add_edge("Agent_7_Business_Strategist", "Agent_8_Digital_Twin")
    workflow.add_edge("Agent_8_Digital_Twin", "Agent_9_Catalogue_Specialist")
    workflow.add_edge("Agent_9_Catalogue_Specialist", END)

    return workflow.compile()

# --- Cycle Final Complet ---
if __name__ == "__main__":
    print("\n" + "="*50)
    print("DEMARRAGE DU CYCLE INDUSTRIE IA (VHP-200 vannes)")
    print("="*50)

    initial_state: AgentState = {
        "project_id": "VHP-200-ALG",
        "file_path": "vanne_haute_pression.pdf",
        "technical_specs": {},
        "cad_files": [],
        "media_files": [],
        "suppliers_data": [],
        "negotiated_prices": {},
        "financial_data": {},
        "business_plan": {},
        "maintenance_data": {},
        "catalog_pack": [],
        "error": ""
    }

    app = build_full_orchestrator()
    final_output = app.invoke(initial_state)

    print("\n" + "="*50)
    print("RÉSULTAT DU CATALOGUE FINAL (Agent 9)")
    print("="*50)
    print(f"Livrables : {final_output['catalog_pack']}")
    print(f"ROI estimé : {final_output['business_plan'].get('expected_roi')}")
    print(f"Alerte Maintenance : {final_output['maintenance_data'].get('alerts')}")
    print("="*50)
