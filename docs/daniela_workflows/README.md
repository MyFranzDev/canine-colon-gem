# Daniela's Workflow Documentation

Questa cartella contiene i file workflow forniti da Daniela (ricercatrice collaboratrice) il 16/11/2025.

## 📁 Struttura File

### File Excel (`/data/daniela_detailed/`)

| File | Righe | Descrizione | Utilizzo |
|------|-------|-------------|----------|
| `FBA_bounds_colonocita_cane_pilota.xlsx` | 19 | Bounds dettagliati per FBA con reazioni pathway-specific | Setup scenario FBA "cane sano" |
| `Cinetiche_Butirrato.xlsx` | 9 | Parametri cinetici Michaelis-Menten per ogni step pathway | Modellazione cinetica (fase 2) |

### File Word (questa cartella)

| File | Contenuto | Scopo |
|------|-----------|-------|
| `flusso codici cobra.docx` | Script Python `caninize_gpr.py` | Sostituzione GPR Human→Dog automatica |
| `Flusso operativo per ortologhi canini mod.docx` | Tutorial BioMart step-by-step | Mapping ortologhi + download sequenze |
| `primi step per caninizzare il modello umano (1).docx` | Workflow scientifico completo | Roadmap caninizzazione + validazione |
| `pyton test via del butirrato.docx` | Script test funzionali (7 test) | Validazione pathway butirrato |

---

## 📊 Dettaglio File Excel

### FBA_bounds_colonocita_cane_pilota.xlsx

**Novità rispetto a `01_physiological_bounds.xlsx`** (che ha solo 9 righe):

#### Exchange Reactions (lume ↔ sangue)
- `EX_but_lum`: -10 (starter, aumentare per high-fiber)
- `EX_ac_lum`: -5 (acetato)
- `EX_lac__L_lum`: -2 (lattato uptake/secrezione)
- `EX_nh4_lum`: -1 (ammonio, facoltativo)
- `EX_glc__D_lum`: **0** (glucosio chiuso → scenario butirrato-centrico)
- `EX_o2_bld`: -0.5 (ipossia)
- `EX_co2_bld`, `EX_h2o_bld`: -1000 (non limitanti)

#### Reazioni Pathway Butirrato (specifiche)
- `BUTtex`: Trasporto butirrato lume→epitelio (0, 1000)
- `BUTtmit`: Trasporto epitelio→mitocondrio (0, 1000)
- `BUTt`: Uptake MCT/SMCT (0, 1000) *per cinetica MM*
- `BUTACoA`: Attivazione BUT→Butirril-CoA (0, 1000)
- `BOXC4`: β-ossidazione C4→Acetil-CoA (0, 1000)
- `TCA`: Ciclo TCA aggregato (0, 1000)
- `ATPS4m`: ATP sintasi mitocondriale (0, 1000)
- `PDH`: Piruvato deidrogenasi (0, 1000, non essenziale)

**Uso consigliato**:
```python
bounds_df = pd.read_excel("data/daniela_detailed/FBA_bounds_colonocita_cane_pilota.xlsx")
for _, row in bounds_df.iterrows():
    if row['Reaction_ID'] in model.reactions:
        rxn = model.reactions.get_by_id(row['Reaction_ID'])
        rxn.lower_bound = row['LB']
        rxn.upper_bound = row['UB']
```

---

### Cinetiche_Butirrato.xlsx

**9 reazioni con parametri Michaelis-Menten dettagliati**:

| N° | Reazione | Km init (mM) | Vmax init | Tipo |
|----|----------|--------------|-----------|------|
| 1 | Trasporto MCT1 | 2.0 | 5 | H⁺/but symport (bassa affinità) |
| 2 | Trasporto SMCT1 | 0.3 | 3 | Na⁺-dipendente (alta affinità, dominante a basse [but]) |
| 3 | Attivazione (ACSM2A/ACSS3) | 0.1 | 2 | BUT→Butirril-CoA |
| 4 | **ACADS** (β-ox step 1) | **0.05** | **10** | **Step limitante** → FADH₂ |
| 5 | ECHS1 (β-ox step 2) | 0.05 | 10 | Equilibrio rapido |
| 6 | HADHA/B (β-ox step 3) | 0.05 | 10 | Complesso AND → NADH |
| 7 | ACAT1 (tiolasi) | 0.1 | 15 | Chiude β-ossidazione |
| 8 | ETF/ETFDH | 0.1 | 10 | FADH₂→Ubiquinone (ponte OXPHOS) |
| 9 | OXPHOS/ATP synthase | k=10 | - | Lineare (lumped Complessi I-V) |

**Range esplorazione**:
- Km: 0.02–5.0 mM
- Vmax: 1–30 mmol/gDW/h

**Uso**: Calibrazione cinetiche dopo validazione FBA. Integrare con moduli dinamici (dFBA).

---

## 📖 Contenuto File Word

### 1. flusso codici cobra.docx

**Script Python completo**: `caninize_gpr.py`

**Funzionalità**:
- Carica mapping Human→Dog da Excel
- Sostituisce ENSG IDs nelle GPR (con boundary regex)
- Gestisce casi speciali (one2many, orphans)
- Valida sintassi GPR (parentesi bilanciate)

**Uso**:
```bash
python caninize_gpr.py \
  --sbml_in Human-GEM.xml \
  --mapping ortologhi_ENSG_IDs.xlsx \
  --human-col "ID Ensembl umano" \
  --dog-col "ID Ensembl canino" \
  --sbml_out CanineColon_butyrate.xml
```

**Key function**:
```python
def map_rule(rule: str, mapping: Dict[str, str]) -> str:
    """Sostituisce ENSG human → ENSCAFG dog con word boundary"""
    sorted_keys = sorted(mapping.keys(), key=len, reverse=True)
    for k in sorted_keys:
        rule = re.sub(rf"(?<![A-Za-z0-9_.\-]){re.escape(k)}(?![A-Za-z0-9_.\-])",
                      mapping[k], rule)
    return rule
```

---

### 2. Flusso operativo per ortologhi canini mod.docx

**Tutorial BioMart**: come passare da geni umani a sequenze canine.

**Workflow**:
1. **Estrarre ENSG umani** da SBML:
   ```python
   model = cobra.io.read_sbml_model("Human-GEM.xml")
   genes = set()
   for rxn in model.reactions:
       for tok in re.findall(r"[A-Za-z0-9_.\-]+", rxn.gene_reaction_rule or ""):
           if tok.upper() not in {"AND","OR"}:
               genes.add(tok)  # Questi sono ENSG00000...
   ```

2. **BioMart - Mapping Human→Dog**:
   - Dataset: Homo sapiens (GRCh38)
   - Filters: Gene → "Input external references ID list" → incolla ENSG
   - Attributes:
     - GENE: Ensembl Gene ID, HGNC symbol
     - HOMOLOGS → Canis lupus familiaris:
       - Dog gene stable ID (ENSCAFG…)
       - Dog homology type (ortholog_one2one/one2many)
       - Dog % identity
   - Output: `Human_to_Dog_orthologs.tsv`

3. **BioMart - Sequenze canine**:
   - Dataset: Canis lupus familiaris
   - Filters: Gene → Limit to IDs → incolla ENSCAFG
   - Attributes → SEQUENCES (FASTA):
     - Gene sequence (genomica)
     - CDS (coding)
     - Peptide (aminoacidi)
   - Output: `dog_genes.fasta`, `dog_cds.fasta`, `dog_pep.fasta`

**Gestione casi speciali**:
- **one2many**: conserva tutti, marca tipo/identità, scegli con espressione/letteratura
- **Gene mancante**: lascia "NA", marca reazione orphan

---

### 3. primi step per caninizzare il modello umano (1).docx

**Documento scientifico completo** - workflow caninizzazione + validazione.

**Problema scientifico**:
- Disbiosi canina: patologie croniche intestinali, dermatiti, malassorbimento
- Terapie/diete scelte empiricamente (tempi lunghi, costi alti)
- Soluzione: gemello digitale metabolismo colon cane

**Approccio CORRETTO** (reazioni→geni):

#### Step 1: Estrarre reazioni butirrato
```python
but_rxns = [r for r in model.reactions
            if "but" in r.id.lower() or "butyr" in r.name.lower()]

submodel = model.copy()
submodel.reactions = but_rxns
submodel.genes = set(g for r in but_rxns for g in r.genes)
```

#### Step 2: Verificare pathway completo (4 fasi)
1. **Trasporto SCFA**: lume[lum] → citosol[c]
   - SLC16A1 (MCT1), SLC5A8/12 (SMCT1/2)
2. **Attivazione**: BUT → Butirril-CoA
   - ACSM2A/2B, ACSS3
3. **β-ossidazione C4**: Butirril-CoA → 2 Acetil-CoA
   - ACADS → ECHS1 → HADHA/HADHB → ACAT1
4. **OXPHOS**: NADH/FADH₂ → ATP
   - Complessi I-V + ATP synthase

**Verificare compartimenti**: [lum] ↔ [c] ↔ [m] ↔ [b]

#### Step 3: Estrarre ENSG umani
```python
human_genes = [g.id for g in submodel.genes]  # ENSG00000... (NON gene symbols!)
# Output: HumanGEM_gene_list_for_BioMart.xlsx
```

#### Step 4: BioMart → ortologhi canini (ENSCAFG)

#### Step 5: Test post-sostituzione
- **GPR integrity**: no parentesi spezzate, AND/OR corretti
- **Unmapped reactions**: `[r.id for r in model.reactions if not r.genes]`
- **Core genes check**: MCT1/SMCT/ACSM/ACADS/ECHS1/HADH/ACAT1/ETF canini presenti?

#### Step 6: Validazione funzionale FBA
Con bounds "cane sano":
- `EX_but_lum`: -8, altri SCFA limitati/spenti, `EX_o2_bld`: -0.5
- Objective: `ATPM`
- Check:
  - `status == optimal`
  - `ATPM > 0`
  - Flussi ACADS/ECHS1/HADH/ACAT1 > 0

**Analisi sensibilità**: variare `EX_but_lum` (-2, -4, -8, -12) → ATPM deve crescere/saturare

---

### 4. pyton test via del butirrato.docx

**Script test funzionali completo** - 7 test validazione pathway.

**Scenario**: "solo butirrato = -8" (acetato/propionato spenti, O₂ limitato)

#### Test 1 – FBA: fattibilità e ATP
```python
model.objective = "ATPM"
sol = model.optimize()
assert sol.status == "optimal"
assert sol.objective_value > 0
```

#### Test 2 – Uptake butirrato
```python
v_but = sol.fluxes["EX_but_lum"]
assert v_but ≈ -8  # usa tutto il bound permesso
```

#### Test 3 – Flussi pathway
```python
keys = ["BUTt_MCT1", "BUTact_ACSM", "BUTox1_ACADS", "BUTox2_ECHS1",
        "BUTox3_HADH", "BUTox4_ACAT1", "BUT_ETF"]
for k in keys:
    assert sol.fluxes[k] != 0  # pathway percorso
```

#### Test 4 – FVA (Flux Variability Analysis)
```python
max_ATP = sol.objective_value
model.reactions.ATPM.lower_bound = 0.9 * max_ATP
fva = flux_variability_analysis(model, reaction_list=keys, fraction_of_optimum=0.9)
# Se ACADS ha min≈max≠0 → vincolato (buono)
# Se ACADS ha min=0 → esistono bypass (da verificare)
```

#### Test 5 – Essenzialità genetica
```python
genes = ["ACADS_CANIS", "ACSM2A_CANIS", "ETFDH_CANIS", "SLC16A1_CANIS"]
del_res = single_gene_deletion(model, gene_list=genes)
# Knockout ACADS → ATPM crolla (coerente)
```

#### Test 6 – Sensibilità bounds
```python
for lb in [-2, -4, -8, -12]:
    model.reactions.EX_but_lum.lower_bound = lb
    sol = model.optimize()
    print(f"LB but = {lb} → ATPM = {sol.objective_value}")
# ATPM deve crescere/saturare all'aumentare |LB|
```

#### Test 7 – Controllo energetico
- Butirrato completo → 27-34 ATP/mol (ordine grandezza)
- Se `but = -8` e `ATPM = 3-5` → plausibile
- Se `ATPM = 0.1` → collo bottiglia sbagliato

---

## 🎯 Workflow Consigliato (da file Daniela)

### Fase 1: Preparazione
1. Caricare Human-GEM
2. **Estrarre reazioni** (non geni!) con keyword butirrato
3. Creare sotto-modello con quelle reazioni
4. **Estrarre geni ENSG** da quelle reazioni

### Fase 2: Mapping Ortologhi
1. Salvare lista ENSG in Excel
2. BioMart: ENSG umani → ENSCAFG canini
3. Download: mapping table + sequenze FASTA

### Fase 3: Caninizzazione
1. Usare script `caninize_gpr.py` per sostituire GPR
2. Verificare GPR syntax (parentesi, AND/OR)
3. Gestire unmapped (orphans)

### Fase 4: Validazione Funzionale
1. Applicare bounds "cane sano" (`FBA_bounds_colonocita_cane_pilota.xlsx`)
2. FBA con `ATPM` objective
3. Eseguire 7 test funzionali (script `pyton test via del butirrato.docx`)
4. Analisi sensibilità

### Fase 5: Cinetiche (opzionale, fase 2)
1. Usare parametri `Cinetiche_Butirrato.xlsx`
2. Implementare Michaelis-Menten per reazioni chiave
3. Calibrare Km/Vmax con FBA reference

---

## ⚠️ Differenze Chiave vs Approccio Precedente

| Aspetto | Approccio Precedente (ERRATO) | Approccio Daniela (CORRETTO) |
|---------|-------------------------------|------------------------------|
| **Punto partenza** | 14 geni core → cercare reazioni | Reazioni butirrato → estrarre geni |
| **Gene IDs** | Gene symbols (SLC16A1) | ENSG IDs (ENSG00000155380) |
| **Mapping ortologhi** | Simboli → simboli | ENSG → ENSCAFG |
| **Completezza pathway** | Keyword search (43 rxn) | Verifica 4 fasi + compartimenti |
| **Sostituzione GPR** | Fallita (0 sostituzioni) | Regex boundary-aware con ENSG |
| **Exchange reactions** | IDs inventati (EX_but_lum) | IDs reali da modello |
| **Validazione** | Solo FBA | 7 test funzionali completi |

---

## 📚 Riferimenti

**Database**:
- Ensembl BioMart: https://www.ensembl.org/biomart
- VGNC (Vertebrate Gene Nomenclature): per simboli canini
- UniProt: annotazioni funzionali

**Letteratura**:
- Minamoto Y et al. (2019). *Fecal SCFA in dogs with chronic enteropathy*
- Palmqvist H et al. (2023). *Butyrate metabolism in canine IBD*
- Grum DE et al. (1984). *Colonic oxygen consumption*

---

**Ultimo aggiornamento**: 2025-11-16
**Fonte**: Email Daniela 16/11/2025 (18:47, 19:49)
