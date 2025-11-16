# Canine Colon Genome-Scale Metabolic Model (GEM)

## Overview

This project develops the first **digital twin of canine intestinal metabolism**, focusing on colonocyte butyrate metabolism to predict therapeutic and dietary interventions in canine dysbiosis.

Canine intestinal dysbiosis is highly prevalent and associated with chronic enteropathies, allergic dermatitis, and malabsorption. Current therapies and diets are chosen empirically with long evaluation times and significant costs. This model enables *in silico* simulation of nutritional and therapeutic scenarios before clinical application.

**Market potential**: Pet health and pet food markets projected to exceed $200B globally by 2030 (Grand View Research).

## Scientific Background

### Colonocyte Butyrate Metabolism

Colonocytes (colonic epithelial cells) derive ~70% of their energy from **butyrate**, a short-chain fatty acid (SCFA) produced by gut microbiota through fiber fermentation. Key metabolic features:

- **Butyrate oxidation** → ATP production (primary energy source)
- **Physiological hypoxia**: β-oxidation consumes O₂, maintaining low oxygen levels that favor beneficial anaerobic bacteria
- **Dysbiosis mechanism**: Impaired butyrate metabolism → increased O₂ availability → proliferation of pathogenic aerobic bacteria

### Model Scope

**Pilot focus**: Core butyrate oxidation pathway in canine colonocytes

**Key metabolic subsystems**:
1. SCFA transport (MCT1, SMCT1/2)
2. Butyrate activation (ACSM2A/2B, ACSS3)
3. β-oxidation (ACADS, ECHS1, HADHA/HADHB, ACAT1)
4. Electron transfer chain (ETFA/ETFB/ETFDH)
5. OXPHOS (Complexes I-V, ATP synthase)

## Technical Approach

### Workflow: Human-GEM → Canine-GEM

**1. Model source**: Human-GEM (Recon3D)
   - 12,971 reactions, 2,887 genes (SBML version loaded)
   - Fully annotated with KEGG, MetaCyc, BiGG IDs
   - SBML format, COBRApy compatible

**2. Caninization pipeline**:
   - Extract butyrate-related reactions from Human-GEM
   - Map human genes → dog orthologs (Ensembl BioMart)
   - Substitute Gene-Protein-Reaction (GPR) associations
   - Validate model integrity (no orphan reactions, intact GPR logic)
   - Apply canine physiological bounds

**3. Validation & testing**:
   - Flux Balance Analysis (FBA): verify butyrate → ATP flux
   - Parsimonious FBA (pFBA): identify minimal active reaction set
   - Flux Variability Analysis (FVA): assess pathway redundancy
   - Physiological constraint validation (hypoxia, SCFA uptake rates)

## Repository Structure

```
canine-colon-gem/
├── README.md                          # This file
├── requirements.txt                   # Python dependencies
├── .gitignore                        # Git ignore patterns
├── notebooks/
│   └── 01_caninization_workflow.ipynb  # Main analysis notebook (da aggiornare)
├── data/
│   ├── 01_physiological_bounds.xlsx   # Canine SCFA uptake rates, O₂ bounds (9 righe)
│   ├── 02_human_dog_orthologs.xlsx    # Human→Dog gene mappings (14 geni core)
│   ├── 03_kinetic_parameters.xlsx     # Km/Vmax ranges for core reactions (5 lumped)
│   └── daniela_detailed/              # ⭐ File dettagliati da Daniela (16/11/2025)
│       ├── FBA_bounds_colonocita_cane_pilota.xlsx  # 19 bounds (+ pathway specifiche)
│       └── Cinetiche_Butirrato.xlsx                # 9 reazioni MM (step-by-step β-ox)
├── docs/
│   ├── daniela_workflows/             # ⭐ Workflow documentation da Daniela
│   │   ├── README.md                  # Tutorial completo + confronto approcci
│   │   ├── flusso codici cobra.docx   # Script Python caninize_gpr.py
│   │   ├── Flusso operativo per ortologhi canini mod.docx  # BioMart tutorial
│   │   ├── primi step per caninizzare il modello umano (1).docx  # Workflow scientifico
│   │   └── pyton test via del butirrato.docx      # 7 test funzionali
│   └── CONCEPTS_EXPLAINED.md          # Spiegazione concetti tecnici (COBRApy, GEM, etc.)
└── scripts/                           # Utility scripts (future)
```

## Data Files

### 01_physiological_bounds.xlsx
Metabolite exchange bounds for "healthy dog" baseline:
- Butyrate uptake: -8 mmol/gDW/h (Minamoto 2019, Palmqvist 2023)
- Acetate uptake: -25 mmol/gDW/h
- Propionate uptake: -12 mmol/gDW/h
- O₂ uptake: -0.5 mmol/gDW/h (hypoxic colon, Grum 1984)
- ATP maintenance (ATPM): 8 mmol/gDW/h

### 02_human_dog_orthologs.xlsx
14 core genes mapped via Ensembl (Human GRCh38 → Dog CanFam3.1):
- Transporters: SLC16A1 (MCT1), SLC5A8/12 (SMCT1/2)
- Activation: ACSM2A/2B, ACSS3
- β-oxidation: ACADS, ECHS1, HADHA/HADHB, ACAT1
- ETF: ETFA, ETFB, ETFDH

Includes orthology type (1:1, 1:many) and % protein identity.

### 03_kinetic_parameters.xlsx
Km and Vmax ranges for 5 lumped reactions:
- BUT_uptake_MCT1
- BUT_activation
- BetaOx_C4 (lumped β-oxidation)
- PDH (pyruvate dehydrogenase)
- OXPHOS_ComplexV

## Installation

```bash
# Clone repository
git clone https://github.com/yourusername/canine-colon-gem.git
cd canine-colon-gem

# Create virtual environment
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

## Usage

### Jupyter Notebook (Local)
```bash
jupyter lab notebooks/01_caninization_workflow.ipynb
```

### Google Colab
1. Upload notebook to Colab
2. Mount Google Drive or upload data files
3. Run cells sequentially

## Technology Stack

- **Python 3.9+**
- **COBRApy**: constraint-based modeling
- **pandas**: data manipulation
- **openpyxl**: Excel file I/O
- **matplotlib/seaborn**: visualization
- **SBML**: model exchange format

## References

### Scientific Literature
- Minamoto Y et al. (2019). *Fecal SCFA in dogs with chronic enteropathy*
- Palmqvist H et al. (2023). *Butyrate metabolism in canine IBD*
- Grum DE et al. (1984). *Colonic oxygen consumption*
- Fernández-Pinteño M et al. (2023). *SCFA profiles in dysbiosis*

### Databases & Tools
- **Human-GEM**: https://github.com/SysBioChalmers/Human-GEM
- **Ensembl BioMart**: https://www.ensembl.org/biomart
- **COBRApy**: https://opencobra.github.io/cobrapy/

## Workflow Documentation

**⚠️ IMPORTANTE**: Il workflow corretto segue l'approccio **REAZIONI → GENI** (non geni → reazioni).

### Daniela's Detailed Workflows
Documentazione completa fornita dalla ricercatrice collaboratrice (16/11/2025):
- 📖 **Tutorial completo**: `docs/daniela_workflows/README.md`
- 📊 **Bounds dettagliati**: `data/daniela_detailed/FBA_bounds_colonocita_cane_pilota.xlsx` (19 reazioni)
- 🧬 **Parametri cinetici**: `data/daniela_detailed/Cinetiche_Butirrato.xlsx` (9 step pathway)
- 🔧 **Script Python**: GPR substitution, functional tests, BioMart mapping

**Workflow corretto**:
1. Estrarre **reazioni butirrato** da Human-GEM (keyword search)
2. Creare sotto-modello con quelle reazioni
3. Estrarre **ENSG IDs umani** dalle reazioni
4. BioMart: mapping ENSG → ENSCAFG (ortologhi canini)
5. Sostituire GPR con IDs canini
6. Validare con 7 test funzionali (FBA, FVA, gene deletion, sensitivity)

Vedi roadmap dettagliata: [GitHub Issue #1](https://github.com/MyFranzDev/canine-colon-gem/issues/1)

## Roadmap

### Phase 1: Pilot (Current)
- [x] Data collection and curation
- [x] Daniela's workflow documentation integration
- [ ] Butyrate reactions extraction (keyword search)
- [ ] Pathway completeness verification (4 phases + compartments)
- [ ] ENSG gene list extraction for BioMart
- [ ] BioMart ortholog mapping (ENSG → ENSCAFG)
- [ ] GPR substitution with canine IDs
- [ ] FBA validation with detailed bounds (19 reactions)
- [ ] 7 functional tests (feasibility, uptake, pathway, FVA, essentiality, sensitivity, energetic)

### Phase 2: Expansion
- [ ] Kinetic modeling (Michaelis-Menten parameters)
- [ ] Dynamic FBA (dFBA) implementation
- [ ] Full colonocyte metabolism (glycolysis, TCA, amino acids)
- [ ] Multi-compartment model (lumen, epithelium, blood)
- [ ] Microbiota integration (community FBA)

### Phase 3: Clinical Application
- [ ] Dysbiosis patient data integration
- [ ] Diet formulation optimization
- [ ] Probiotic/prebiotic effect prediction
- [ ] Veterinary decision support tool

## License

[To be determined]

## Contact

[Your contact information]

## Acknowledgments

This project builds upon:
- Human-GEM consortium (Chalmers University)
- Ensembl genome annotation
- COBRA Toolbox community
