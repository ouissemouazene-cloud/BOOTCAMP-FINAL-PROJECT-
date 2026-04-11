# Agent 7 : Stratège Business (Business Planning)

## Rôle
Prépare le plan stratégique et décisionnel pour le directeur technique de la PME.

## Étapes de Travail (Workflow)

1. **Analyse de Marché (Algérie/Region)** :
    - Récupération des tendances de prix de vente des vannes haute pression.
    - Analyse de la demande locale (Secteur pétrolier, hydraulique).

2. **Élaboration de la Matrice SWOT** :
    - Forces (Proximité, Réactivé), Faiblesses (Coût matière variable), Opportunités (Nouveaux marchés), Menaces (Concurrence importée).

3. **Projections Financières (3 Ans)** :
    - Calcul du Seuil de Rentabilité (Break-even node).
    - Calcul de la Valeur Actuelle Nette (VAN/NPV) et du Temps de Retour sur Investissement (ROI).

4. **Synthèse de Rapport (Business Case)** :
    - Rédaction du résumé exécutif.

## Sorties (Outputs)
- **Fichier Business Plan (PDF)** : `business_plan.pdf`.
- **État LangGraph** : Mise à jour de `state['business_plan']` pour l'Agent 8.

## Outils Open Source Potentiels
- `ReportLab` ou `FPDF` pour générer le rapport PDF.
- `Google Search API` (SERP) pour les tendances de marché.
- `LangChain chains` pour synthétiser le contenu.
