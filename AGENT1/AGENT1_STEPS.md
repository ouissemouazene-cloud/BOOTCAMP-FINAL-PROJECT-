# Agent 1 : Analyseur Technique (Technical Blueprint Analyzer)

## Rôle
Point d'entrée de INDUSTRIE IA. L'agent utilise **pdfplumber** et un LLM pour extraire les données techniques critiques nécessaires à la fabrication des 200 vannes.

## Données à Extraire (Cibles)
1.  **Dimensions** : Hauteur, diamètre, entraxes des perçages.
2.  **Matériaux** : Nuance d'acier (Inox 316, A105, etc.).
3.  **Tolérances** : Exigences de précision (H7, g6, rugosité Ra).
4.  **Pression Nominale (PN)** : Capacité de résistance (ex: PN16, PN200).

## Étapes de Travail (Workflow)

1. **Ingestion & Parsing PDF** :
    - Ouverture du fichier technique via `pdfplumber`.
    - Extraction du texte brut et des données de tableaux de nomenclature.

2. **Analyse LLM (Contextualisation)** :
    - Envoi du texte extrait à un LLM avec un prompt structuré.
    - Identification précise des 4 points clés (Dimensions, Matériaux, Tolérances, PN).

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
