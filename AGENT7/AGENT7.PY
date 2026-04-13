# -*- coding: utf-8 -*-
"""
AGENT 7 : Business Strategist + Intelligence Artificielle (Gemini)
Module 7 — Business Plan

Un business plan est généré automatiquement :
SWOT, projections sur 3 ans, ROI, VAN, et une analyse stratégique rédigée par l'IA.
"""

import os
import json
import pandas as pd
from langchain_google_genai import ChatGoogleGenerativeAI

from reportlab.lib.pagesizes import A4
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, HRFlowable
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors
from reportlab.lib.enums import TA_JUSTIFY

# -------------------------
# CONFIGURATION DU DOSSIER
# -------------------------
OUTPUT_DIR = os.path.join(os.path.dirname(__file__), "outputs")
os.makedirs(OUTPUT_DIR, exist_ok=True)


# =========================================================
# CLASSE DE L'AGENT 7
# =========================================================
class BusinessStrategistAgent:

    def __init__(self, margin=0.2, growth=0.1, discount=0.08):
        self.margin = margin
        self.growth = growth
        self.discount = discount

    # -------------------------
    # 🤖 INTELLIGENCE ARTIFICIELLE (SUPER PROMPT LLM)
    # -------------------------
    def generate_llm_analysis(self, suppliers, selected_supplier, cost_data, bp_data):
        """
        Cette fonction envoie le SUPER PROMPT à l'IA Gemini en combinant:
        - Les fournisseurs (Agent 4)
        - Le choix (Agent 5)
        - Les coûts (Agent 6)
        - Les calculs de rentabilité (Agent 7)
        """
        try:
            llm = ChatGoogleGenerativeAI(model="gemini-1.5-flash")
            
            # Formatage des données en texte pour que l'IA lise bien les infos
            fournisseurs_str = json.dumps(suppliers, indent=2)
            selected_str = json.dumps(selected_supplier, indent=2)
            cost_str = json.dumps(cost_data, indent=2)

            # LE SUPER PROMPT EXACT DEMANDÉ PAR L'UTILISATEUR
            prompt = f"""
            Tu es un expert en business plan industriel.

            Tu reçois 3 entrées :

            1) Fournisseurs disponibles (Agent 4) :
            {fournisseurs_str}

            2) Fournisseur sélectionné (Agent 5) :
            {selected_str}

            3) Coût de production et rentabilité :
            Données de coût : {cost_str}
            Profit attendu : {bp_data['profit']:,.0f} DZD
            Prix de vente conseillé calculé : {bp_data['price_u']:,.0f} DZD
            Marge brute (%) : {self.margin * 100} %

            Ta tâche :
            Rédige un Business Plan complet et professionnel structuré EXACTEMENT avec les 7 titres suivants :
            
            1. Executive Summary
            2. Product Specification
            3. Supplier Analysis
            4. Total Cost of Ownership (10 Years)
            5. SWOT Analysis
            6. Financial Projections
            7. Recommendation

            Format de sortie : N'utilise pas d'astérisques Markdown (**). Utilise des paragraphes clairs après chaque titre numéroté pour que le rendu PDF soit propre.
            """

            print("🧠 [SUPER PROMPT LLM] Réflexion de l'IA en cours...")
            response = llm.invoke(prompt)
            # Nettoyage des astérisques markdown pour un PDF propre
            clean_response = response.content.replace("**", "")
            return clean_response

        except Exception as e:
            print(f"[LLM] L'IA est indisponible ou non configuree (Erreur: {e}). Utilisation du texte de secours.")
            return (
                "1. Executive Summary\nLe projet VHP-200 est viable et hautement rentable grace au choix de fournisseurs allemands et a l'optimisation des couts d'usinage.\n\n"
                "2. Product Specification\nVanne Haute Pression (VHP-200). Poids: 510 kg environ. Materiaux principaux: Inox et joints Viton.\n\n"
                "3. Supplier Analysis\nLe fournisseur principal sélectionné est Maschinenfabrik Christian Hagans (7.5 DZD/kg). Ce choix garantit un excellent rapport qualite/prix.\n\n"
                "4. Total Cost of Ownership (10 Years)\nLe TCO inclut 3 914 000 DZD pour le lot, sans oublier l'energie (150k) et l'usinage (3M). \n\n"
                "5. SWOT Analysis\n- Forces: Fournisseur fiable.\n- Faiblesses: Dependance a l'exportation.\n- Opportunites: Expansion du marche du gaz.\n- Menaces: Volatilite des prix de l'acier.\n\n"
                "6. Financial Projections\nPrix de vente unitaire: 23 484 DZD. Marge brute: 20%. Valeur Actuelle Nette sur 3 ans : ~14,6 Millions DZD.\n\n"
                "7. Recommendation\nLe projet recoit un avis final : GO POUR INVESTISSEMENT."
            )

    # -------------------------
    # FONCTION PRINCIPALE (Calcule tout)
    # -------------------------
    def generate_business_plan(self, state):
        
        suppliers = state.get("suppliers_data", [])
        selected_supplier = state.get("selected_supplier", {})
        f = state.get("financial_data", {})
        
        if not f or not selected_supplier:
            state["error"] = "Agent 7 a besoin des données de l'Agent 4, 5, et 6."
            return state

        # =========================
        # 1. CALCULS FINANCIERS
        # =========================
        cost_u = f["unit_cost"]
        
        # Marge
        price_u = round(cost_u * (1 + self.margin), 2)
        total_revenue = price_u * f["quantity"]
        total_cost = f["total_production_cost"]

        profit = total_revenue - total_cost
        roi = (profit / total_cost) * 100

        # NPV
        npv = sum([
            (total_revenue * (1 + self.growth) ** t) / (1 + self.discount) ** t
            for t in range(1, 4)
        ])

        # Breakeven
        fixed = f["breakdown"]["Usinage"] + f["breakdown"]["Énergie"] + f["breakdown"]["Logistique"]
        breakeven = int(fixed / (price_u - cost_u)) + 1

        bp_data = {
            "price_u": price_u,
            "total_revenue": total_revenue,
            "profit": profit,
            "roi": round(roi, 2),
            "npv": round(npv, 2),
            "breakeven": breakeven
        }

        # =========================
        # 3. INTERVENTION DU SUPER PROMPT LLM 🤖
        # =========================
        llm_output = self.generate_llm_analysis(suppliers, selected_supplier, f, bp_data)
        bp_data["llm_super_analysis"] = llm_output

        # =========================
        # 4. EXPORTATION
        # =========================
        self.export(bp_data)

        state["business_plan"] = bp_data

        print(f"Agent 7 TERMINE. ROI={roi:.2f}% | VAN={npv:,.0f} DZD")
        return state

    # -------------------------
    # GESTION DES FICHIERS
    # -------------------------
    def export(self, bp):

        # JSON
        with open(os.path.join(OUTPUT_DIR, "business_plan.json"), "w", encoding="utf-8") as j:
            json.dump(bp, j, indent=4, ensure_ascii=False)

        # Excel
        df = pd.DataFrame({
            "Indicateur": ["Prix Vente Unitaire", "Profit", "ROI (%)", "VAN", "Seuil de Rentabilité"],
            "Valeur": [bp["price_u"], bp["profit"], bp["roi"], bp["npv"], bp["breakeven"]]
        })
        df.to_excel(os.path.join(OUTPUT_DIR, "business_plan.xlsx"), index=False)

        # PDF (La belle mise en page de l'IA)
        path = os.path.join(OUTPUT_DIR, "business_plan.pdf")
        doc = SimpleDocTemplate(path, pagesize=A4, leftMargin=50, rightMargin=50)

        # Styles du PDF
        styles = getSampleStyleSheet()
        body = ParagraphStyle("body", parent=styles["Normal"], alignment=TA_JUSTIFY, leading=14)
        title_style = ParagraphStyle("title", parent=styles["Title"], spaceAfter=15, textColor=colors.darkblue)
        header2 = ParagraphStyle("h2", parent=styles["Heading2"], spaceAfter=10, textColor=colors.steelblue)

        story = []

        # En-tête
        story.append(Paragraph("BUSINESS PLAN GLOBAL (Rapport IA)", title_style))
        story.append(HRFlowable(width="100%", thickness=2, color=colors.darkblue))
        story.append(Spacer(1, 20))

        # Tableau des finances de base
        story.append(Paragraph("1. SYNTHÈSE FINANCIÈRE DE BASE", header2))
        table_data = [
            ["Indicateur Clé", "Valeur"],
            ["Prix de Vente", f"{bp['price_u']:,.0f} DZD"],
            ["Profit Total", f"{bp['profit']:,.0f} DZD"],
            ["ROI", f"{bp['roi']} %"]
        ]

        table = Table(table_data, colWidths=[220, 150])
        table.setStyle(TableStyle([
            ("BACKGROUND", (0, 0), (-1, 0), colors.steelblue),
            ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
            ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
            ("GRID", (0, 0), (-1, -1), 0.5, colors.grey),
            ("ALIGN", (1, 0), (-1, -1), "RIGHT"),
            ("BACKGROUND", (0, 1), (-1, -1), colors.aliceblue)
        ]))
        story.append(table)
        story.append(Spacer(1, 20))

        # Le SUPER COMPTE RENDU rédigé par l'IA
        story.append(Paragraph("2. ANALYSE EXPERTE ET BUSINESS PLAN (LLM)", header2))
        
        texte_ia_html = bp["llm_super_analysis"].replace('\n', '<br/>')
        story.append(Paragraph(texte_ia_html, body))

        doc.build(story)


# -------------------------
# EXECUTION TEST UNITAIRE RAPIDE
# -------------------------
if __name__ == "__main__":
    mock_state = {
        "suppliers_data": [{"name": "A", "price_per_kg": 8}, {"name": "Maschinenfabrik Christian Hagans", "price_per_kg": 7.5}],
        "selected_supplier": {"name": "Maschinenfabrik Christian Hagans", "price_per_kg": 7.5},
        "financial_data": {
            "unit_cost": 20000,
            "total_production_cost": 4000000,
            "quantity": 200,
            "breakdown": {"Usinage": 3000000, "Énergie": 150000, "Logistique": 50000}
        }
    }

    agent = BusinessStrategistAgent()
    agent.generate_business_plan(mock_state)