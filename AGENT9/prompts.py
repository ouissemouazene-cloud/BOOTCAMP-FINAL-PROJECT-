# =============================================================================
# prompts.py
# Modèles de prompts pour l'Agent 9 (Catalogue Exporter)
# =============================================================================

# Constantes pour faciliter la modification des prompts par les experts métier

DETAILED_DESCRIPTION_PROMPT = """
Write a high-impact commercial summary for a product called {part_name} made of {material}.
The response MUST be a list of 4 detailed bullet points (using '-').
Focus on technical excellence, quality, and industrial durability.
Do not mention prices.
Clean text only.
"""

INDUSTRIAL_USE_CASE_PROMPT = """
Explain the industrial context and use cases for {part_name}.
The response MUST be a list of 3 specific examples of where this product is essential (e.g., Oil & Gas, Water Treatment, etc.).
Format as a list of bullet points starting with '-'.
Clean text only.
"""

STRATEGIC_VALUE_PROMPT = """
Generate a business value proposition for a procurement manager interested in {part_name}.
Explain why this is a secure investment.
The response MUST be a list of 3 strategic advantages (uptime, ROI through quality, risk reduction).
Format as a list of bullet points starting with '-'.
Clean text only.
"""
