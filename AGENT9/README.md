# 📦 Module 9 : Catalogue Exporter (INDUSTRIE IA)

Ce module représente **l'Agent 9**, le tout dernier agent du pipeline pour le challenge final de l'initiative *OpenIndustry Algérie* (Bootcamp IA 2026). 

Son rôle est capital : il consolide la totalité des informations générées par les 8 agents précédents, valide l'intégrité de ces données via **Pydantic**, puis les compile en **cinq formats différents** (HTML, PDF, Excel, JSON, XML). Il génère enfin un manifeste d'intégrité (hash SHA-256) et compresse le tout sous forme d'une archive `.zip` livrable au client.

---

## 🛠️ Pré-requis & Installation

Ce module nécessite plusieurs bibliothèques de génération de documents (openpyxl, weasyprint, jinja2, lxml).

1. **Installer les dépendances Python :**
   ```bash
   pip install -r requirements.txt
   ```

2. **Note spécifique pour le PDF (WeasyPrint sous Windows) :**
   Si vous êtes sous Windows, WeasyPrint nécessite les bibliothèques **GTK3** pour fonctionner. Si GTK3 n'est pas détecté, l'Agent 9 ne crashera pas : il capturera l'exception (`OSError`) grâce à son fallback sécurisé et continuera la génération des autres formats sans le PDF.

---

## 🚀 Exécution & Tests

### Exécution Autonome (Standalone)
Vous pouvez tester l'agent 9 de manière isolée avec des fausses données issues du pipeline complet :

```bash
python agent9.PY
```
Cela générera un dossier `output_catalogue/` à la racine de l'agent contenant tous les formats générés ainsi que l'archive finale.

### Tests Unitaires
Les tests unitaires assurent la validation du pipeline, couvrant les cas conformes et les mauvaises structurations de données :

```bash
python -m pytest tests/ -v
```
Les tests valident la structure XML, le nombred'onglets Excel, le parsing HTML, la présence du manifeste, etc.

---

## 🧠 Architecture & Méthodes

Le code est architecturé autour d'un principe de séparation des responsabilités. Le fichier principal `agent9.PY` orchestre le flux, tandis que les dossiers `generators/` et `templates/` concentrent la logique propre à chaque format.

### 1- Validation Pydantic
Dès sa prise en main des données du *State* global de LangGraph, l'agent utilise le modèle **`PipelineData(**pipeline_data)`** décrit dans `models.py`. Si le moindre champ attendu par nos spécifications est manquant ou ne correspond pas au bon format, une `ValidationError` est levée, empêchant la génération d'un livrable défectueux.

### 2- Dossier `generators/` (Les 5 Formats)
- **`html_gen.py` :** Injecte les variables système (`specs`, `twin`, `bp`, etc.) dans notre template Jinja2 respectif pour produire un HTML web autonome.
- **`pdf_gen.py` :** Convertit précisément le résultat HTML mentionné précédemment en un document imprimable PDF en respectant un format de dimensions exact via `WeasyPrint`.
- **`excel_gen.py` :** Conçu via `openpyxl`, il met un point d'honneur sur la lisibilité humaine et génère 6 onglets hautement stylisés contenant respectivement (Résumé, Spécifications, Fournisseurs, Coûts TCO, Business Plan, Jumeau Numérique).
- **`xml_gen.py` :** Assure la compatibilité machine industrielle, il intègre à un modèle Jinja2 la structuration imposée puis est validé via **LXML** pour vous assurer qu'aucune balise n'ait été mal formée.
- **`json_gen.py` :** Simplifie les données en une structure hiérarchique idéale pour un développement API.

### 3- L'archive Automatisée et le Hash 
Afin d'assurer l'**intégrité du livrable final**, l'agent produit un document nommé `manifeste.json`. Ce dernier référence les 5 fichiers, leur taille exacte générée, et applique un calcul **SHA-256**. L'agent englobe le tout grâce à `zipfile`.

### 4- Intégration LangGraph
La fonction `agent9_node(state: PipelineState)` est l'unique point d'entrée pour le Node LangGraph. Elle récupère le `state` issu du dictionnaire de l'Agent 8, s'infiltre dans le processus de génération (`run_agent9`), met à jour ce dict avec les chemins vers le `<dossier source>` des exports et son archive validée, puis renvoie la boucle finale de notre **INDUSTRIE IA**.
