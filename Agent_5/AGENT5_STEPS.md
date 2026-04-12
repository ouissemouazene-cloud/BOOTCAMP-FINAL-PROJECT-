# Agent 5 : Négociateur IA (Procurement)

## Rôle
Simule le processus de négociation pour obtenir les meilleures conditions tarifaires pour le lot de 200 vannes.

## Étapes de Travail (Workflow)

1. **Définition de la Stratégie (Négociation)** :
    - Établissement de la marge de négociation par rapport aux prix du marché d'Agent 4 (ex : -15% pour volume).
    - Préparation des arguments (200 pièces d'un coup, partenariat long terme).

2. **Simulation d'Échanges (Multi-Agents Simulation)** :
    - Simulation d'un dialogue Agent-Fournisseur (en format texte et/ou audio).
    - Gestion des refus ou des contre-offres.

3. **Génération de Scripts de Negoc (Export Audio)** :
    - Transcription de la négociation idéale.
    - Utilisation d'une API TTS (Text-to-Speech) pour un rendu audio réaliste.

4. **Validation de l'Offre Finale** :
    - Confirmation du prix négocié pour les 200 unités.

## Sorties (Outputs)
- **Fichier Texte (Transcription)** : `negotiation_transcript.txt`.
- **Fichier Audio** : `negotiation_summary.mp3`.
- **État LangGraph** : Mise à jour de `state['negotiated_prices']` pour l'Agent 6.

## Outils Open Source Potentiels
- `ElevenLabs` ou `gTTS` (Google TTS) pour l'audio.
- `LangChain Memory` pour maintenir le contexte du dialogue.
- `OpenAI/Gemini` pour la simulation de personnalités (Acheteur vs Vendeur).
