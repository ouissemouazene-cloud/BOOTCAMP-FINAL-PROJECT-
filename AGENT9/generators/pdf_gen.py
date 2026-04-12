# =============================================================================
# generators/pdf_gen.py
# Génération du PDF via WeasyPrint + Jinja2
#
# Processus :
#   1. Jinja2 charge le template HTML (catalogue.html.j2)
#   2. Jinja2 injecte toutes les données dedans → HTML final en mémoire
#   3. WeasyPrint convertit ce HTML en PDF mise en page A4
#
# WeasyPrint gère les CSS @page, les page-breaks, les tableaux, etc.
# =============================================================================

import os
from pathlib import Path
from jinja2 import Environment, FileSystemLoader
from weasyprint import HTML as WeasyprintHTML

# Chemin absolu vers le dossier templates/
TEMPLATES_DIR = Path(__file__).parent.parent / "templates"


def generate_pdf(context: dict, output_path: str) -> str:
    """
    Génère le catalogue en PDF.

    Args:
        context: dict contenant toutes les données (specs, tco, bp, twin, etc.)
        output_path: chemin complet du fichier PDF à créer (ex: /tmp/catalogue.pdf)

    Returns:
        Le chemin du fichier PDF créé
    """

    # ── Étape 1 : Configurer Jinja2 pour lire le dossier templates/ ──────────
    env = Environment(
        loader=FileSystemLoader(str(TEMPLATES_DIR)),
        autoescape=True  # Échapper les caractères spéciaux HTML pour sécurité
    )
    template = env.get_template("catalogue.html.j2")

    # ── Étape 2 : Remplir le template avec les données → HTML string ─────────
    html_content = template.render(**context)

    # ── Étape 3 : WeasyPrint convertit le HTML en PDF ─────────────────────────
    # base_url permet à WeasyPrint de résoudre les ressources relatives (images CSS)
    WeasyprintHTML(
        string=html_content,
        base_url=str(TEMPLATES_DIR)
    ).write_pdf(output_path)

    print(f"  [PDF] ✓ Généré → {output_path}")
    return output_path