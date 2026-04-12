# =============================================================================
# generators/xml_gen.py
# Génération du fichier XML via Jinja2 + validation lxml
#
# Processus :
#   1. Jinja2 rend le template catalogue.xml.j2 → string XML
#   2. lxml parse le string XML pour vérifier qu'il est bien formé
#   3. lxml re-sérialise avec pretty_print=True pour un XML lisible
#   4. Écriture du fichier final
# =============================================================================

from pathlib import Path
from jinja2 import Environment, FileSystemLoader
from lxml import etree

TEMPLATES_DIR = Path(__file__).parent.parent / "templates"


def generate_xml(context: dict, output_path: str) -> str:
    """
    Génère le catalogue en XML structuré.

    Args:
        context: dict avec toutes les données du pipeline
        output_path: chemin du fichier .xml à créer

    Returns:
        Chemin du fichier créé
    """

    # ── Étape 1 : Jinja2 → string XML brut ───────────────────────────────────
    env = Environment(
        loader=FileSystemLoader(str(TEMPLATES_DIR)),
        autoescape=False  # Pas d'autoescape : on génère du XML, pas du HTML
    )
    template = env.get_template("catalogue.xml.j2")
    xml_string = template.render(**context)

    # ── Étape 2 : Validation et pretty-print via lxml ─────────────────────────
    # lxml va lever une exception si le XML est mal formé (balises non fermées, etc.)
    try:
        root = etree.fromstring(xml_string.encode("utf-8"))
    except etree.XMLSyntaxError as e:
        raise ValueError(f"XML généré invalide : {e}") from e

    # ── Étape 3 : Écriture avec indentation propre ────────────────────────────
    tree = etree.ElementTree(root)
    tree.write(
        output_path,
        encoding="UTF-8",
        xml_declaration=True,    # Ajoute <?xml version="1.0" encoding="UTF-8"?>
        pretty_print=True        # Indentation lisible
    )

    print(f"  [XML] ✓ Généré → {output_path}")
    return output_path