# Agent 1 : Analyseur Technique (Technical Blueprint Analyzer)

## Rôle
Point d'entrée de INDUSTRIE IA. Transforme un document technique non structuré en une structure JSON exploitable pour la fabrication des 200 vannes haute pression.

## Étapes de Travail (Workflow)

1. **Ingestion & Conversion** :
    - Réception du fichier PDF provenant de sources open-source (GrabCAD/Thingiverse).
    - Conversion des pages en images haute résolution pour l'analyse visuelle.

2. **Extraction de Métadonnées Globales** :
    - Identification du nom de la pièce (ex : Vanne Haute Pression).
    - Identification du matériau spécifié (ex : Inox 316L, Acier A105).
    - Extraction des dimensions hors-tout.

3. **Analyse de la Nomenclature (BOM - Bill of Materials)** :
    - Détection automatique des tableaux de nomenclature sur le plan.
    - Identification des composants standards (visserie, joints) et des pièces à usiner.

4. **Identification des Contraintes Critiques** :
    - Extraction des tolérances géométriques et dimensionnelles importantes.
    - Repérage des exigences de rugosité (Ra) et des traitements de surface requis.
    - Identification de la classe de pression (Pressure Rating) (ex : PN-16, PN-100).

5. **Sortie Structurée** :
    - Génération de `technical_specs.json` pour alimenter l'Agent 2 (CAD/BIM).

## Spécifications de Sortie (Example JSON)
```json
{
  "project_id": "VHP-200-ALG",
  "part_name": "Vanne Industrielle",
  "material": "Inox 316L",
  "pressure_rating": "200 Bars",
  "bom": [ ... ]
}
```
