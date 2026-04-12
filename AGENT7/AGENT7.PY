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
    # 🤖 INTELLIGENCE ARTIFICIELLE (Gemini LLM)
    # -------------------------
    def generate_llm_analysis(self, bp_data):
        """
        Cette fonction envoie les calculs à l'IA Gemini.
        L'IA joue le rôle d'un expert et rédige un texte d'analyse pour le PDF.
        """
        try:
            # 1. On prépare le "Cerveau" Gemini (modèle rapide flash)
            # ⚠️ Si la clé GOOGLE_API_KEY n'est pas configurée dans l'ordinateur,
            #    le code passera dans le bloc "except" pour ne pas bloquer.
            llm = ChatGoogleGenerativeAI(model="gemini-1.5-flash")
            
            # 2. On rédige la consigne (Prompt) pour l'IA
            prompt = f"""
            Tu es un consultant en stratégie industrielle de haut niveau pour l'entreprise 'MechanoDZ'.
            
            Analyse brièvement le projet de vannes haute pression avec ces données exactes :
            - Profit généré : {bp_data['profit']:,.0f} DZD
            - Retour sur Investissement (ROI) : {bp_data['roi']} %
            - Valeur Actuelle Nette (VAN) : {bp_data['npv']:,.0f} DZD
            - Seuil de rentabilité : {bp_data['breakeven']} unités

            Rédige DEUX petits paragraphes :
            1. Une conclusion sur la viabilité financière de l'usine.
            2. Une recommandation stratégique sur le marché algérien.
            
            Format attendu : Un texte direct, clair, professionnel. Pas de liste à puces.
            """

            # 3. L'IA réfléchit et génère le texte
            print("[LLM] Réflexion de l'IA en cours...")
            response = llm.invoke(prompt)
            return response.content

        except Exception as e:
            # PLAN B : Si l'IA n'arrive pas à se connecter (pas de clé API),
            # on donne un texte par défaut pour que l'exécution continue sans bloquer !
            print(f"[LLM] L'IA est indisponible ou non configuree (Erreur: {e}). Utilisation du texte de secours.")
            return (
                "Analyse générée automatiquement (Mode Hors-Ligne) : "
                "Le projet présente des indicateurs financiers solides. "
                "Le retour sur investissement et la VAN positive justifient le lancement "
                "immédiat de la production de vannes pour le marché algérien."
            )

    # -------------------------
    # FONCTION PRINCIPALE (Calcule tout)
    # -------------------------
    def generate_business_plan(self, state):
        
        # On vérifie qu'on a bien reçu les données de l'Agent 6
        f = state.get("financial_data", {})
        if not f:
            state["error"] = "Agent 7 a besoin des données de l'Agent 6."
            return state

        # =========================
        # 1. CALCULS FINANCIERS
        # =========================
        cost_u = f["unit_cost"]
        
        # Prix de vente = cout + marge
        price_u = round(cost_u * (1 + self.margin), 2)
        total_revenue = price_u * f["quantity"]
        total_cost = f["total_production_cost"]

        # Le profil et le ROI
        profit = total_revenue - total_cost
        roi = (profit / total_cost) * 100

        # Valeur Actuelle Nette (NPV) sur 3 ans
        npv = sum([
            (total_revenue * (1 + self.growth) ** t) / (1 + self.discount) ** t
            for t in range(1, 4)
        ])

        # Seuil de rentabilité (Combien de vannes à vendre ?)
        fixed = f["breakdown"]["Usinage"] + f["breakdown"]["Énergie"] + f["breakdown"]["Logistique"]
        breakeven = int(fixed / (price_u - cost_u)) + 1

        # =========================
        # 2. PRÉPARATION DES DONNÉES
        # =========================
        bp_data = {
            "price_u": price_u,
            "total_revenue": total_revenue,
            "profit": profit,
            "roi": round(roi, 2),
            "npv": round(npv, 2),
            "breakeven": breakeven
        }

        # =========================
        # 3. INTERVENTION DE L'IA (LLM) 🤖
        # =========================
        llm_output = self.generate_llm_analysis(bp_data)
        bp_data["llm_analysis"] = llm_output

        # =========================
        # 4. EXPORTATION DES DOCUMENTS
        # =========================
        self.export(bp_data, f)

        # On met le plan dans l'état global
        state["business_plan"] = bp_data

        print(f"Agent 7 TERMINE. ROI={roi:.2f}% | VAN={npv:,.0f} DZD")
        return state

    # -------------------------
    # GESTION DES FICHIERS (JSON, EXCEL, PDF)
    # -------------------------
    def export(self, bp, f):

        # JSON
        with open(os.path.join(OUTPUT_DIR, "business_plan.json"), "w", encoding="utf-8") as j:
            json.dump(bp, j, indent=4, ensure_ascii=False)

        # Excel
        df = pd.DataFrame({
            "Indicateur": ["Prix Vente", "Profit", "ROI", "VAN", "Seuil de Rentabilité"],
            "Valeur": [bp["price_u"], bp["profit"], f"{bp['roi']}%", bp["npv"], bp["breakeven"]]
        })
        df.to_excel(os.path.join(OUTPUT_DIR, "business_plan.xlsx"), index=False)

        # PDF (La belle mise en page)
        path = os.path.join(OUTPUT_DIR, "business_plan.pdf")
        doc = SimpleDocTemplate(path, pagesize=A4, leftMargin=50, rightMargin=50)

        # Styles du PDF
        styles = getSampleStyleSheet()
        body = ParagraphStyle("body", parent=styles["Normal"], alignment=TA_JUSTIFY, leading=14)
        title_style = ParagraphStyle("title", parent=styles["Title"], spaceAfter=15, textColor=colors.darkblue)
        header2 = ParagraphStyle("h2", parent=styles["Heading2"], spaceAfter=10, textColor=colors.steelblue)

        story = []

        # En-tête
        story.append(Paragraph("BUSINESS PLAN & STRATÉGIE", title_style))
        story.append(HRFlowable(width="100%", thickness=2, color=colors.darkblue))
        story.append(Spacer(1, 20))

        # Tableau des finances
        story.append(Paragraph("1. SYNTHÈSE FINANCIÈRE", header2))
        table_data = [
            ["Indicateur Clé", "Montant / Valeur"],
            ["Prix de Vente Conseillé", f"{bp['price_u']:,.0f} DZD"],
            ["Profit Estimé", f"{bp['profit']:,.0f} DZD"],
            ["Retour sur Investissement (ROI)", f"{bp['roi']} %"],
            ["Valeur Actuelle Nette (VAN sur 3 ans)", f"{bp['npv']:,.0f} DZD"],
            ["Seuil de Rentabilité (minimum)", f"{bp['breakeven']} unités"]
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

        # Texte rédigé par l'IA
        story.append(Paragraph("2. ANALYSE EXPERT PAR L'IA (LLM)", header2))
        
        # Astuce : On convertit les "entrer" du texte en sauts de ligne HTML pour le PDF
        texte_ia_html = bp["llm_analysis"].replace('\n', '<br/>')
        story.append(Paragraph(texte_ia_html, body))

        doc.build(story)


# -------------------------
# EXECUTION TEST 
# -------------------------
if __name__ == "__main__":
    # Ceci "simule" ce que l'agent 6 aurait calculé pour pouvoir tester l'Agent 7
    mock_state = {
        "financial_data": {
            "unit_cost": 20000,
            "total_production_cost": 4000000,
            "quantity": 200,
            "breakdown": {
                "Usinage": 3000000,
                "Énergie": 150000,
                "Logistique": 50000
            }
        }
    }

    agent = BusinessStrategistAgent()
    agent.generate_business_plan(mock_state)