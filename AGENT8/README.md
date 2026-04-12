# 🤖 Module 8 : Jumeau Numérique & Maintenance Prédictive (INDUSTRIE IA)

Ce module représente **l'Agent 8** du challenge final de l'initiative *OpenIndustry Algérie* (Bootcamp IA 2026). 
Son rôle est de créer un **Jumeau Numérique (Digital Twin)** d'une vanne industrielle haute pression (DN100 PN40) et de simuler son comportement sur un an (8760 heures) afin de prédire les pannes et de générer des recommandations de maintenance.

Ce projet s'intègre dans le pipeline LangGraph global mais peut également être exécuté de manière autonome.

---

## 🛠️ Pré-requis & Installation

Les modèles de prédiction utilisent **PyTorch** et l'analyse intelligente nécessite **Ollama** (avec le modèle Mistral) pour simuler la phase d'hyper-raisonnement.

1. **Installer les dépendances Python :**
   ```bash
   pip install pandas numpy scipy scikit-learn python-dateutil jsonschema langgraph langchain langchain-community
   ```

2. **Installer PyTorch :**
   *(Pour CPU ou CUDA en fonction de votre système)*
   ```bash
   pip install torch torchvision torchaudio
   ```

3. **Installer Ollama (optionnel mais recommandé) :**
   Pour profiter du raisonnement par LLM local (gratuit), téléchargez [Ollama](https://ollama.com/) et lancez :
   ```bash
   ollama run mistral
   ```
   *(Note : Si Ollama n'est pas disponible ou manque de RAM, le script est conçu pour basculer intelligemment sur un plan de secours rule-based, garantissant la fluidité du pipeline complet).*

---

## 🚀 Exécution Standalone

Vous pouvez tester l'agent 8 indépendamment du reste du pipeline LangGraph :

```bash
python agent8_full.py
```

### Visualisation 3D 
L'Agent 8 génère un fichier JSON compatible 3D (`outputs/digital_twin_3d.json`).
Un script de visualisation rapide HTML est disponible. Pour le voir :
1. Lancez un serveur local rapide : `python -m http.server 8000`
2. Ouvrez : `http://localhost:8000/outputs/viewer.html`

---

## 🧠 Architecture & Méthodes (Les 8 Étapes)

Le code (dans `agent8_full.py`) est segmenté en 8 blocs clairs et s'appuie sur trois bases de données (NASA CMAPSS, Kaggle Pump Sensor, Kaggle AI4I 2020) :

### 1- Initialisation & Ingestion avec LLM
- **Chargement** des spécifications extraites par l'Agent 1.
- Le LLM Mistral **lit les spécifications dynamiquement** et déduit de façon autonome les seuils de risque (Warning / Critical) sans aucun hardcoding.
- Utilisation du *Maximum Likelihood Estimation (MLE)* pour extraire des modèles paramétriques sur les distributions historiques de nos bases "Open Data".

### 2- Simulation de Monte Carlo
- Simulation de **8760 heures** de données (1 an) pour la température, la pression, le débit et les vibrations.
- Injection d'un bruit stochastique, de vagues saisonnières (ex: canicule en Algérie affectant la température ambiante) et d'événements aléatoires destructeurs (processus de Poisson).

### 3- Détection Multicouches des Anomalies
- **1. Seuils Statiques :** (définis par le LLM).
- **2. Z-Score :** Détection purement statistique (>3 écarts types).
- **3. Modèle Autoencodeur Deep Learning (PyTorch) :** Construit une représentation compacte des opérations normales. Lors de l'inférence, toute erreur de reconstruction massive signale une anomalie multivariée complexe.
- **4. Alertes de Tendances :** Analyse des moyennes mobiles sur 72h pour identifier l'usure précoce.

### 4- Génération Intelligente d'Alertes
- Face à une panne critique (TWF, PWF, HDF, etc.), **l'Agent LLM (Mistral)** consolide toutes les variables (historique, durée et criticité) pour générer une **recommandation de réparation textuelle concise et très précise**.

### 5- Calcul du Score de Santé (MCDA)
- Utilisation de la méthode mathématique MCDA (Multi-Criteria Decision Analysis) pondérant précisément le volume de pannes, les altérations de capteurs et le RUL estimé pour générer un **Score de Santé sur 100**.

### 6- Prédiction du RUL (Remaining Useful Life) par LSTM
- Un réseau récurrent **LSTM (Long Short-Term Memory, PyTorch)** est entraîné sur les cycles de dégradation de la base NASA.
- Lors de l'inférence, notre agent passe ses courbes de mesure réelles à travers le réseau LSTM pour deviner avec exactitude le mois de **Maintenance requise** et le mois de **Panne critique** (Failure Date).
- *Fallback :* En cas d'incompatibilité avec le modèle, un classificateur linéaire (Regression Lineaire) prend le relais pour sécuriser l'orchestration.

### 7- Exportation de la Scène 3D
- Construction d'une configuration **Three.js format JSON** embarquant les couleurs qui réagissent selon la criticité des différentes zones de la vanne. Ce JSON sera lu par l'Agent 9 pour générer un catalogue interactif.

### 8- Validation LLM & Schema
- Une dernière itération **Ollama/Mistral** valide la cohérence générale de toute l'intervention (ex: Vérifie qu'il n'y ait pas un Status "Critique" en parallèle d'un Score à "99/100").
- L'enregistrement du dictionnaire LangGraph officiel est validé via **JSONSchema**.
