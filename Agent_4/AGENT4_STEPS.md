# Agent 4 : Agent Sourcing (Supply Chain)

## Rôle
Identifie les fournisseurs pour les 200 vannes : matières premières (acier), composants standards (joints), et sous-traitants (usinage local ou import).

## Étapes de Travail (Workflow)

1. **Analyse de la Nomenclature (BOM)** :
    - Réception de la liste des composants identifiée par l'Agent 1.
    - Identification des pièces à acheter (Ex : Joint Viton, Boulons M12).

2. **Recherche de Fournisseurs (Local/International)** :
    - Scan d'annuaires industriels (Ex : Europages, ThomasNet, Pages Jaunes Algérie).
    - Utilisation d'APIs Open Data (ex: B2B directories) pour trouver des fonderies ou des revendeurs d'acier.

3. **Demande d'Offres (RFX Simulation)** :
    - Simulation d'envoi de demandes de devis pour un volume de 200 unités.

4. **Comparaison des Sources** :
    - Sélection des trois meilleures options (Prix bas, Proximité, Qualité).

## Sorties (Outputs)
- **Fichier JSON `suppliers_list.json`** : Contient les prix unitaires et les délais constatés.
- **État LangGraph** : Mise à jour de `state['suppliers_data']` pour l'Agent 5.

## Outils Open Source Potentiels
- `SerpAPI` ou `DuckDuckGo Search API` (via LangChain).
- `OpenCorporates` pour la vérification des entreprises.
- `Pandas` pour la structuration des données fournisseurs.
