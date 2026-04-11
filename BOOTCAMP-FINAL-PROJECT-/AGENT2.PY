import json
from typing import TypedDict, List, Dict, Any
# import ezdxf  # Pour générer des fichiers DXF réels

# --- État LangGraph (Partagé entre agents) ---
class AgentState(TypedDict):
    project_id: str
    file_path: str
    technical_specs: Dict[str, Any]
    cad_files: List[str]
    error: str

# --- Agent 2 : Concepteur CAD/BIM ---
class CADBIMAgent:
    def __init__(self, output_dir: str = "cad_output"):
        self.output_dir = output_dir

    def generate_cad_files(self, state: AgentState) -> AgentState:
        """
        Simule la génération automatique de plans 2D/3D (DXF/IFC).
        Dans une version réelle, on utiliserait 'ezdxf' pour dessiner les géométries.
        """
        specs = state.get("technical_specs", {})
        if not specs:
            state["error"] = "Aucune spécification technique trouvée pour générer les plans CAD."
            return state

        print(f"--- CONCEPTION CAD : {specs.get('part_name', 'Inconnu')} ---")
        
        # Logique de génération (Simulation)
        dxf_filename = f"{state['project_id']}_blueprint.dxf"
        ifc_filename = f"{state['project_id']}_model.ifc"
        
        # Simulation d'écriture de fichier DXF avec les dimensions extraites
        print(f"Extraction des dimensions pour le plan : {specs.get('dimensions')}")
        print(f"Action : Dessin des perçages pour vannes {specs.get('pressure_rating', 'PN-Standard')}")
        
        # Mise à jour de l'état
        state["cad_files"] = [dxf_filename, ifc_filename]
        return state

# Note : Le LangGraph final orchestrera l'Agent 1 puis l'Agent 2.
if __name__ == "__main__":
    # Test unitaire de l'Agent 2
    mock_state: AgentState = {
        "project_id": "VHP-200-ALG",
        "file_path": "test.pdf",
        "technical_specs": {
            "part_name": "Vanne Haute Pression",
            "material": "Inox 316L",
            "pressure_rating": "200 Bars",
            "dimensions": {"overall_height": "250mm", "flange_diameter": "150mm"}
        },
        "cad_files": [],
        "error": ""
    }
    
    agent = CADBIMAgent()
    result = agent.generate_cad_files(mock_state)
    
    print("\n--- RESULTAT FINAL AGENT 2 ---")
    print(f"Plans générés : {result['cad_files']}")
