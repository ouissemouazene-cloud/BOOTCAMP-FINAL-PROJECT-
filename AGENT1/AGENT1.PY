import os             # TO VERIFY THE PATH OF THE FILE TO KNOW IF IT EXIST  Gestion des fichiers et dossiers
import json           #  THE FILE THAT GONNA CONTAIN THE SPECS Formatage et sauvegarde des données techniques
import pdfplumber     # Extraction du texte et des tableaux techniques du PDF
from typing import Dict, Any, List #  THE STRUCTER OF DATA IN THE JSON FILE Définition des structures de données (Types)
from langchain_google_genai import ChatGoogleGenerativeAI # Connexion au cerveau IA (Gemini)

# --- Étape 1 : Chargement du fichier PDF ---

def charger_le_pdf(nom_du_fichier: str):
    """
    Vérifie l'existence du fichier et prépare son accès.
    """
    print(f"🔄 Tentative de chargement du fichier : {nom_du_fichier}")

    if os.path.exists(nom_du_fichier):
        print(f"✅ Succès : Le fichier '{nom_du_fichier}' a été trouvé.")
        return nom_du_fichier
    else:
        print(f"❌ Erreur : Le fichier '{nom_du_fichier}' est introuvable.")
        return None

# --- Étape 2 : Extraction du texte (Page par Page) ---

def extraire_texte_pdf(nom_du_fichier: str):
    texte_complet = ""
    
    # On ouvre le fichier avec pdfplumber
    with pdfplumber.open(nom_du_fichier) as pdf:
        # On parcourt chaque page une à une
        for page in pdf.pages:
            # On récupère le texte de la page
            contenu = page.extract_text()
            if contenu:
                # On l'ajoute au texte total avec un saut de ligne
                texte_complet += contenu + "\n"
                
    return texte_complet

# --- Étape 3 : Analyse avec l'IA (Le cerveau du système) ---
# - WE DEFINE A FUNCTION DEF THAT TAKES TESTECOMPLET AS A AN INPUT AND STOCK IT IN STR
# WE INITIALIZE THE LLM 
# WE CREAT THE PROMPT
# WE COMBINE BOTH THE PROMPT WITH THE TEXT STR IN ONE FINAL PROMPT
# WE GIVE IT TO THE LLM AND IT GIVES AS THE RESULT 

def analyser_avec_ia(texte_extrait: str):
    """
    Envoie le texte brute du PDF à l'IA pour extraire les données métiers.
    """
    # On initialise le "cerveau" (le modèle Gemini 1.5 Flash)
    llm = ChatGoogleGenerativeAI(model="gemini-1.5-flash")
    
    # On définit l'ordre précis pour l'ingénieur IA
    instruction = (
        "À partir du texte suivant extrait d'un plan industriel, extrait les 4 points clés "
        "en format JSON (Dimensions, Matériaux, Tolérances, Pression Nominale)."
    )
    
    # On combine l'ordre et le texte du plan
    prompt_final = f"{instruction}\n\nTexte du plan :\n{texte_extrait}"
    
    print("🚀 Analyse en cours par l'IA...")
    
    # On demande à l'IA de nous répondre
    resultat = llm.invoke(prompt_final)
    
    return resultat.content

# --- Étape 4 : Création du fichier JSON final ---

def sauvegarder_specs_json(donnees_ia: str, nom_fichier="technical_specs.json"):
    """
    Transforme la réponse texte de l'IA en fichier JSON réel.
    """
    print(f"💾 Génération du fichier {nom_fichier}...")
    
    try:
        # On convertit le texte de l'IA en objet Python
        objet_json = json.loads(donnees_ia)
        
        # On écrit physiquement le fichier sur l'ordinateur
        with open(nom_fichier, 'w', encoding='utf-8') as f:
            json.dump(objet_json, f, indent=4, ensure_ascii=False)
            
        print("✅ Terminé ! L'Agent 1 a fini sa mission.")
    except Exception as e:
        print(f"❌ Erreur lors de la création du JSON : {e}")

# --- LANCEMENT GLOBAL DE L'AGENT 1 ---

if __name__ == "__main__":
    # 1. On charge le fichier
    fichier = charger_le_pdf("plan_vanne.pdf")
    
    if fichier:
        # 2. On extrait le texte brute
        texte_brute = extraire_texte_pdf(fichier)
        
        # 3. L'IA analyse et extrait les 4 points clés
        resultat_brut_ia = analyser_avec_ia(texte_brute)
        
        # 4. On génère le fichier JSON final
        sauvegarder_specs_json(resultat_brut_ia)
