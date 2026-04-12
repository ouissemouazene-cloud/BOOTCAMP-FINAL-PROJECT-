# Agent 2 : Concepteur CAD/BIM (Digital Design)

## Rôle
Prend en entrée les spécifications techniques structurées (JSON) de l'Agent 1 et génère des plans de fabrication normalisés.

## Étapes de Travail (Workflow)

1. **Ingestion des Spécifications (JSON)** :
    - Récupération du JSON produit par l'Agent 1.
    - Identification des dimensions critiques (hauteur, diamètre, ports).

2. **Génération de Géométrie (Paramétrée)** :
    - Calcul des coordonnées pour les flasques, le corps de la vanne et les perçages.
    - Détermination des vues (Face, Profil, Dessus).

3. **Exportation CAD (DXF/DWG/IFC)** :
    - Création de fichiers au format d'échange industriel.
    - Utilisation d'outils comme `ezdxf` pour générer des fichiers DXF directement exploitables.

4. **Vérification de Conformité Industrielle** :
    - Vérification que les plans incluent les cartouches techniques et les échelles correctes.

## Sorties (Outputs)
- **Fichier DXF/DWG** : Plan de fabrication pour les 200 vannes.
- **Fichier IFC** : Modèle BIM pour l'intégration dans des complexes industriels.
- **État LangGraph** : Mise à jour de `state['cad_files']` pour l'Agent 3.

## Outils Open Source Potentiels
- `ezdxf` (Python library) pour la création de plans 2D.
- `ifcopenshell` pour l'exportation BIM.
- `OpenSCAD` (via script) pour la modélisation 3D paramétrique.
