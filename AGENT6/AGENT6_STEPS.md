# Agent 6 : Analyste Couts (Financial Calculation — TCO)

## Role
Calcule le Cout Total de Possession (TCO) pour la production des 200 vannes,
incluant la fabrication, la logistique et l'energie.
Genere les fichiers de sortie Excel, JSON et graphiques PNG.

## Etapes de Travail (Workflow)

1. **Calcul des Couts Directs (Materiaux)** :
    - Agregation des prix negocies par l'Agent 5 pour le lot de 200.
    - Estimation des consommables pour l'usinage (huile, fraises).

2. **Calcul des Couts Indirects (Usinage & Energie)** :
    - Calcul du temps d'usinage total (via Agent 1 Specs) multiplie par le cout horaire machine.
    - Estimation de la consommation electrique moyenne (kWh).

3. **Logistique et Transport** :
    - Frais de port, assurance et douanes (si importation d'Inox).

4. **Rentabilite et Marges** :
    - Etablissement de la repartition des couts.
    - Projection de l'evolution des couts sur 10 ans (+3%/an).

## Modifications Apportees (v2)

| # | Modification | Detail |
|---|-------------|--------|
| 1 | **Ajout graphique PNG (chart 1)** | `tco_breakdown_chart.png` — bar chart horizontal montrant la repartition des 4 composantes de couts avec pourcentages |
| 2 | **Ajout graphique PNG (chart 2)** | `tco_evolution_10ans.png` — bar chart vertical de l'evolution du cout total sur 10 ans (croissance +3%/an), 3 phases colorees : lancement / croissance / maturite |
| 3 | **Import matplotlib + numpy** | Ajout des librairies `matplotlib`, `matplotlib.patches`, `numpy` |
| 4 | **Mode Agg (sans ecran)** | `matplotlib.use("Agg")` — fonctionne en mode serveur/CI sans interface graphique |
| 5 | **Methode `_export_charts()`** | Nouvelle methode privee qui genere les 2 PNG dans `AGENT6/outputs/` |
| 6 | **JSON propre** | La cle `charts` (chemins locaux) est exclue du JSON exporte |
| 7 | **Chemins des charts dans state** | `state['financial_data']['charts']` contient les chemins des PNG pour les agents suivants |

## Sorties (Outputs) — Completes

| Fichier | Format | Description |
|---------|--------|-------------|
| `cost_analysis.json` | JSON | Donnees TCO structurees → Agent 7 |
| `cost_analysis.xlsx` | Excel | Tableau formate avec couleurs et formules |
| `tco_breakdown_chart.png` | PNG | Repartition des 4 composantes de couts |
| `tco_evolution_10ans.png` | PNG | Evolution du cout total sur 10 ans |

## Outils Utilises

- `openpyxl` — generation du fichier Excel formate
- `matplotlib` — generation des graphiques PNG
- `numpy` — calculs numeriques
- `json` — export de l'etat LangGraph
