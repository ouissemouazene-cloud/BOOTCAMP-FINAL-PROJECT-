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
import matplotlib.pyplot as plt
from langchain_google_genai import ChatGoogleGenerativeAI

from reportlab.lib.pagesizes import A4
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, HRFlowable, Image as RLImage
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
            proj_str = json.dumps(bp_data.get("projections", {}), indent=2)

            # LE SUPER PROMPT EXACT DEMANDÉ PAR L'UTILISATEUR
            prompt = f"""
            Tu es un expert en business plan industriel. Les 4 agents précédents t'envoient ces informations automatiques :
            - AGENT 4 (Sourcing) : {fournisseurs_str}
            - AGENT 5 (Choix/Négociation) : {selected_str}
            - AGENT 6 (Coûts/TCO) : {cost_str}
            - AGENT 7 (Projections financières) : {proj_str}
            
            Ta tâche :
            Rédige un Business Plan COMPLET qui suit STRICTEMENT ET EXACTEMENT la forme du modèle suivant. 
            Utilise les balises HTML <b>Titre</b> pour mettre en valeur les sections (car le rendu est pour ReportLab) et utilise des "<br/>" obligatoirement au lieu de simples sauts à la ligne.

            <b>BUSINESS PLAN — INDUSTRIE IA</b><br/><br/>
            <b>1. Page de garde</b><br/>
            PROJET : INDUSTRIE IA<br/>
            Production de équipements/vannes<br/>
            Quantité : [Quantité] unités<br/>
            Date : 2026<br/><br/>

            <b>2. Résumé exécutif</b><br/>
            [Rédiger le résumé en combinant l'approche multi-agents 4, 5, 6 et 7]<br/><br/>

            <b>3. Analyse des fournisseurs (Agent 4)</b><br/>
            [Liste détaillée formatée en lignes avec le nom, pays, prix et détail de tous les fournisseurs]<br/>
            👉 Plusieurs fournisseurs fiables ont été identifiés.<br/><br/>

            <b>4. Sélection du fournisseur (Agent 5)</b><br/>
            Le fournisseur retenu est :<br/>
            👉 <b>[Nom du fournisseur sélectionné]</b><br/>
            Justification :<br/>
            [Commentaire et liste des atouts tirés des négociations]<br/><br/>

            <b>5. Analyse des coûts (Agent 6)</b><br/>
            💰 Coût total de production : [Coût total] DZD<br/>
            💰 Coût unitaire : [Coût un] DZD<br/>
            📊 Détail des coûts : [Répartition matières, usinage, énergie...]<br/>
            👉 L’usinage représente la part dominante des coûts.<br/><br/>

            <b>6. Analyse financière (Agent 7)</b><br/>
            💵 Prix de vente estimé : [Prix] DZD / unité<br/>
            📈 Revenus : [Revenus] DZD<br/>
            💰 Profit : [Profit] DZD<br/>
            📊 ROI : ≈ [ROI] %<br/>
            👉 Le projet est rentable.<br/><br/>

            <b>7. Projection sur 3 ans 📊</b><br/>
            [Détail Année 1, Année 2, Année 3 des revenus et profits selon les données]<br/>
            👉 Hypothèse : croissance de 20% par an<br/>
            📈 Le profit augmente grâce à l’économie d’échelle.<br/><br/>

            <b>8. Analyse SWOT</b><br/>
            [Forces, Faiblesses, Opportunités, Menaces sous forme textuelle ou tirets]<br/><br/>

            <b>9. Analyse des risques</b><br/>
            [Liste de risques]<br/>
            👉 Risques modérés et contrôlables<br/><br/>

            <b>10. Recommandation finale</b><br/>
            👉 <b>Décision : GO</b><br/>
            Le projet est rentable, scalable et bien structuré.<br/>
            Il est recommandé de lancer la production.
            """
            import requests
            # 1. Tentative avec Ollama (votre LLM Local, comme dans Agent 5)
            try:
                print("[SUPER PROMPT LLM] Requete envoyee a l'IA locale (Ollama - mistral)...")
                payload = {"model": "mistral", "prompt": prompt, "stream": False}
                res = requests.post("http://localhost:11434/api/generate", json=payload, timeout=200)
                if res.status_code == 200:
                    print("[OLLAMA] Rapport rédigé avec succès par le LLM Mistral !")
                    return res.json().get("response", "").strip().replace("**", "").replace('\n', '<br/>')
            except Exception as e:
                print(f"[OLLAMA] Non disponible ou echec. Tentative avec Google Gemini...")

            # 2. Tentative avec Google Gemini
            print("[SUPER PROMPT LLM] Reflexion de l'IA Cloud (Gemini) en cours...")
            response = llm.invoke(prompt)
            return response.content.replace("**", "").replace('\n', '<br/>')

        except Exception as e:
            print(f"[LLM ERREUR] Aucune IA n'a repondu : {e}")
            print("[ATTENTION] Lancement du script dynamique Python de secours...")
            qty = cost_data.get('quantity', 200)
            best_name = selected_supplier.get('name', 'Fournisseur Sélectionné')
            
            fourn_lines = ""
            for s in suppliers[:5]:
                n = s.get('name', 'Inconnu')
                loc = s.get('country', s.get('location', 'Inconnu'))
                p = s.get('price_per_kg', s.get('price_unit', 0))
                c = s.get('currency', 'DZD')
                fourn_lines += f"{n} ({loc}) - {p} {c}/unité<br/>"
                
            c_prod = cost_data.get('total_production_cost', 0)
            c_unit = cost_data.get('unit_cost', 0)
            mat = cost_data.get('breakdown', {}).get('Matières', 0)
            usin = cost_data.get('breakdown', {}).get('Usinage', 0)
            ener = cost_data.get('breakdown', {}).get('Énergie', 0)
            logi = cost_data.get('breakdown', {}).get('Logistique', 0)
            
            p_val = bp_data.get('price_u', 0)
            rev = bp_data.get('total_revenue', 0)
            prof = bp_data.get('profit', 0)
            roi = bp_data.get('roi', 20)
            
            proj = bp_data.get('projections', {})
            y1_prof = proj.get('profits', [0,0,0])[0] if 'profits' in proj else prof
            y2_prof = proj.get('profits', [0,0,0])[1] if 'profits' in proj else prof*1.2
            y3_prof = proj.get('profits', [0,0,0])[2] if 'profits' in proj else prof*1.4
            
            y1_rev = proj.get('revenues', [0,0,0])[0] if 'revenues' in proj else rev
            y2_rev = proj.get('revenues', [0,0,0])[1] if 'revenues' in proj else rev*1.2
            y3_rev = proj.get('revenues', [0,0,0])[2] if 'revenues' in proj else rev*1.4
            
            y1_cst = proj.get('costs', [0,0,0])[0] if 'costs' in proj else c_prod
            y2_cst = proj.get('costs', [0,0,0])[1] if 'costs' in proj else c_prod*1.15
            y3_cst = proj.get('costs', [0,0,0])[2] if 'costs' in proj else c_prod*1.3
            
            return f"""<b>BUSINESS PLAN — INDUSTRIE IA</b><br/><br/>
<b>1. Page de garde</b><br/><br/>
PROJET : INDUSTRIE IA<br/>
Production de vannes industrielles<br/>
Quantité : {qty} unités<br/>
Date : 2026<br/><br/>
<b>2. Résumé exécutif</b><br/><br/>
Le projet INDUSTRIE IA vise la production de {qty} vannes industrielles en s’appuyant sur une approche automatisée basée sur des agents intelligents.<br/><br/>
L’analyse des coûts (Agent 6) estime le coût total de production à {c_prod:,.0f} DZD, avec un coût unitaire de {c_unit:,.0f} DZD.<br/><br/>
L’étude financière (Agent 7) montre une rentabilité du projet avec un ROI estimé à {roi:.0f} % et une croissance progressive sur 3 ans.<br/><br/>
👉 <b>Le projet est viable et recommandé (GO).</b><br/><br/>
<b>3. Analyse des fournisseurs (Agent 4)</b><br/>
{fourn_lines}<br/>
👉 Plusieurs fournisseurs fiables ont été identifiés.<br/><br/>
<b>4. Sélection du fournisseur (Agent 5)</b><br/><br/>
Le fournisseur retenu est :<br/><br/>
👉 <b>{best_name}</b><br/><br/>
Justification :<br/>
- Bon équilibre coût / qualité<br/>
- Délai de livraison acceptable<br/>
- Score global compétitif<br/><br/>
<b>5. Analyse des coûts (Agent 6)</b><br/>
💰 Coût total de production :<br/>
{c_prod:,.0f} DZD<br/><br/>
💰 Coût unitaire :<br/>
{c_unit:,.0f} DZD<br/><br/>
📊 Détail des coûts :<br/>
Matières : {mat:,.0f}<br/>
Usinage : {usin:,.0f}<br/>
Énergie : {ener:,.0f}<br/>
Logistique : {logi:,.0f}<br/><br/>
👉 L’usinage représente la part dominante des coûts.<br/><br/>
<b>6. Analyse financière</b><br/>
💵 Prix de vente estimé :<br/>
{p_val:,.0f} DZD / unité<br/><br/>
📈 Revenus :<br/>
{qty} x {p_val:,.0f} = {rev:,.0f} DZD<br/><br/>
💰 Profit :<br/>
{rev:,.0f} - {c_prod:,.0f} = {prof:,.0f} DZD<br/><br/>
📊 ROI :<br/>
≈ {roi:.0f} %<br/><br/>
👉 Le projet est rentable.<br/><br/>
<b>7. Projection sur 3 ans 📊</b><br/>
Année 1 | Revenus : {y1_rev:,.0f} | Coûts : {y1_cst:,.0f} | Profit : {y1_prof:,.0f}<br/>
Année 2 | Revenus : {y2_rev:,.0f} | Coûts : {y2_cst:,.0f} | Profit : {y2_prof:,.0f}<br/>
Année 3 | Revenus : {y3_rev:,.0f} | Coûts : {y3_cst:,.0f} | Profit : {y3_prof:,.0f}<br/><br/>
👉 Hypothèse : croissance de 20% par an<br/><br/>
📈 Le profit augmente grâce à l’économie d’échelle.<br/><br/>
<b>8. Analyse SWOT</b><br/>
Forces : Fournisseur fiable, Bonne maîtrise des coûts<br/>
Faiblesses : Coût élevé de l’usinage<br/>
Opportunités : Forte demande industrielle, Scalabilité du projet<br/>
Menaces : Fluctuation des prix, Risques logistiques<br/><br/>
<b>9. Analyse des risques</b><br/>
- Retard de livraison<br/>
- Augmentation des coûts matières<br/>
- Dépendance fournisseur<br/><br/>
👉 Risques modérés et contrôlables<br/><br/>
<b>10. Recommandation finale</b><br/><br/>
👉 <b>Décision : GO</b><br/><br/>
Le projet est rentable, scalable et bien structuré.<br/>
Il est recommandé de lancer la production."""

    # -------------------------
    # FONCTION PRINCIPALE (Calcule tout)
    # -------------------------
    def generate_business_plan(self, state):
        
        suppliers = state.get("suppliers_data", [])
        
        # Adaptation pour supporter les nouvelles sorties de l'Agent 5 (negotiated_prices) ou selected_supplier
        negotiated = state.get("negotiated_prices", {})
        if negotiated and "summary" in negotiated:
            # On prend le fournisseur le moins cher issu de la négociation
            best_supp_name = min(negotiated["summary"].keys(), key=lambda k: negotiated["summary"][k]["discounted_price"])
            best_supp_data = negotiated["summary"][best_supp_name]
            selected_supplier = {
                "name": best_supp_name,
                "price_per_kg": best_supp_data["discounted_price"],
                "currency": best_supp_data["currency"]
            }
            # On garde une trace des négociations pour l'IA
            state["selected_supplier"] = negotiated["summary"]
        else:
            selected_supplier = state.get("selected_supplier", {})
            
        f = state.get("financial_data", {})
        
        if not f or not selected_supplier:
            state["error"] = "Agent 7 a besoin des données de l'Agent 4, 5, et 6. Verifiez le State de l'orchestrateur."
            print(state["error"])
            # Return une donnée fictive pour ne pas bloquer les tests
            f = {
                "unit_cost": 19825.0, "total_production_cost": 3965000.0, "quantity": 200, 
                "breakdown": {"Usinage": 3000000, "Matières": 765000, "Énergie": 150000, "Logistique": 50000}
            }

        # =========================
        # 1. CALCULS FINANCIERS
        # =========================
        cost_u = f.get("unit_cost", 15000)
        
        # Marge
        price_u = round(cost_u * (1 + self.margin), 2)
        total_revenue = price_u * f.get("quantity", 200)
        total_cost = f.get("total_production_cost", 3000000)

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
        # 2. PROJECTIONS SUR 3 ANS
        # =========================
        revenues_y1 = total_revenue
        costs_y1 = total_cost
        profit_y1 = profit
        
        # Hypothèse de croissance de volumes de 20%, et économie d'échelle sur les coûts 15%
        revenues_y2 = revenues_y1 * 1.20
        costs_y2 = costs_y1 * 1.15
        profit_y2 = revenues_y2 - costs_y2
        
        revenues_y3 = revenues_y2 * 1.20
        costs_y3 = costs_y2 * 1.15
        profit_y3 = revenues_y3 - costs_y3
        
        bp_data["projections"] = {
            "years": ["Année 1", "Année 2", "Année 3"],
            "profits": [profit_y1, profit_y2, profit_y3]
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

        # Graphique Matplotlib des profits sur 3 ans
        plt.figure(figsize=(7, 4))
        plt.bar(bp["projections"]["years"], bp["projections"]["profits"], color=['#1f77b4', '#ff7f0e', '#2ca02c'])
        plt.title("Évolution du Profit sur 3 Ans", fontsize=12, fontweight='bold')
        plt.ylabel("Profit")
        plt.grid(axis='y', linestyle='--', alpha=0.7)
        plt.tight_layout()
        chart_path = os.path.join(OUTPUT_DIR, "profit_chart.png")
        plt.savefig(chart_path)
        plt.close()

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
        
        # Astuce technique: si l'IA sort des \n ou si reportlab rale, on nettoie
        html_safe_text = bp["llm_super_analysis"].replace('\n', '<br/>').replace('<br/><br/><br/>', '<br/><br/>')
        
        # ReportLab Paragraph parse les balises <b>, <i>, <br/>
        story.append(Paragraph(html_safe_text, body))

        # 3. Ajouter le graphique au PDF
        try:
            story.append(Spacer(1, 20))
            story.append(Paragraph("3. VISUALISATION DES PROFITS SUR 3 ANS", header2))
            story.append(Spacer(1, 10))
            story.append(RLImage(chart_path, width=400, height=230))
        except Exception as e:
            print(f"Erreur d'insertion du graphique : {e}")

        doc.build(story)


# -------------------------
# EXECUTION TEST UNITAIRE RAPIDE
# -------------------------
if __name__ == "__main__":
    import sys
    import json
    import os

    def load_json(filepath):
        if os.path.exists(filepath):
            with open(filepath, "r", encoding="utf-8") as f:
                return json.load(f)
        return {}
    
    # 1. On tente de lire les fichiers générés par les autres agents sur le disque
    sup_data = load_json("../AGENT4/suppliers_data.json") or load_json("suppliers_data.json")
    if not sup_data:
        sup_data = [{"name": "Pfeiffer", "price_unit": 800, "currency": "DZD"}, {"name": "Maschinenfabrik", "price_unit": 750, "currency": "DZD"}]
        
    neg_prices = load_json("../AGENT5/negotiated_prices.json") or load_json("negotiated_prices.json")
    if not neg_prices:
        neg_prices = {"summary": {"Maschinenfabrik": {"base_price": 750, "discounted_price": 700, "currency": "DZD"}}}
    elif "summary" not in neg_prices:
        neg_prices = {"summary": neg_prices}

    fin_data = load_json("../AGENT6/outputs/cost_analysis.json") or load_json("cost_analysis.json")
    if not fin_data:
        fin_data = {
            "unit_cost": 20000,
            "total_production_cost": 4000000,
            "quantity": 200,
            "breakdown": {"Usinage": 3000000, "Énergie": 150000, "Logistique": 50000}
        }

    # Assemblage de l'état "Local" dynamique
    mock_state = {
        "suppliers_data": sup_data,
        "negotiated_prices": neg_prices,
        "financial_data": fin_data
    }

    agent = BusinessStrategistAgent()
    agent.generate_business_plan(mock_state)