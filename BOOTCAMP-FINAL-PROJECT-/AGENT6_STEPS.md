# Agent 6 : Analyste Coûts (Financial Calculation)

## Rôle
Calcule le Coût Total de Possession (TCO) pour la production des 200 vannes, incluant la fabrication, la logistique et l'énergie.

## Étapes de Travail (Workflow)

1. **Calcul des Coûts Directs (Matériaux)** :
    - Agrégation des prix négociés par l'Agent 5 pour le lot de 200.
    - Estimation des consommables pour l'usinage (huile, fraises).

2. **Calcul des Coûts Indirects (Usinage & Énergie)** :
    - Calcul du temps d'usinage total (via Agent 1 Specs) multiplié par le coût horaire machine.
    - Estimation de la consommation électrique moyenne (kWh).

3. **Logistique et Transport** :
    - Calcul du poids total pour 200 vannes.
    - Frais de port, assurance et douanes (si importation d'Inox).

4. **Rentabilité et Marges** :
    - Établissement de la répartition des coûts (Graphe).

## Sorties (Outputs)
- **Fichier Excel/JSON `cost_analysis.xlsx`** : Détail complet des coûts.
- **État LangGraph** : Mise à jour de `state['financial_data']` pour l'Agent 7.

## Outils Open Source Potentiels
- `OpenPyXL` pour la génération des fichiers Excel.
- `Matplotlib/Seaborn` pour la visualisation des répartitions de coûts.
- `NumPy` pour les calculs de rentabilité.
