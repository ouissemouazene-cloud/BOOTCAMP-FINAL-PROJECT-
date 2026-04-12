# =============================================================================
# generators/excel_gen.py
# Génération du fichier Excel via openpyxl
#
# Structure du fichier Excel produit :
#   Onglet 1 : Spécifications produit (Agent 1)
#   Onglet 2 : Fournisseurs & Négociation (Agents 4 & 5)
#   Onglet 3 : TCO — Coût Total de Possession (Agent 6)
#   Onglet 4 : Business Plan & Financiers (Agent 7)
#   Onglet 5 : Jumeau Numérique & Alertes (Agent 8)
#   Onglet 6 : Résumé exécutif (synthèse tous agents)
# =============================================================================

from openpyxl import Workbook
from openpyxl.styles import (
    Font, PatternFill, Alignment, Border, Side
)
from openpyxl.utils import get_column_letter
from models import PipelineData


# ── Palette de couleurs ────────────────────────────────────────────────────────
DARK_BLUE   = "1A3A5C"   # Entêtes principales
MID_BLUE    = "2563EB"   # Entêtes secondaires
LIGHT_BLUE  = "DBEAFE"   # Lignes alternées
RED_BG      = "FEE2E2"   # Alertes critiques
YELLOW_BG   = "FEF3C7"   # Alertes warning
GREEN_BG    = "D1FAE5"   # Valeurs positives
WHITE       = "FFFFFF"


def _header_style(cell, bg_color: str = DARK_BLUE, font_color: str = WHITE):
    """Applique le style entête à une cellule."""
    cell.font = Font(bold=True, color=font_color, size=11)
    cell.fill = PatternFill("solid", fgColor=bg_color)
    cell.alignment = Alignment(horizontal="center", vertical="center", wrap_text=True)


def _alt_row(ws, row: int, col_start: int, col_end: int):
    """Colorie une ligne en alternance (bleu clair)."""
    if row % 2 == 0:
        for col in range(col_start, col_end + 1):
            ws.cell(row=row, column=col).fill = PatternFill("solid", fgColor=LIGHT_BLUE)


def _set_col_widths(ws, widths: list):
    """Définit les largeurs de colonnes. widths = liste de largeurs."""
    for i, w in enumerate(widths, start=1):
        ws.column_dimensions[get_column_letter(i)].width = w


def _thin_border():
    """Retourne un style de bordure fine."""
    thin = Side(style="thin", color="CCCCCC")
    return Border(left=thin, right=thin, top=thin, bottom=thin)


# =============================================================================
# ONGLET 1 — Spécifications produit
# =============================================================================
def _sheet_specs(wb: Workbook, data: PipelineData):
    ws = wb.create_sheet("📋 Spécifications")
    s = data.agent1  # ProductSpecs

    # Titre
    ws.merge_cells("A1:B1")
    ws["A1"] = f"Spécifications — {s.part_name}"
    _header_style(ws["A1"])
    ws.row_dimensions[1].height = 30

    # Données en paires (label, valeur)
    rows = [
        ("Référence produit",       s.part_id),
        ("Diamètre nominal",        f"{s.diameter_mm} mm"),
        ("Pression nominale",       f"{s.pressure_bar} bar"),
        ("Matériau",                s.material),
        ("Poids unitaire",          f"{s.weight_kg} kg"),
        ("Tolérance dimensionnelle",f"± {s.tolerance_mm} mm"),
        ("Température max",         f"{s.temperature_max_celsius} °C"),
        ("Débit maximum",           f"{s.flow_rate_m3h} m³/h"),
        ("Durée de vie prévue",     f"{s.lifespan_years_expected} ans"),
    ]

    # Entêtes colonnes
    ws["A2"] = "Paramètre"
    ws["B2"] = "Valeur"
    _header_style(ws["A2"], MID_BLUE)
    _header_style(ws["B2"], MID_BLUE)

    for i, (label, val) in enumerate(rows, start=3):
        ws.cell(row=i, column=1, value=label)
        ws.cell(row=i, column=2, value=val)
        _alt_row(ws, i, 1, 2)

    _set_col_widths(ws, [30, 25])


# =============================================================================
# ONGLET 2 — Fournisseurs & Négociation
# =============================================================================
def _sheet_suppliers(wb: Workbook, data: PipelineData):
    ws = wb.create_sheet("🏭 Fournisseurs")
    src = data.agent4
    neg = data.agent5

    # Titre
    ws.merge_cells("A1:G1")
    ws["A1"] = f"Fournisseurs — {src.material_searched} ({src.suppliers_found} trouvés)"
    _header_style(ws["A1"])
    ws.row_dimensions[1].height = 28

    # Résultat négociation (bloc résumé)
    ws["A3"] = "Résultat négociation"
    _header_style(ws["A3"], MID_BLUE)
    ws.merge_cells("A3:G3")

    neg_info = [
        ("Fournisseur retenu",  f"{neg.winner} ({neg.winner_country})"),
        ("Prix initial",        f"${neg.initial_price_per_kg}/kg"),
        ("Prix négocié final",  f"${neg.final_price_per_kg}/kg"),
        ("Remise obtenue",      f"{neg.discount_percent}%"),
        ("Délai livraison",     f"{neg.delivery_days} jours"),
        ("Quantité contrat",    f"{neg.contract_quantity_kg:,} kg"),
        ("Coût total matière",  f"${neg.total_material_cost_usd:,.0f}"),
    ]
    for i, (k, v) in enumerate(neg_info, start=4):
        ws.cell(row=i, column=1, value=k).font = Font(bold=True)
        ws.cell(row=i, column=2, value=v)

    # Table des fournisseurs
    header_row = 13
    headers = ["Rang", "Nom", "Pays", "Prix $/kg", "Délai (j)", "Commande min (kg)", "Score fiabilité"]
    for col, h in enumerate(headers, start=1):
        cell = ws.cell(row=header_row, column=col, value=h)
        _header_style(cell, MID_BLUE)

    for i, s in enumerate(src.top_suppliers, start=header_row + 1):
        ws.cell(row=i, column=1, value=s.rank)
        ws.cell(row=i, column=2, value=s.name)
        ws.cell(row=i, column=3, value=s.country_name)
        ws.cell(row=i, column=4, value=s.price_per_kg_usd)
        ws.cell(row=i, column=5, value=s.lead_time_days)
        ws.cell(row=i, column=6, value=s.min_order_kg)
        ws.cell(row=i, column=7, value=s.reliability_score)

        # Surligner le fournisseur retenu en vert
        if s.name == neg.winner:
            for col in range(1, 8):
                ws.cell(row=i, column=col).fill = PatternFill("solid", fgColor=GREEN_BG)
        else:
            _alt_row(ws, i, 1, 7)

    _set_col_widths(ws, [8, 22, 15, 12, 12, 20, 16])


# =============================================================================
# ONGLET 3 — TCO
# =============================================================================
def _sheet_tco(wb: Workbook, data: PipelineData):
    ws = wb.create_sheet("💰 TCO")
    t = data.agent6

    ws.merge_cells("A1:C1")
    ws["A1"] = f"Coût Total de Possession — {t.horizon_years} ans"
    _header_style(ws["A1"])
    ws.row_dimensions[1].height = 28

    # Entêtes
    headers = ["Poste de coût", "Montant (USD)", "Note"]
    for col, h in enumerate(headers, start=1):
        _header_style(ws.cell(row=2, column=col, value=h), MID_BLUE)

    rows = [
        ("Quantité",                        t.quantity_units,                   f"{t.quantity_units} unités"),
        ("Coût unitaire",                   t.unit_cost_usd,                    "USD/unité"),
        ("Achat total",                     t.total_purchase_usd,               ""),
        ("Maintenance annuelle",            t.maintenance_cost_per_year_usd,    "$/an"),
        (f"Maintenance {t.horizon_years}ans", t.maintenance_10y_usd,            ""),
        ("Énergie annuelle",                t.energy_cost_per_year_usd,         "$/an"),
        (f"Énergie {t.horizon_years}ans",   t.energy_10y_usd,                   ""),
        ("Taux d'inflation DZ",             t.inflation_rate_dz_percent,        f"Source : {t.inflation_source}"),
        ("Sous-total avant inflation",      t.subtotal_before_inflation_usd,    ""),
        ("TOTAL AJUSTÉ INFLATION",          t.inflation_adjusted_total_usd,     "⚠ Valeur clé"),
        ("TCO par unité",                   t.tco_per_unit_usd,                 "USD/unité"),
    ]

    for i, (label, val, note) in enumerate(rows, start=3):
        ws.cell(row=i, column=1, value=label)
        # Formater comme monétaire si c'est un float > 1
        if isinstance(val, float) and val > 1:
            ws.cell(row=i, column=2, value=val).number_format = '#,##0.00'
        else:
            ws.cell(row=i, column=2, value=val)
        ws.cell(row=i, column=3, value=note)
        _alt_row(ws, i, 1, 3)

    # Surligner la ligne TOTAL en vert
    total_row = 12  # ligne "TOTAL AJUSTÉ"
    for col in range(1, 4):
        ws.cell(row=total_row, column=col).fill = PatternFill("solid", fgColor=GREEN_BG)
        ws.cell(row=total_row, column=col).font = Font(bold=True)

    _set_col_widths(ws, [35, 20, 30])


# =============================================================================
# ONGLET 4 — Business Plan
# =============================================================================
def _sheet_bp(wb: Workbook, data: PipelineData):
    ws = wb.create_sheet("📊 Business Plan")
    bp = data.agent7
    f = bp.financials

    ws.merge_cells("A1:D1")
    ws["A1"] = f"Business Plan — {bp.company_name}"
    _header_style(ws["A1"])
    ws.row_dimensions[1].height = 28

    # KPIs
    ws["A3"] = "KPIs clés"
    _header_style(ws.cell(row=3, column=1, value="Indicateur"), MID_BLUE)
    _header_style(ws.cell(row=3, column=2, value="Valeur"), MID_BLUE)

    kpis = [
        ("ROI",             f"{f.roi_percent}%"),
        ("VAN (NPV)",       f"${f.npv_usd:,.0f}"),
        ("Break-even",      f"{f.break_even_months} mois"),
        ("Marge année 1",   f"{f.margin_percent_year1}%"),
    ]
    for i, (k, v) in enumerate(kpis, start=4):
        ws.cell(row=i, column=1, value=k)
        ws.cell(row=i, column=2, value=v)
        _alt_row(ws, i, 1, 2)

    # Projections 3 ans
    proj_start = 10
    ws.merge_cells(f"A{proj_start}:D{proj_start}")
    ws.cell(row=proj_start, column=1, value="Projections financières 3 ans")
    _header_style(ws.cell(row=proj_start, column=1), DARK_BLUE)

    for col, h in enumerate(["Année", "Chiffre d'affaires", "Charges", "Bénéfice"], start=1):
        _header_style(ws.cell(row=proj_start + 1, column=col, value=h), MID_BLUE)

    proj_data = [
        (1, f.revenue_year1_usd, f.costs_year1_usd, f.profit_year1_usd),
        (2, f.revenue_year2_usd, f.costs_year2_usd, f.profit_year2_usd),
        (3, f.revenue_year3_usd, f.costs_year3_usd, f.profit_year3_usd),
    ]
    for i, (yr, rev, cost, profit) in enumerate(proj_data, start=proj_start + 2):
        ws.cell(row=i, column=1, value=f"Année {yr}")
        for col, val in enumerate([rev, cost, profit], start=2):
            c = ws.cell(row=i, column=col, value=val)
            c.number_format = '#,##0'
        _alt_row(ws, i, 1, 4)

    # SWOT
    swot_start = proj_start + 6
    ws.merge_cells(f"A{swot_start}:D{swot_start}")
    ws.cell(row=swot_start, column=1, value="Analyse SWOT")
    _header_style(ws.cell(row=swot_start, column=1), DARK_BLUE)

    swot_items = [
        ("Forces",         bp.swot.strengths,      GREEN_BG),
        ("Faiblesses",     bp.swot.weaknesses,      RED_BG),
        ("Opportunités",   bp.swot.opportunities,   LIGHT_BLUE),
        ("Menaces",        bp.swot.threats,         YELLOW_BG),
    ]
    r = swot_start + 1
    for category, items, color in swot_items:
        ws.cell(row=r, column=1, value=category).font = Font(bold=True)
        ws.cell(row=r, column=1).fill = PatternFill("solid", fgColor=color)
        for item in items:
            ws.cell(row=r, column=2, value=f"• {item}")
            r += 1
        r += 1

    _set_col_widths(ws, [25, 22, 22, 22])


# =============================================================================
# ONGLET 5 — Jumeau Numérique & Alertes
# =============================================================================
def _sheet_twin(wb: Workbook, data: PipelineData):
    ws = wb.create_sheet("🔧 Jumeau Numérique")
    tw = data.agent8

    ws.merge_cells("A1:F1")
    ws["A1"] = "Jumeau Numérique & Maintenance Prédictive"
    _header_style(ws["A1"])
    ws.row_dimensions[1].height = 28

    # Stats globales
    stats = [
        ("Période simulation",          tw.simulation_period),
        ("Score de santé final",         f"{tw.health_score_final}%"),
        ("Maintenance prévue",           tw.predicted_maintenance_date),
        ("Date panne prévue",            tw.predicted_failure_date),
        ("Durée de vie estimée",         f"{tw.estimated_lifespan_years} ans"),
        ("Nombre d'anomalies détectées", tw.sensor_stats.anomaly_count),
        ("Événements critiques",         tw.sensor_stats.critical_events),
        ("Température moy. (°C)",        tw.sensor_stats.avg_temperature_c),
        ("Pression moy. (bar)",          tw.sensor_stats.avg_pressure_bar),
        ("Vibration moy. (mm/s)",        tw.sensor_stats.avg_vibration_mm_s),
    ]

    for col, h in enumerate(["Indicateur", "Valeur"], start=1):
        _header_style(ws.cell(row=2, column=col, value=h), MID_BLUE)

    for i, (k, v) in enumerate(stats, start=3):
        ws.cell(row=i, column=1, value=k)
        ws.cell(row=i, column=2, value=v)
        _alt_row(ws, i, 1, 2)

        # Surligner score de santé selon valeur
        if k == "Score de santé final":
            color = GREEN_BG if tw.health_score_final > 75 else (YELLOW_BG if tw.health_score_final > 50 else RED_BG)
            for col in range(1, 3):
                ws.cell(row=i, column=col).fill = PatternFill("solid", fgColor=color)

    # Table des alertes
    alert_start = len(stats) + 5
    ws.merge_cells(f"A{alert_start}:F{alert_start}")
    ws.cell(row=alert_start, column=1, value="Alertes détectées")
    _header_style(ws.cell(row=alert_start, column=1), DARK_BLUE)

    for col, h in enumerate(["Mois", "Date", "Type", "Valeur", "Seuil", "Action recommandée"], start=1):
        _header_style(ws.cell(row=alert_start + 1, column=col, value=h), MID_BLUE)

    for i, a in enumerate(tw.alerts, start=alert_start + 2):
        ws.cell(row=i, column=1, value=a.month)
        ws.cell(row=i, column=2, value=a.date)
        ws.cell(row=i, column=3, value=a.type)
        ws.cell(row=i, column=4, value=a.value)
        ws.cell(row=i, column=5, value=a.threshold)
        ws.cell(row=i, column=6, value=a.recommended_action)

        # Couleur selon sévérité
        bg = RED_BG if a.severity == "critical" else YELLOW_BG
        for col in range(1, 7):
            ws.cell(row=i, column=col).fill = PatternFill("solid", fgColor=bg)

    _set_col_widths(ws, [8, 14, 20, 10, 10, 40])


# =============================================================================
# ONGLET 6 — Résumé exécutif
# =============================================================================
def _sheet_summary(wb: Workbook, data: PipelineData):
    ws = wb.create_sheet("📌 Résumé Exécutif")

    ws.merge_cells("A1:B1")
    ws["A1"] = f"Résumé Exécutif — {data.agent1.part_name}"
    _header_style(ws["A1"])
    ws.row_dimensions[1].height = 30

    summary = [
        ("Produit",                 data.agent1.part_name),
        ("Référence",               data.agent1.part_id),
        ("Matériau",                data.agent1.material),
        ("Quantité commandée",      f"{data.agent6.quantity_units} unités"),
        ("Fournisseur retenu",      data.agent5.winner),
        ("Prix négocié",            f"${data.agent5.final_price_per_kg}/kg"),
        ("TCO total (10 ans)",      f"${data.agent6.inflation_adjusted_total_usd:,.0f}"),
        ("TCO par unité",           f"${data.agent6.tco_per_unit_usd:,.2f}"),
        ("ROI",                     f"{data.agent7.financials.roi_percent}%"),
        ("Break-even",              f"{data.agent7.financials.break_even_months} mois"),
        ("Score santé jumeau",      f"{data.agent8.health_score_final}%"),
        ("Prochaine maintenance",   data.agent8.predicted_maintenance_date),
        ("Durée de vie estimée",    f"{data.agent8.estimated_lifespan_years} ans"),
    ]

    for col, h in enumerate(["Indicateur", "Valeur"], start=1):
        _header_style(ws.cell(row=2, column=col, value=h), MID_BLUE)

    for i, (k, v) in enumerate(summary, start=3):
        ws.cell(row=i, column=1, value=k).font = Font(bold=True)
        ws.cell(row=i, column=2, value=v)
        _alt_row(ws, i, 1, 2)

    _set_col_widths(ws, [30, 30])


# =============================================================================
# Fonction principale
# =============================================================================
def generate_excel(data: PipelineData, output_path: str) -> str:
    """
    Génère le fichier Excel complet avec 6 onglets.

    Args:
        data: PipelineData validé (toutes les sorties des agents 1-8)
        output_path: chemin du fichier .xlsx à créer

    Returns:
        Chemin du fichier créé
    """

    wb = Workbook()

    # Supprimer l'onglet vide créé par défaut
    wb.remove(wb.active)

    # Créer les 6 onglets dans l'ordre
    _sheet_summary(wb, data)    # Résumé en premier (onglet de couverture)
    _sheet_specs(wb, data)
    _sheet_suppliers(wb, data)
    _sheet_tco(wb, data)
    _sheet_bp(wb, data)
    _sheet_twin(wb, data)

    wb.save(output_path)
    print(f"  [Excel] ✓ Généré → {output_path} (6 onglets)")
    return output_path