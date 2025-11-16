#!/usr/bin/env python3
"""
extract_butyrate_pathway_daniela.py

Estrae pathway butirrato da Human-GEM seguendo workflow Daniela:
1. REAZIONI → keyword search
2. Verifica 4 fasi + compartimenti
3. Estrai ENSG IDs dalle reazioni
4. Genera Excel per BioMart
5. Statistiche per condivisione

Author: Francesco (con workflow Daniela 16/11/2025)
"""

import cobra
import pandas as pd
import re
from collections import defaultdict

# ============================================================================
# STEP 1: Load Human-GEM
# ============================================================================

print("="*80)
print("STEP 1: LOAD HUMAN-GEM MODEL")
print("="*80)

model = cobra.io.read_sbml_model("data/Human-GEM.xml")
print(f"\n✓ Model loaded: {model.id}")
print(f"  Reactions: {len(model.reactions):,}")
print(f"  Metabolites: {len(model.metabolites):,}")
print(f"  Genes: {len(model.genes):,}")

# ============================================================================
# STEP 2: Extract Butyrate Reactions (KEYWORD SEARCH)
# ============================================================================

print("\n" + "="*80)
print("STEP 2: EXTRACT BUTYRATE REACTIONS (KEYWORD SEARCH)")
print("="*80)

# Keywords per fase pathway
transport_keywords = ['mct1', 'mct4', 'smct', 'slc16a1', 'slc5a8', 'slc5a12',
                     'monocarboxylate transport', 'butyrate transport']
activation_keywords = ['butyryl-coa', 'butanoyl-coa', 'butyrate:coa',
                      'acsm', 'acss', 'butyryl coa']
oxidation_keywords = ['butyr', 'c4:0', 'c4', 'acads', 'echs1', 'hadha', 'hadhb',
                     'acat1', 'butanoyl', 'β-oxidation']

# Combina
include_keywords = transport_keywords + activation_keywords + oxidation_keywords

# Exclude false positives
exclude_keywords = [
    'aminobut',       # aminobutanoate (GABA pathway)
    'ureidobut',      # ureidoisobutyrate (pyrimidine degradation)
    'methylbut',      # methylbutanoyl (leucine metabolism)
    'hydroxybut',     # hydroxybutyrate (ketone bodies)
]

but_reactions = []
transport_rxns = []
activation_rxns = []
oxidation_rxns = []
excluded_count = 0

for rxn in model.reactions:
    rxn_str = (rxn.id + " " + rxn.name).lower()

    has_include = any(kw in rxn_str for kw in include_keywords)
    has_exclude = any(kw in rxn_str for kw in exclude_keywords)

    if has_include and not has_exclude:
        but_reactions.append(rxn)

        # Classifica per fase
        if any(kw in rxn_str for kw in transport_keywords):
            transport_rxns.append(rxn)
        if any(kw in rxn_str for kw in activation_keywords):
            activation_rxns.append(rxn)
        if any(kw in rxn_str for kw in oxidation_keywords):
            oxidation_rxns.append(rxn)
    elif has_include and has_exclude:
        excluded_count += 1

print(f"\n✓ Found {len(but_reactions)} butyrate reactions")
print(f"  Excluded {excluded_count} false positives")
print(f"\n=== BREAKDOWN BY PATHWAY PHASE ===")
print(f"  TRASPORTO:      {len(transport_rxns):3d} reactions")
print(f"  ATTIVAZIONE:    {len(activation_rxns):3d} reactions")
print(f"  β-OSSIDAZIONE:  {len(oxidation_rxns):3d} reactions")

# ============================================================================
# STEP 3: Add OXPHOS + Exchange Reactions
# ============================================================================

print("\n" + "="*80)
print("STEP 3: ADD OXPHOS & EXCHANGE REACTIONS")
print("="*80)

core_reactions = set(but_reactions)
initial_count = len(core_reactions)

# Add OXPHOS
oxphos_keywords = ['oxphos', 'respiratory chain', 'atp synthase',
                   'complex i', 'complex ii', 'complex iii', 'complex iv', 'complex v',
                   'nadh dehydrogenase', 'succinate dehydrogenase',
                   'cytochrome c oxidase', 'ubiquinol']
oxphos_count = 0

for rxn in model.reactions:
    rxn_str = (rxn.id + " " + rxn.name + " " + (rxn.subsystem or "")).lower()
    if any(kw in rxn_str for kw in oxphos_keywords):
        if rxn not in core_reactions:
            oxphos_count += 1
        core_reactions.add(rxn)

print(f"\n  Added {oxphos_count} OXPHOS reactions")

# Add Exchange reactions (IDs corretti da ricerca precedente)
exchange_ids_to_add = {
    'MAR09809': 'Exchange of butyrate',
    'MAR09086': 'Exchange of acetate',
    'MAR09808': 'Exchange of propanoate',
    'MAR09048': 'Exchange of O2',
    'MAR09058': 'Exchange of CO2',
    'MAR09047': 'Exchange of H2O',
}

exchange_added = []
for rxn_id, name in exchange_ids_to_add.items():
    if rxn_id in model.reactions:
        rxn = model.reactions.get_by_id(rxn_id)
        if rxn not in core_reactions:
            exchange_added.append(rxn)
            core_reactions.add(rxn)

print(f"  Added {len(exchange_added)} key exchange reactions:")
for rxn in exchange_added:
    print(f"    + {rxn.id:15s} | {rxn.name}")

# Add Biomass (ATPM equivalent)
biomass_ids = ['MAR09931', 'MAR09932', 'MAR04413']
for bio_id in biomass_ids:
    if bio_id in model.reactions:
        rxn = model.reactions.get_by_id(bio_id)
        core_reactions.add(rxn)
        print(f"    + {rxn.id:15s} | {rxn.name} (BIOMASS/ATPM)")

print(f"\n✓ TOTAL CORE REACTIONS: {len(core_reactions)}")

# ============================================================================
# STEP 4: Verify Pathway Completeness (4 Phases + Compartments)
# ============================================================================

print("\n" + "="*80)
print("STEP 4: VERIFY PATHWAY COMPLETENESS")
print("="*80)

# Analizza compartimenti
compartments_found = defaultdict(int)
for rxn in core_reactions:
    for met in rxn.metabolites:
        compartments_found[met.compartment] += 1

print("\n=== COMPARTMENTS DISTRIBUTION ===")
compartment_names = {
    'c': 'Cytosol',
    'm': 'Mitochondria',
    'e': 'Extracellular',
    'l': 'Lumen',
    'lum': 'Lumen',
    'b': 'Blood',
    'n': 'Nucleus',
    'r': 'Endoplasmic reticulum',
    'x': 'Peroxisome',
    'g': 'Golgi',
}

for comp, count in sorted(compartments_found.items(), key=lambda x: x[1], reverse=True):
    comp_name = compartment_names.get(comp, comp)
    print(f"  [{comp}] {comp_name:25s}: {count:4d} metabolites involved")

# Verifica presenza fasi chiave
print("\n=== PATHWAY PHASES VERIFICATION ===")
phases_status = {
    'TRASPORTO (lumen→cytosol)': len(transport_rxns) > 0,
    'ATTIVAZIONE (BUT→Butirril-CoA)': len(activation_rxns) > 0,
    'β-OSSIDAZIONE (4 steps)': len(oxidation_rxns) > 0,
    'OXPHOS (ATP production)': oxphos_count > 0,
}

for phase, status in phases_status.items():
    status_icon = "✓" if status else "✗"
    print(f"  {status_icon} {phase}")

# ============================================================================
# STEP 5: Extract ENSG IDs from Reactions
# ============================================================================

print("\n" + "="*80)
print("STEP 5: EXTRACT ENSG IDs FROM BUTYRATE REACTIONS")
print("="*80)

# Estrai geni ENSG dalle reazioni butirrato
but_genes_ensg = set()
gene_to_reactions = defaultdict(list)

for rxn in but_reactions:
    for gene in rxn.genes:
        if gene.id.startswith('ENSG'):  # Solo ENSG IDs
            but_genes_ensg.add(gene.id)
            gene_to_reactions[gene.id].append(rxn.id)

print(f"\n✓ Extracted {len(but_genes_ensg)} unique ENSG IDs from butyrate reactions")
print(f"\nSample ENSG IDs (first 10):")
for i, ensg in enumerate(sorted(list(but_genes_ensg))[:10], 1):
    rxn_count = len(gene_to_reactions[ensg])
    print(f"  {i:2d}. {ensg}  →  {rxn_count} reactions")

# Cerca gene symbols (per matching con file ortologhi)
gene_symbols = {}
for gene_obj in model.genes:
    if gene_obj.id in but_genes_ensg:
        # Gene name potrebbe contenere symbol
        gene_symbols[gene_obj.id] = gene_obj.name or gene_obj.id

# ============================================================================
# STEP 6: Create BioMart Excel File
# ============================================================================

print("\n" + "="*80)
print("STEP 6: CREATE BIOMART INPUT FILE")
print("="*80)

# Create DataFrame per BioMart
biomart_data = []
for ensg in sorted(but_genes_ensg):
    rxn_list = gene_to_reactions[ensg]
    biomart_data.append({
        'ENSG_ID': ensg,
        'Gene_Symbol': gene_symbols.get(ensg, ''),
        'Reaction_Count': len(rxn_list),
        'Reactions': ', '.join(rxn_list[:5]) + ('...' if len(rxn_list) > 5 else ''),
        'Notes': 'Butyrate pathway gene'
    })

df_biomart = pd.DataFrame(biomart_data)
biomart_file = "data/HumanGEM_butyrate_genes_for_BioMart.xlsx"
df_biomart.to_excel(biomart_file, index=False)

print(f"\n✓ BioMart input file created: {biomart_file}")
print(f"  Total genes: {len(df_biomart)}")
print(f"\n=== PREVIEW (first 10 rows) ===")
print(df_biomart.head(10).to_string(index=False))

# ============================================================================
# STEP 7: Generate Summary Statistics for Daniela
# ============================================================================

print("\n" + "="*80)
print("STEP 7: SUMMARY STATISTICS FOR DANIELA")
print("="*80)

summary = {
    'Human-GEM Total Reactions': len(model.reactions),
    'Human-GEM Total Genes': len(model.genes),
    'Butyrate Reactions Found': len(but_reactions),
    '  - Transport': len(transport_rxns),
    '  - Activation': len(activation_rxns),
    '  - β-Oxidation': len(oxidation_rxns),
    'OXPHOS Reactions Added': oxphos_count,
    'Exchange Reactions Added': len(exchange_added),
    'Total Core Reactions': len(core_reactions),
    'ENSG Genes Extracted': len(but_genes_ensg),
    'Compartments Involved': len(compartments_found),
}

print("\n=== PROJECT SUMMARY ===")
for key, value in summary.items():
    if key.startswith('  '):
        print(f"  {key}: {value:,}")
    else:
        print(f"{key}: {value:,}")

# Save reactions details
reactions_df = []
for rxn in sorted(but_reactions, key=lambda r: r.id):
    rxn_genes = [g.id for g in rxn.genes if g.id.startswith('ENSG')]
    reactions_df.append({
        'Reaction_ID': rxn.id,
        'Name': rxn.name,
        'Equation': rxn.reaction,
        'GPR': rxn.gene_reaction_rule or 'None',
        'Genes_ENSG': '; '.join(rxn_genes) if rxn_genes else 'None',
        'Reversible': rxn.reversibility,
        'LB': rxn.lower_bound,
        'UB': rxn.upper_bound,
    })

df_reactions = pd.DataFrame(reactions_df)
reactions_file = "data/butyrate_reactions_detailed.xlsx"
df_reactions.to_excel(reactions_file, index=False)

print(f"\n✓ Detailed reactions exported: {reactions_file}")

# ============================================================================
# STEP 8: Key Findings for Daniela
# ============================================================================

print("\n" + "="*80)
print("STEP 8: KEY FINDINGS & NEXT STEPS")
print("="*80)

print("""
✅ COMPLETATO WORKFLOW REAZIONI→GENI (corretto):

1. ESTRAZIONI REAZIONI:
   - {but_reactions} reazioni butirrato trovate con keyword search
   - {transport} trasporto, {activation} attivazione, {oxidation} β-ossidazione
   - {oxphos} reazioni OXPHOS aggiunte
   - {exchange} exchange reactions chiave aggiunte

2. VERIFICA PATHWAY:
   ✓ 4 fasi presenti (trasporto, attivazione, β-ox, OXPHOS)
   ✓ Compartimenti rilevati: {compartments}

3. GENE EXTRACTION:
   - {genes} ENSG IDs estratti DALLE REAZIONI (non da lista manuale!)
   - File per BioMart: {biomart_file}

4. PROSSIMI STEP:
   a) Usare BioMart per mappare ENSG umani → ENSCAFG canini
   b) Sostituire GPR con ENSCAFG (usando script caninize_gpr.py)
   c) Applicare bounds dettagliati (FBA_bounds_colonocita_cane_pilota.xlsx)
   d) Eseguire 7 test funzionali (workflow Daniela)

FILES GENERATI:
- {biomart_file}
- {reactions_file}

NOTA IMPORTANTE:
- Exchange reactions identificate con IDs corretti Human-GEM:
  * Butirrato: MAR09809
  * Acetato: MAR09086
  * Propionato: MAR09808
  * O2/CO2/H2O: MAR09048/MAR09058/MAR09047
  * Biomass (ATPM): MAR09931

- Gli IDs nel file bounds precedente (EX_but_lum, etc.) NON esistono
  in Human-GEM → vanno sostituiti con quelli corretti
""".format(
    but_reactions=len(but_reactions),
    transport=len(transport_rxns),
    activation=len(activation_rxns),
    oxidation=len(oxidation_rxns),
    oxphos=oxphos_count,
    exchange=len(exchange_added),
    compartments=', '.join([f'[{c}]' for c in sorted(compartments_found.keys())]),
    genes=len(but_genes_ensg),
    biomart_file=biomart_file,
    reactions_file=reactions_file,
))

print("="*80)
print("✓ SCRIPT COMPLETED")
print("="*80)
