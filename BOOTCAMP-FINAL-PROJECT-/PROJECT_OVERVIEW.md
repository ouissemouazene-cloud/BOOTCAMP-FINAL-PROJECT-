# INDUSTRIE IA : Modernisation de l'Usinage en Algérie

## Contexte
OpenIndustry Algérie est une initiative citoyenne visant à démocratiser l'Industrie 4.0 pour les PME algériennes. Ce système multi-agents automatise le cycle complet de production, de la lecture du plan technique au catalogue final.

### Demande Spécifique
Production de **200 vannes industrielles haute pression** à partir d'un plan public (PDF).

## Architecture des 9 Agents (LangGraph)

| Agent | Nom | Rôle | Format de Sortie |
| :--- | :--- | :--- | :--- |
| **1** | **Analyseur Technique** | Extraction de specs (Vision LLM/PDF) | JSON |
| **2** | **Concepteur CAD/BIM** | Plans 2D/3D normalisés | DXF, DWG, IFC |
| **3** | **Créateur Multimédia** | Vidéos promotionnelles / Animations | MP4, AVI |
| **4** | **Agent Sourcing** | Identification Fournisseurs (Local/Intl) | JSON |
| **5** | **Négociateur IA** | Simulation de négociation (Volume 200) | Text, Audio |
| **6** | **Analyste Coûts** | Calcul du TCO (Logistique, Énergie) | Excel, JSON |
| **7** | **Stratège Business** | Business Plan (SWOT, ROI, NPV) | PDF |
| **8** | **Expert Jumeau Numérique** | Maintenance prédictive (Kaggle Data) | Alerts |
| **9** | **Spécialiste Catalogue** | Compilation finale multi-format | PDF, HTML, XML |

## État actuel
- Agent 1 : Défini et Implémenté (Prototype).
- Orchestration : LangGraph (Structure de base).
