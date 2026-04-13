# Agent 8 : Expert Jumeau Numérique (Predictive Maintenance)

## Rôle
Assure la fiabilité des vannes après production en créant un jumeau numérique (Digital Twin) capable de générer des alertes de maintenance prédictive.

## Étapes de Travail (Workflow)

1. **Ingestion de Données Capteurs (Simulation)** :
    - Récupération de jeux de données historiques de pannes de vannes industrielles (via Kaggle open data).
    - Simulation de flux de capteurs (Vibration, Température, Pression).

2. **Entraînement de Modèle ML (Predictive)** :
    - Utilisation de modèles de classification (Random Forest/LSTM) pour prédire une défaillance de joint ou de tige.
    - Identification du temps restant avant défaillance (RUL - Remaining Useful Life).

3. **Génération d'Alertes Maintenance** :
    - Déclenchement automatique d'alertes en cas d'anomalies simulées.

4. **Synchronisation avec Agent 9** :
    - Intégration des recommandations de maintenance dans le catalogue final.

## Sorties (Outputs)
- **Fichier de Prédiction (Alerts)** : `maintenance_report.json`.
- **Fichier Machine Learning Model** : `predictive_model.pkl`.
- **État LangGraph** : Mise à jour de `state['maintenance_data']` pour l'Agent 9.

## Outils Open Source Potentiels
- `Kaggle API` pour les jeux de données techniques.
- `Scikit-Learn` ou `XGBoost` pour les modèles prédictifs.
- `Pandas` pour le nettoyage des données.
