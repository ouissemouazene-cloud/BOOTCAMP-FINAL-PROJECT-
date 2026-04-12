# =============================================================================
# generators/html_gen.py
# Génération du fichier HTML via Jinja2
#
# C'est le format le plus simple : on réutilise exactement le même template
# que pour le PDF. Le HTML produit est autonome (pas de dépendances externes)
# et peut être ouvert directement dans un navigateur.
# =============================================================================

from pathlib import Path
from jinja2 import Environment, FileSystemLoader

TEMPLATES_DIR = Path(__file__).parent.parent / "templates"


def generate_html(context: dict, output_path: str) -> str:
    """
    Génère le catalogue en HTML.

    Args:
        context: dict avec toutes les données du pipeline
        output_path: chemin du fichier .html à créer

    Returns:
        Chemin du fichier créé
    """

    # ── Charger et remplir le template Jinja2 ────────────────────────────────
    env = Environment(
        loader=FileSystemLoader(str(TEMPLATES_DIR)),
        autoescape=True
    )
    template = env.get_template("catalogue.html.j2")
    html_content = template.render(**context)

    # ── Écrire le fichier HTML final ──────────────────────────────────────────
    with open(output_path, "w", encoding="utf-8") as f:
        f.write(html_content)

    print(f"  [HTML] ✓ Généré → {output_path}")
    return output_path