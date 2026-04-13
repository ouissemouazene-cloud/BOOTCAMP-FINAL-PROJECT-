# Agent 9 — Commercial Catalogue Generation Engine (INDUSTRIE IA)

Agent 9 is the final stage of the **INDUSTRIE IA** pipeline. Its role is to transform complex, multi-agent industrial data (technical specs, CAD files, negotiation results, TCO, etc.) into a professional, client-ready commercial catalogue.

## 🚀 Overview

The system acts as a "Commercial Reasoning Engine." It doesn't just export data; it interprets the output of Agents 1-8 to build a value-driven proposal for non-technical stakeholders.

### Key Capabilities:
- **Multiformat Delivery**: Generates HTML, PDF (optional), JSON, Excel, and XML.
- **LLM-Powered Copywriting**: Uses Mistral (via Ollama) to generate high-impact commercial highlights and use-case scenarios.
- **Strict Data Pruning**: Automatically simplifies technical jargon and hides internal complexity (e.g., specific supplier IDs, historical negotiation steps) to provide a "Client-Facing" view.
- **Data Validation**: Enforces strict schema integrity using Pydantic models.
- **Archive Management**: Packages all deliverables with an automated manifest and SHA-256 checksums into a single ZIP.

---

## 🏗️ Architecture

Agent 9 follows a robust 4-step generation workflow:

1. **Validation**: Validates the incoming `PipelineData` object using Pydantic to ensure all upstream agents (1-8) provided consistent data.
2. **Commercial Reasoning**: Calls an LLM to transform technical materials and specs into structured commercial bullet points (Summary, Context, Value Proposition).
3. **Generation**: Executes specialized generators for each format:
    - `html_gen.py`: Professional rich UI using Jinja2 templates.
    - `json_gen.py`: Produces both hierarchical and "BI-ready" flat JSON.
    - `excel_gen.py`: Creates a 6-sheet technical and financial report.
    - `xml_gen.py`: Standardized XML for ERP integration.
    - `pdf_gen.py`: High-quality PDF export (via WeasyPrint).
4. **Finalization**: Computes manifests, verifies file sizes/hashes, and compresses the results.

---

## 📂 Project Structure

```text
AGENT9/
├── agent9.PY            # Main orchestrator & LangGraph Node
├── prompts.py           # Externalized LLM prompt templates
├── models.py            # Pydantic data schemas (Agent 1-8)
├── fake_data.py         # Mock data for standalone testing
├── requirements.txt     # Python dependencies
├── generators/          # Format-specific logic
│   ├── html_gen.py
│   ├── json_gen.py
│   ├── excel_gen.py
│   ├── xml_gen.py
│   └── pdf_gen.py
├── templates/           # Jinja2 templates
│   ├── catalogue.html.j2
│   └── catalogue.xml.j2
└── output_catalogue/    # Default output directory
```

---

## 🔧 Installation & Setup

### Prerequisites:
- **Python 3.10+**
- **Ollama**: Running locally with the `mistral` model installed.
- **GTK3 (Optional)**: Required if you wish to generate PDFs via WeasyPrint.

### Steps:
1. **Clone the repository** and navigate to the `AGENT9` folder.
2. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```
3. **Ensure Ollama is running**:
   ```bash
   ollama pull mistral
   ```

---

## 🛠️ Usage

### Standalone Mode (Testing)
You can run Agent 9 independently using mock data to verify the generation process:
```bash
python agent9.PY
```
The results will be available in the `./output_catalogue/` directory.

### LangGraph Integration
Agent 9 is designed to fit perfectly into a LangGraph pipeline. Import the `agent9_node` to add it to your state graph:
```python
from agent9 import agent9_node

# In your graph definition:
workflow.add_node("agent9", agent9_node)
workflow.add_edge("agent8", "agent9")
```

---

## 📊 Data Schema (Expected Input)

Agent 9 expects a `PipelineData` object containing:
- **Agent 1**: Material, Diameter, Pressure, Flow Rate, Lifespan.
- **Agent 2**: CAD file paths and scale data.
- **Agent 3**: Video presentation assets.
- **Agent 4 & 5**: Procurement metadata (Supplier selected, lead times).
- **Agent 6**: TCO analysis (Total unit cost, inflation index).
- **Agent 7**: Business Plan (SWOT, NPV, ROI).
- **Agent 8**: Digital Twin status (Maintenance schedule, health scores).

---

## 📝 Commercial Rules (Client-Facing Mode)
The system enforces strict commercial rules to protect industrial secrets:
1. **No Specific Suppliers**: Only "Certified Network" mentions are exported to the client.
2. **No Negotiation History**: Displays only the final agreed terms.
3. **Time Ranges**: Maintenance dates from Agent 8 are converted into safe operational ranges.
4. **Unified Output**: All output files are named `catalogue_professional.*` for consistent branding.

---

*© 2026 INDUSTRIE IA — Smart Engineering Systems*
