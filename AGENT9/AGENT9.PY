# =============================================================================
# agent9.py
# Agent 9 — Catalogue Exporter
#
# Rôle : Dernier agent du pipeline INDUSTRIE IA.
#        Collecte toutes les sorties des Agents 1→8, génère le catalogue
#        en 5 formats simultanés et crée un ZIP livrable au client.
#
# Formats produits :
#   catalogue.pdf    → WeasyPrint + Jinja2
#   catalogue.html   → Jinja2
#   catalogue.xlsx   → openpyxl (6 onglets)
#   catalogue.json   → json (hiérarchique + flat)
#   catalogue.xml    → lxml + Jinja2
#   livrable_client.zip → archive finale
#
# Intégration LangGraph :
#   Ce fichier expose une fonction `agent9_node(state)` qui respecte le
#   contrat LangGraph : reçoit un State dict, retourne un State dict mis à jour.
# =============================================================================

import os
import sys
import json
import zipfile
import hashlib
import tempfile
from datetime import datetime
from pathlib import Path
from typing import TypedDict, Any

# Fix encoding for Windows console (cp1252)
if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8")

from models import PipelineData
from generators.html_gen import generate_html
from generators.xml_gen import generate_xml
from generators.json_gen import generate_json
from generators.excel_gen import generate_excel

# WeasyPrint est importé ici pour que l'erreur soit claire si pas installé
try:
    from generators.pdf_gen import generate_pdf
    PDF_AVAILABLE = True
except (ImportError, OSError) as e:
    PDF_AVAILABLE = False
    print(f"  [WARNING] Probleme avec WeasyPrint (GTK3 manquant) -> PDF ignore. Erreur: {e}")


# =============================================================================
# LangGraph State
# On définit le TypedDict du State partagé entre tous les agents du pipeline.
# Chaque agent lit et écrit dans ce dictionnaire.
# =============================================================================
class PipelineState(TypedDict):
    # Sorties de chaque agent (remplies au fur et à mesure du pipeline)
    agent1: dict
    agent2: dict
    agent3: dict
    agent4: dict
    agent5: dict
    agent6: dict
    agent7: dict
    agent8: dict

    # Sortie de l'agent 9 (remplie par ce fichier)
    agent9: dict


# =============================================================================
# Fonction utilitaire : calcul du checksum SHA-256 d'un fichier
# Permet de vérifier l'intégrité des fichiers dans le manifeste
# =============================================================================
def _sha256(filepath: str) -> str:
    """Retourne le hash SHA-256 d'un fichier."""
    h = hashlib.sha256()
    with open(filepath, "rb") as f:
        for chunk in iter(lambda: f.read(8192), b""):
            h.update(chunk)
    return h.hexdigest()


# =============================================================================
# Fonction utilitaire : création du manifeste JSON
# Le manifeste liste tous les fichiers produits avec leurs métadonnées
# =============================================================================
def _create_manifest(files: dict, generated_at: str) -> dict:
    """
    Crée le manifeste du livrable.

    Args:
        files: dict {nom_fichier: chemin_absolu}
        generated_at: timestamp de génération

    Returns:
        dict manifeste
    """
    manifest = {
        "pipeline": "INDUSTRIE_IA",
        "agent": 9,
        "generated_at": generated_at,
        "files": {}
    }

    for name, path in files.items():
        if os.path.exists(path):
            size = os.path.getsize(path)
            manifest["files"][name] = {
                "size_bytes": size,
                "size_kb": round(size / 1024, 1),
                "sha256": _sha256(path)
            }

    return manifest


# =============================================================================
# Fonction principale de génération des 5 formats
# Peut être appelée directement (standalone) ou via LangGraph
# =============================================================================
def run_agent9(pipeline_data: dict, output_dir: str = None) -> dict:
    """
    Génère tous les formats du catalogue et crée le ZIP livrable.

    Args:
        pipeline_data: dict contenant les sorties de tous les agents (1→8)
        output_dir: dossier où écrire les fichiers. Si None → dossier temporaire.

    Returns:
        dict avec les chemins des fichiers générés et les métadonnées
    """

    print("\n" + "="*60)
    print("  AGENT 9 — Catalogue Exporter")
    print("="*60)

    # ── Étape 1 : Valider les données d'entrée avec Pydantic ─────────────────
    # Si un champ manque ou a un mauvais type, Pydantic lève une ValidationError
    print("\n[1/4] Validation des données d'entrée...")
    try:
        data = PipelineData(**pipeline_data)
        print(f"  ✓ Données valides — Produit : {data.agent1.part_name}")
    except Exception as e:
        raise ValueError(f"Données du pipeline invalides : {e}") from e

    # ── Étape 2 : Préparer le dossier de sortie ───────────────────────────────
    if output_dir is None:
        output_dir = tempfile.mkdtemp(prefix="catalogue_")
    os.makedirs(output_dir, exist_ok=True)

    generated_at = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    part_id = data.agent1.part_id.replace("/", "_")  # Sécuriser pour nom de fichier

    # ── Étape 3 : Préparer le contexte Jinja2 ────────────────────────────────
    # Ce dictionnaire est passé aux templates HTML et XML
    context = {
        "specs":           data.agent1,
        "cad":             data.agent2,
        "video":           data.agent3,
        "sourcing":        data.agent4,
        "nego":            data.agent5,
        "tco":             data.agent6,
        "bp":              data.agent7,
        "twin":            data.agent8,
        "generated_date":  generated_at,
    }

    # ── Étape 4 : Générer les 5 formats ──────────────────────────────────────
    print("\n[2/4] Génération des 5 formats...")

    produced_files = {}

    # 4a. HTML
    html_path = os.path.join(output_dir, f"catalogue_{part_id}.html")
    generate_html(context, html_path)
    produced_files["catalogue.html"] = html_path

    # 4b. PDF (si WeasyPrint est installé)
    if PDF_AVAILABLE:
        pdf_path = os.path.join(output_dir, f"catalogue_{part_id}.pdf")
        generate_pdf(context, pdf_path)
        produced_files["catalogue.pdf"] = pdf_path
    else:
        print("  [PDF] ⚠ Ignoré (WeasyPrint non disponible)")

    # 4c. Excel
    xlsx_path = os.path.join(output_dir, f"catalogue_{part_id}.xlsx")
    generate_excel(data, xlsx_path)
    produced_files["catalogue.xlsx"] = xlsx_path

    # 4d. JSON
    json_path = os.path.join(output_dir, f"catalogue_{part_id}.json")
    generate_json(data, json_path)
    produced_files["catalogue.json"] = json_path

    # 4e. XML
    xml_path = os.path.join(output_dir, f"catalogue_{part_id}.xml")
    generate_xml(context, xml_path)
    produced_files["catalogue.xml"] = xml_path

    # ── Étape 5 : Créer le manifeste ─────────────────────────────────────────
    print("\n[3/4] Création du manifeste...")
    manifest = _create_manifest(produced_files, generated_at)

    manifest_path = os.path.join(output_dir, "manifeste.json")
    with open(manifest_path, "w", encoding="utf-8") as f:
        json.dump(manifest, f, ensure_ascii=False, indent=2)
    produced_files["manifeste.json"] = manifest_path
    print(f"  [Manifeste] ✓ → {manifest_path}")

    # ── Étape 6 : Créer le ZIP livrable ──────────────────────────────────────
    print("\n[4/4] Compression ZIP...")
    zip_name = f"livrable_client_{part_id}.zip"
    zip_path = os.path.join(output_dir, zip_name)

    with zipfile.ZipFile(zip_path, "w", zipfile.ZIP_DEFLATED) as zf:
        for archive_name, filepath in produced_files.items():
            if os.path.exists(filepath):
                # arcname = nom dans l'archive (sans le chemin absolu)
                zf.write(filepath, arcname=archive_name)

    zip_size_kb = round(os.path.getsize(zip_path) / 1024, 1)
    print(f"  [ZIP] ✓ → {zip_path} ({zip_size_kb} KB)")

    # ── Résumé final ──────────────────────────────────────────────────────────
    print("\n" + "="*60)
    print(f"  Agent 9 terminé — {len(produced_files)} fichiers générés")
    print(f"  ZIP livrable : {zip_path}")
    print("="*60 + "\n")

    # Retourner le résultat (compatible avec le State LangGraph)
    return {
        "status": "success",
        "output_dir": output_dir,
        "zip_path": zip_path,
        "zip_size_kb": zip_size_kb,
        "files_generated": list(produced_files.keys()),
        "manifest": manifest,
        "generated_at": generated_at,
    }


# =============================================================================
# Nœud LangGraph
# Cette fonction est enregistrée dans le graphe LangGraph comme nœud "agent9".
# Elle lit le State global et met à jour la clé "agent9" avec les résultats.
# =============================================================================
def agent9_node(state: PipelineState) -> PipelineState:
    """
    Nœud LangGraph pour Agent 9.

    LangGraph appelle cette fonction avec le State complet du pipeline.
    On lit les sorties des agents 1→8 depuis state, on génère le catalogue,
    et on retourne le state mis à jour avec les résultats de l'agent 9.

    Usage dans le graphe :
        from agent9 import agent9_node
        graph.add_node("agent9", agent9_node)
        graph.add_edge("agent8", "agent9")
    """

    # Extraire les données des agents 1→8 depuis le State
    pipeline_data = {
        "agent1": state["agent1"],
        "agent2": state["agent2"],
        "agent3": state["agent3"],
        "agent4": state["agent4"],
        "agent5": state["agent5"],
        "agent6": state["agent6"],
        "agent7": state["agent7"],
        "agent8": state["agent8"],
    }

    # Lancer la génération
    result = run_agent9(pipeline_data)

    # Retourner le State mis à jour
    return {**state, "agent9": result}


# =============================================================================
# Point d'entrée standalone (test sans LangGraph)
# Lancer : python agent9.py
# =============================================================================
if __name__ == "__main__":
    from fake_data import FAKE_PIPELINE_DATA

    # Utiliser les données fake pour tester le pipeline complet
    result = run_agent9(
        pipeline_data=FAKE_PIPELINE_DATA,
        output_dir="./output_catalogue"
    )

    print("Fichiers générés :")
    for f in result["files_generated"]:
        print(f"  -> {f}")

    print(f"\nZIP livrable : {result['zip_path']}")