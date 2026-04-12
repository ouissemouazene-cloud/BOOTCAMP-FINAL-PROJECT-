# Agent 9 : Spécialiste Catalogue (Final Documentation)

## Rôle
Compile le travail des 8 autres agents dans un ensemble de documents professionnels prêts à être diffusés.

## Étapes de Travail (Workflow)

1. **Agrégation des Sorties Agents** :
    - Récupération du Plan CAD (A2), de la Vidéo (A3), des Prix (A5/A6), du Business Plan (A7) et de la Maintenance (A8).

2. **Génération Multiformat (Template-based)** :
    - **PDF** : Brochure commerciale pour impression.
    - **HTML** : Catalogue en ligne interactif.
    - **JSON/XML** : Pour intégration avec l'ERP ou le CRM de la PME.
    - **Excel** : Recapitulatif global pour la direction.

3. **Mise en Page AESTHETIC (Rich UI)** :
    - Utilisation de templates visuels impactants.
    - Insertion des images (Plan CAD, Animations).

4. **Archivage et Finalisation** :
    - Emballage du dossier complet (Zip) pour le client final.

## Sorties (Outputs)
- **Pack Final** : `INDUSTRIE_IA_CATALOGUE_FULL.zip`.
- **Catalogue PDF Principal** : `VHP-200_Catalogue.pdf`.
- **Catalogue HTML** : `index.html`.

## Outils Open Source Potentiels
- `Jinja2` pour le templating HTML.
- `Pandas/OpenPyXL` pour les fichiers Excel structurés.
- `PDFkit` ou `ReportLab` pour le catalogue PDF.
