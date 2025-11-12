# Canine Colon GEM - Concepts Explained

A comprehensive guide to understanding the notebook and metabolic modeling concepts.

---

## Table of Contents

1. [What is Metabolic Modeling?](#what-is-metabolic-modeling)
2. [COBRApy - The Tool](#cobrapy---the-tool)
3. [Human-GEM - The Model](#human-gem---the-model)
4. [Core Concepts](#core-concepts)
   - [Metabolites](#metabolites)
   - [Reactions](#reactions)
   - [Genes](#genes)
   - [GPR (Gene-Protein-Reaction)](#gpr-gene-protein-reaction)
5. [Block-by-Block Notebook Guide](#block-by-block-notebook-guide)
6. [FAQ](#faq)

---

## What is Metabolic Modeling?

### The Big Picture

Imagine the cell as a **chemical factory**:
- **INPUT**: nutrients (butyrate, oxygen, glucose, etc.)
- **PROCESS**: thousands of chemical reactions happening simultaneously
- **OUTPUT**: energy (ATP), building blocks for growth, waste products (CO₂, H₂O)

**Metabolic modeling** = creating a mathematical representation of this factory to:
- Predict what happens if we change the inputs
- Understand which pathways are active
- Simulate diseases or interventions

### Why Genome-Scale?

A **Genome-Scale Metabolic Model (GEM)** includes:
- ALL known metabolic reactions in an organism
- Based on its genome (DNA → genes → enzymes → reactions)
- Thousands of reactions connected in a network

**Our goal**: Create the first canine colonocyte GEM to predict how diet affects gut metabolism.

---

## COBRApy - The Tool

### What is COBRApy?

**COBRA** = **C**onstraint-**B**ased **R**econstruction and **A**nalysis

**COBRApy** = Python library for metabolic modeling

Think of it as:
- **Excel on steroids** for biochemical networks
- Loads models in SBML format (like XML for biology)
- Runs simulations (FBA, pFBA, FVA)
- Manipulates thousands of reactions easily

### What COBRApy Does

```python
import cobra

# Load a model (like opening an Excel file)
model = cobra.io.read_sbml_model("Human-GEM.xml")

# Inspect it
print(model.reactions)  # List all reactions
print(model.metabolites)  # List all compounds
print(model.genes)  # List all genes

# Run simulation
solution = model.optimize()  # Find optimal flux distribution
print(solution.objective_value)  # How much ATP produced?
```

### Key COBRApy Operations

| Operation | What it does |
|-----------|-------------|
| `read_sbml_model()` | Load a model from file |
| `model.reactions` | Access all reactions |
| `model.metabolites` | Access all metabolites |
| `model.genes` | Access all genes |
| `model.optimize()` | Run FBA simulation |
| `pfba()` | Run parsimonious FBA |
| `flux_variability_analysis()` | Find flux ranges |

---

## Human-GEM - The Model

### What is Human-GEM?

**Human-GEM** = The most comprehensive metabolic model of human cells

**Stats**:
- **12,971 reactions** (chemical transformations)
- **8,455 metabolites** (molecules like glucose, ATP, butyratel)
- **2,887 genes** (instructions for making enzymes)
- Represents **all known human metabolism**

### Why Use Human-GEM?

Because there's **no Canine-GEM yet**!

Our strategy:
1. Start with Human-GEM (well-curated)
2. Replace human genes with dog orthologs (similar genes)
3. Create Canine-GEM (our innovation!)

### Human-GEM Structure

```
Human-GEM.xml (41 MB file)
├── Reactions (12,971)
│   ├── Glycolysis (10 reactions)
│   ├── TCA cycle (8 reactions)
│   ├── Butyrate metabolism (15 reactions) ← WE FOCUS HERE
│   ├── Fatty acid oxidation (200 reactions)
│   └── ... (hundreds of pathways)
├── Metabolites (8,455)
│   ├── glucose, ATP, NADH, butyryl-CoA, ...
├── Genes (2,887)
│   └── ACADS, SLC16A1, HADHA, ...
└── Compartments
    ├── [c] cytosol
    ├── [m] mitochondrion
    ├── [lum] lumen (gut)
    └── [bld] blood
```

---

## Core Concepts

### Metabolites

**What**: Chemical compounds (molecules) in the cell

**Examples**:
- `but_lum` = butyrate in the lumen (gut)
- `but_c` = butyrate in cytosol (inside cell)
- `atp_m` = ATP in mitochondrion
- `o2_bld` = oxygen from blood

**Format**: `metabolite_compartment`
- Compartments: `[c]` cytosol, `[m]` mitochondrion, `[lum]` lumen, `[bld]` blood

**Why important**: Metabolites move between compartments and transform via reactions

---

### Reactions

**What**: Chemical transformations (A + B → C + D)

**Example - Butyrate activation**:
```
Reaction ID: ACSM2A_rxn
Name: Butyrate + CoA + ATP → Butyryl-CoA + AMP + PPi
Equation: but_c + coa_c + atp_c → butcoa_c + amp_c + ppi_c

Translation:
- Butyrate (food) gets "activated" by attaching CoA
- Costs 1 ATP (energy investment)
- Produces butyryl-CoA (ready for β-oxidation)
```

**Reaction Properties**:

| Property | Description | Example |
|----------|-------------|---------|
| `id` | Unique identifier | `ACSM2A_rxn` |
| `name` | Human-readable name | "Butyryl-CoA synthetase" |
| `reaction` | Chemical equation | `but + coa + atp → butcoa` |
| `lower_bound` | Min flux allowed | -1000 (reversible) or 0 (forward only) |
| `upper_bound` | Max flux allowed | 1000 |
| `genes` | Which genes encode enzyme | `ACSM2A or ACSM2B` |
| `subsystem` | Pathway category | "Fatty acid metabolism" |

**Flux**: How fast a reaction happens (mmol/gDW/h = millimoles per gram dry weight per hour)

---

### Genes

**What**: DNA instructions for making enzymes (proteins that catalyze reactions)

**Flow**: DNA (gene) → RNA → Protein (enzyme) → Catalyzes reaction

**Example - SLC16A1**:
```
Gene: SLC16A1 (human gene symbol)
Ensembl ID: ENSG00000155363
Protein: MCT1 (Monocarboxylate Transporter 1)
Function: Transports butyrate from gut lumen into cell
Reaction: EX_but_lum (butyrate uptake)

Dog ortholog: ENSCAFG00000002954 (we substitute this!)
```

**Why substitute genes?**
- Humans and dogs have ~95% similar metabolism
- But gene IDs differ (ENSG... vs ENSCAFG...)
- We map human → dog genes via Ensembl database
- Replace human IDs with dog IDs → Canine model!

---

### GPR (Gene-Protein-Reaction)

**What**: Logic rules connecting genes to reactions

**Why needed?**: Some reactions need:
- 1 gene (simple enzyme)
- Multiple genes together (protein complex) → **AND**
- Alternative genes (isozymes) → **OR**

**Examples**:

#### 1. Single gene (simple)
```
Reaction: MCT1_transport
GPR: SLC16A1
Meaning: Only SLC16A1 gene needed
```

#### 2. Protein complex (AND logic)
```
Reaction: MTP_complex
GPR: HADHA AND HADHB
Meaning: Both genes required (they form a complex)
If either is missing → reaction blocked
```

#### 3. Isozymes (OR logic)
```
Reaction: Butyrate_activation
GPR: ACSM2A OR ACSM2B
Meaning: Either gene sufficient (redundancy)
If at least one present → reaction works
```

#### 4. Complex GPR (nested logic)
```
Reaction: ETF_pathway
GPR: (ETFA AND ETFB AND ETFDH)
Meaning: All 3 genes form electron transfer flavoprotein
```

**Caninization = replacing gene IDs in GPRs**:
```
Human GPR:  SLC16A1 AND HADHA
            ↓ substitute ↓
Canine GPR: ENSCAFG00000002954 AND ENSCAFG00000012221
```

---

## Block-by-Block Notebook Guide

### Block 1: Setup & Imports

**What it does**: Loads Python libraries

```python
import cobra          # Metabolic modeling
import pandas as pd   # Data manipulation (Excel-like)
import numpy as np    # Math operations
import matplotlib.pyplot as plt  # Plotting
import seaborn as sns # Pretty plots
```

**Output**: Confirms all packages loaded successfully

**Why important**: Without these imports, nothing else works

---

### Block 2: Load Human-GEM Model

**What it does**: Reads the 41 MB XML file into memory

```python
model_human = cobra.io.read_sbml_model("../data/Human-GEM.xml")
```

**What happens**:
1. COBRApy parses XML file
2. Creates Python objects for reactions, metabolites, genes
3. Builds network connectivity
4. Takes ~30 seconds (it's big!)

**Output**:
```
✓ Model loaded: HumanGEM
  Reactions: 12971
  Metabolites: 8455
  Genes: 2887
```

**Interpretation**:
- 12,971 reactions = all human metabolic transformations
- 8,455 metabolites = all compounds tracked
- 2,887 genes = enzymes encoded in genome

**Why important**: This is our starting point. We'll extract butyrate subset.

---

### Block 3: Filter Butyrate Pathway Reactions ⭐

**THE MOST IMPORTANT BLOCK - Let's break it down step-by-step**

#### Goal
From 12,971 reactions, find only those related to **butyrate metabolism** (~50-100 reactions)

#### Step 3.1: Keyword Search

```python
keywords = ['but', 'butyr', 'butyrate', 'c4', 'scfa', 'mct1', 'smct', 'slc16a1', 'slc5a8']

but_reactions = []
for rxn in model_human.reactions:
    rxn_str = (rxn.id + " " + rxn.name).lower()
    if any(kw in rxn_str for kw in keywords):
        but_reactions.append(rxn)
```

**What this does**:
1. Define keywords related to butyrate (but, butyr, C4 = 4-carbon chain)
2. Loop through ALL 12,971 reactions
3. For each reaction, combine its ID + name into a string
4. Check if ANY keyword appears in that string
5. If yes → add to `but_reactions` list

**Example matches**:
- Reaction ID: `MCT1_transport` → matches "mct1"
- Reaction name: "Butyrate activation" → matches "butyrate"
- Reaction: `C4_beta_oxidation` → matches "c4"

**Output**: ~50 reactions containing keywords

#### Step 3.2: Extract Core Genes

```python
core_genes = [
    'SLC16A1',  # MCT1 transporter
    'SLC5A8', 'SLC5A12',  # SMCT transporters
    'ACSM2A', 'ACSM2B', 'ACSS3',  # Activation enzymes
    'ACADS',  # β-oxidation step 1
    'ECHS1', 'HADHA', 'HADHB', 'ACAT1',  # β-oxidation steps 2-4
    'ETFA', 'ETFB', 'ETFDH'  # Electron transfer
]

core_reactions = set()
for gene_id in core_genes:
    gene = model_human.genes.get_by_id(gene_id)
    core_reactions.update(gene.reactions)  # Add all reactions this gene is in
```

**What this does**:
1. Define 14 CORE genes (from ortholog mapping file)
2. For each gene, find ALL reactions it participates in
3. Add those reactions to `core_reactions` set

**Why?** Keyword search might miss some reactions. By including all reactions linked to core genes, we ensure completeness.

**Example**:
```
Gene: ACADS (acyl-CoA dehydrogenase)
Reactions it's in:
  - ACADS_C4 (butyrate dehydrogenation)
  - ACADS_C6 (hexanoate dehydrogenation)
  - ACADS_C8 (octanoate dehydrogenation)
→ All 3 added to core_reactions
```

#### Step 3.3: Add Essential Subsystems

```python
essential_keywords = ['oxphos', 'respiratory', 'atp synthase', 'atpm', 'complex']

for rxn in model_human.reactions:
    rxn_str = (rxn.id + " " + rxn.name + " " + (rxn.subsystem or "")).lower()
    if any(kw in rxn_str for kw in essential_keywords):
        core_reactions.add(rxn)
```

**What this does**:
Include OXPHOS (oxidative phosphorylation) reactions:
- Complex I, II, III, IV (electron transport chain)
- Complex V (ATP synthase)
- ATPM (ATP maintenance reaction)

**Why important**: Butyrate produces FADH₂ and NADH → feed into OXPHOS → make ATP. Without OXPHOS, we can't measure energy production!

**Analogy**: Butyrate is coal, OXPHOS is the power plant. We need both to measure electricity output (ATP).

#### Step 3.4: Add Exchange Reactions

```python
for rxn in model_human.exchanges:
    if any(met in rxn.id.lower() for met in ['but', 'o2', 'co2', 'h2o', 'h_', 'pi']):
        core_reactions.add(rxn)
```

**What are exchange reactions?**
- Special reactions that move metabolites in/out of the system
- Format: `EX_metabolite_compartment`

**Examples**:
- `EX_but_lum` = butyrate uptake from lumen (gut)
- `EX_o2_bld` = oxygen uptake from blood
- `EX_co2_bld` = CO₂ release to blood
- `EX_h2o_bld` = water exchange
- `EX_pi_bld` = phosphate exchange

**Why needed**: These are the boundaries. Inputs (butyrate, O₂) and outputs (CO₂, H₂O).

#### Final Output of Block 3

```
✓ Found 50 butyrate-related reactions (keyword search)
✓ 14 genes associated with butyrate reactions
✓ After adding OXPHOS + exchanges: 150 reactions
```

**What we have now**:
- `but_reactions`: Reactions with butyrate keywords
- `but_genes`: Genes involved
- `core_reactions`: Complete set including:
  - Butyrate pathway
  - OXPHOS (energy production)
  - Exchange reactions (boundaries)

**Next step** (Block 4): Load human→dog gene mappings to replace these genes.

---

### Block 4: Load Ortholog Mappings

**What it does**: Reads Excel file with human→dog gene mappings

```python
df_orthologs = pd.read_excel("../data/02_human_dog_orthologs.xlsx")
ortholog_map = dict(zip(
    df_orthologs['Gene umano'],      # Human gene: SLC16A1
    df_orthologs['Ortologo canino']  # Dog gene: ENSCAFG00000002954
))
```

**Creates dictionary**:
```python
{
    'SLC16A1': 'ENSCAFG00000002954',
    'SLC5A8': 'ENSCAFG00000006942',
    'ACADS': 'ENSCAFG00000007629',
    # ... 14 mappings total
}
```

**Output**: Confirms 14 gene mappings loaded

---

### Block 5: Substitute GPRs (Caninization!)

**What it does**: Replace human gene IDs with dog IDs in ALL GPR rules

**Before**:
```
Reaction: ACADS_C4
GPR: SLC16A1 AND HADHA
```

**After**:
```
Reaction: ACADS_C4
GPR: ENSCAFG00000002954 AND ENSCAFG00000012221
```

**Code logic**:
1. Loop through ALL reactions
2. Read GPR string
3. Find human gene IDs
4. Replace with dog IDs using `ortholog_map`
5. Update GPR

**Output**:
```
✓ Substituted 150 gene occurrences
  Genes without mapping: 500 (genes outside butyrate pathway)
✓ Canine model created: CanineColon_Butyrate
```

**What we have now**: A model with dog genes! 🐕

---

### Block 6: Validate Model Integrity

**What it does**: Check nothing broke during substitution

**Checks**:
1. **Orphan reactions**: Reactions with no genes (might be broken)
2. **GPR syntax**: Parentheses balanced? `(HADHA AND HADHB)` ✓ vs `(HADHA AND HADHB` ✗
3. **Core gene presence**: All 14 dog genes present?

**Output**: List of warnings or "✓ All checks passed"

---

### Block 7: Apply Bounds & Run FBA

**What it does**: Set realistic constraints and simulate metabolism

#### Apply Bounds

```python
EX_but_lum: [-8, 1000]    # Uptake 8 mmol/h (physiological)
EX_o2_bld:  [-0.5, 1000]  # Low oxygen (hypoxia)
ATPM:       [8, 1000]     # Minimum ATP needed
```

**Lower bound < 0** = uptake (metabolite coming IN)
**Upper bound > 0** = secretion (metabolite going OUT)

#### Run FBA (Flux Balance Analysis)

**What is FBA?**
- Mathematical optimization: Maximize ATP production
- Subject to constraints: stoichiometry + bounds
- Finds flux distribution (how fast each reaction runs)

**Analogy**: Like finding the best route for water through pipes to maximize flow at the end.

**Output**:
```
Status: optimal
Objective value (ATPM): 8.5 mmol/gDW/h
Key fluxes:
  EX_but_lum    -8.0  (uptake)
  EX_o2_bld     -0.5  (consumption)
  ATPM           8.5  (ATP produced)
```

**Interpretation**:
- Model works! ✓
- Butyrate → ATP pathway is functional
- Produces 8.5 mmol ATP per hour

---

### Block 8: Visualize & Export

**What it does**:
1. Plot key fluxes (bar chart)
2. Export canine model to `CanineColon_Butyrate.xml`
3. Save flux results to CSV

**Output**: Canine model ready for further analysis!

---

## FAQ

### Q1: Why do we need 12,971 reactions if we only use ~150?

**A**: We extract a subset, but keep connectivity to OXPHOS and core metabolism. This ensures realistic flux distributions.

### Q2: What does "flux" mean?

**A**: Reaction rate (how fast it happens). Units: mmol/gDW/h (millimoles per gram dry weight per hour).

### Q3: Why human→dog and not build from scratch?

**A**: Building a GEM from scratch takes years. Human-GEM is well-curated (10+ years of work). Dogs are 95% similar metabolically, so substitution is faster and reliable.

### Q4: What if a dog gene is missing?

**A**: We either:
1. Keep human gene (assume similar)
2. Mark reaction as "orphan" (no gene assigned)
3. Remove reaction if critical

For our 14 core genes, all have dog orthologs!

### Q5: What is SBML?

**A**: Systems Biology Markup Language. XML format for storing models. Like a universal Excel file for biology.

### Q6: Can I change parameters?

**A**: Yes! In Block 7, you can change bounds:
```python
EX_but_lum: [-10, 1000]  # More butyrate
EX_o2_bld:  [-2, 1000]   # More oxygen (less hypoxia)
```

Then re-run FBA to see how ATP changes.

### Q7: What's the difference between FBA and pFBA?

**A**:
- **FBA**: Maximizes objective (ATP), flux can be anywhere in feasible range
- **pFBA**: Maximizes objective + minimizes total flux (more realistic, prefers simpler pathways)

### Q8: How do I interpret flux results?

**A**:
- **Positive flux**: Reaction runs forward
- **Negative flux**: Reaction runs backward (if reversible)
- **Zero flux**: Reaction inactive
- **Magnitude**: How important (higher = more active)

---

## Summary Diagram

```
┌─────────────────────────────────────────────────────────┐
│                    WORKFLOW SUMMARY                      │
└─────────────────────────────────────────────────────────┘

1. LOAD HUMAN-GEM (12,971 reactions)
              ↓
2. FILTER BUTYRATE PATHWAY (~150 reactions)
   - Keyword search
   - Core genes (14)
   - OXPHOS reactions
   - Exchange reactions
              ↓
3. LOAD ORTHOLOG MAPPINGS (14 human→dog genes)
              ↓
4. SUBSTITUTE GPRs (replace human IDs with dog IDs)
              ↓
5. VALIDATE MODEL (check integrity)
              ↓
6. APPLY PHYSIOLOGICAL BOUNDS
   - Butyrate: -8 mmol/h
   - O₂: -0.5 mmol/h (hypoxia)
   - ATP: min 8 mmol/h
              ↓
7. RUN FBA (optimize ATP production)
              ↓
8. VISUALIZE & EXPORT
   → CanineColon_Butyrate.xml (Canine model!)
   → canine_flux_results.csv
```

---

## Key Takeaways

1. **Metabolic model** = mathematical network of reactions, metabolites, genes
2. **COBRApy** = Python library to manipulate models
3. **Human-GEM** = comprehensive human metabolic model (starting point)
4. **Caninization** = replace human genes with dog orthologs
5. **FBA** = simulation technique to predict metabolic fluxes
6. **Butyrate pathway** = colonocyte's main energy source (SCFA → ATP)

---

**Next**: Run the notebook cells sequentially and watch the caninization happen! 🐕🧬

If you have more questions on specific concepts, ask and I'll add to this doc!
