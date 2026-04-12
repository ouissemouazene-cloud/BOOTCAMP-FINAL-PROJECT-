# Agent 7 : Stratege Business (Business Planning)

## Role
Prepare le plan strategique et decisionnel pour le directeur technique de la PME.
Genere un rapport complet avec analyse SWOT, calculs ROI/NPV/Breakeven,
et produit les fichiers de sortie Excel (3 feuilles) et PDF executif.

## Etapes de Travail (Workflow)

1. **Analyse de Marche (Algerie/Region)** :
    - Recuperation des tendances de prix de vente des vannes haute pression.
    - Analyse de la demande locale (Secteur petrolier, hydraulique).

2. **Elaboration de la Matrice SWOT** :
    - Forces (Proximite, Reactivite), Faiblesses (Cout matiere variable),
      Opportunites (Nouveaux marches), Menaces (Concurrence importee).

3. **Projections Financieres (3 Ans)** :
    - Calcul du Seuil de Rentabilite (Breakeven).
    - Calcul de la Valeur Actuelle Nette (VAN/NPV) avec taux d'actualisation a 8%.
    - Calcul du ROI (Return on Investment).

4. **Synthese de Rapport (Business Case)** :
    - Redaction du resume executif automatique.

## Modifications Apportees (v2)

| # | Modification | Detail |
|---|-------------|--------|
| 1 | **Export JSON** | `business_plan.json` — etat LangGraph complet transmis a Agent 8 |
| 2 | **Export Excel 3 feuilles** | `business_plan.xlsx` avec : Synthese Financiere + Analyse SWOT coloree + Projection NPV annuelle |
| 3 | **Export PDF executif** | `business_plan.pdf` — rapport ReportLab avec titre, tableau KPIs, SWOT, conclusion |
| 4 | **Calcul NPV reel** | Formule VAN avec taux d'actualisation 8% et croissance 10%/an sur 3 ans |
| 5 | **Calcul Breakeven** | Seuil de rentabilite calcule dynamiquement (couts fixes / marge de contribution) |
| 6 | **Calcul ROI reel** | ROI = (profit / cout total) x 100, compare automatiquement a la cible (25%) |
| 7 | **Marge configurable** | Parametre `selling_margin` (defaut 50%) facilement modifiable |
| 8 | **Resume executif auto** | Chaine de texte generee automatiquement avec tous les chiffres cles |
| 9 | **Methodes privees** | Code organise : `_calculate_roi()`, `_calculate_npv()`, `_calculate_breakeven()`, `_build_swot()` |

## Sorties (Outputs) — Completes

| Fichier | Format | Description |
|---------|--------|-------------|
| `business_plan.json` | JSON | Business Plan structure → Agent 8 |
| `business_plan.xlsx` | Excel | 3 feuilles : KPIs + SWOT + Projection NPV |
| `business_plan.pdf` | PDF | Rapport executif complet (ReportLab) |

## Indicateurs Calcules

| Indicateur | Valeur (exemple VHP-200) |
|------------|--------------------------|
| Cout unitaire | 19,825 DZD |
| Prix de vente unitaire | 29,738 DZD |
| ROI | 50.00% (cible : 25%) |
| VAN sur 3 ans | 18,511,530 DZD |
| Seuil de rentabilite | 323 unites |

## Outils Utilises

- `openpyxl` — generation du fichier Excel (3 feuilles, mise en forme coloree)
- `reportlab` — generation du rapport PDF executif
- `json` — export de l'etat LangGraph
