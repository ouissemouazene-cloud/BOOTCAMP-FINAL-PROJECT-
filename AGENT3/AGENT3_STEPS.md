# Agent 3 : Créateur Multimédia (Visual Marketing)

## Rôle
Améliore la présentation du produit en générant des supports visuels impactants (vidéos, animations 3D) montrant la vanne en action.

## Étapes de Travail (Workflow)

1. **Ingestion de Modèle (CAD)** :
    - Réception des fichiers produits par l'Agent 2.
    - Identification des pièces mobiles (tige, tournant, volant).

2. **Scénarisation (Prompts Vidéo)** :
    - Génération de scripts visuels décrivant le fonctionnement sous pression (ex : "Vue éclatée de la vanne en 3D montrant le passage du fluide à 200 Bars").
    - Utilisation d'un LLM pour rédiger des prompts détaillés pour des IA génératrices de vidéo (Kling, Luma, Sora).

3. **Génération d'Animations (Simulation Logicielle)** :
    - Exportation des animations de fonctionnement au format MP4 ou AVI.
    - Ajout de titrages techniques (dimensions, matériaux).

4. **Contrôle Qualité de Rendu** :
    - S'assurer que le rendu visuel est professionnel et prêt pour le catalogue.

## Sorties (Outputs)
- **Fichiers Vidéo/Anim** : `promotional_animation.mp4`, `exploded_view.avi`.
- **État LangGraph** : Mise à jour de `state['media_files']` pour l'Agent 4.

## Outils Open Source Potentiels
- `Manim` pour les animations mathématiques/techniques.
- `Blender` (scripté en Python) pour les rendus 3D photoréalistes.
- `MoviePy` pour le montage et l'ajout de texte.
