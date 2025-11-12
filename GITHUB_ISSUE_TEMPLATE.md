# Canine Colon GEM - Implementation Roadmap

## Milestone 1: Environment Setup & Data Preparation
- [ ] Create Python virtual environment
- [ ] Install dependencies (`pip install -r requirements.txt`)
- [ ] Download Human-GEM model from [GitHub](https://github.com/SysBioChalmers/Human-GEM/releases)
- [ ] Place Human-GEM.xml in `data/` folder
- [ ] Verify all data files are present

## Milestone 2: Model Loading & Exploration
- [ ] Load Human-GEM model with COBRApy
- [ ] Validate model structure (reactions, metabolites, genes)
- [ ] Extract butyrate-related reactions
- [ ] Identify core metabolic subsystems
- [ ] Document model statistics

## Milestone 3: Gene Mapping & Ortholog Integration
- [ ] Load ortholog mapping file (`02_human_dog_orthologs.xlsx`)
- [ ] Verify all 14 core genes have mappings
- [ ] Check orthology types (1:1, 1:many)
- [ ] Validate % protein identity thresholds
- [ ] Handle unmapped genes (if any)

## Milestone 4: GPR Substitution (Caninization)
- [ ] Create copy of human model
- [ ] Substitute human gene IDs → dog orthologs in GPRs
- [ ] Preserve GPR logic (AND/OR operators)
- [ ] Handle complex cases (protein complexes, isozymes)
- [ ] Document substitution statistics

## Milestone 5: Model Validation
- [ ] Check GPR syntax integrity (balanced parentheses)
- [ ] Identify orphan reactions (no associated genes)
- [ ] Verify core pathway completeness
  - [ ] SCFA transporters (SLC16A1, SLC5A8/12)
  - [ ] Activation (ACSM2A/2B, ACSS3)
  - [ ] β-oxidation (ACADS, ECHS1, HADHA/B, ACAT1)
  - [ ] ETF chain (ETFA, ETFB, ETFDH)
  - [ ] OXPHOS (Complexes I-V)
- [ ] Check mass/charge balance
- [ ] Document validation results

## Milestone 6: Physiological Bounds Application
- [ ] Load bounds file (`01_physiological_bounds.xlsx`)
- [ ] Apply "healthy dog" baseline constraints
  - [ ] Butyrate uptake: -8 mmol/gDW/h
  - [ ] Acetate uptake: -25 mmol/gDW/h
  - [ ] Propionate uptake: -12 mmol/gDW/h
  - [ ] O₂ uptake: -0.5 mmol/gDW/h (hypoxia)
  - [ ] ATP maintenance: 8 mmol/gDW/h
- [ ] Set objective function (ATPM)
- [ ] Verify bounds consistency

## Milestone 7: FBA Analysis
- [ ] Run standard FBA
- [ ] Verify optimal solution status
- [ ] Check objective value (ATP production)
- [ ] Analyze key flux distributions
  - [ ] SCFA uptake fluxes
  - [ ] O₂ consumption
  - [ ] ATP synthesis rate
- [ ] Run pFBA (parsimonious FBA)
- [ ] Compare FBA vs pFBA solutions
- [ ] Identify active vs inactive reactions

## Milestone 8: Flux Variability Analysis
- [ ] Run FVA on core reactions
- [ ] Identify essential reactions (fixed flux)
- [ ] Find redundant pathways
- [ ] Assess model flexibility
- [ ] Document flux ranges

## Milestone 9: Results Visualization
- [ ] Plot key metabolite exchange fluxes
- [ ] Visualize pathway activity map
- [ ] Compare human vs canine flux distributions
- [ ] Create summary statistics table
- [ ] Generate figures for publication/presentation

## Milestone 10: Model Export & Documentation
- [ ] Export canine model to SBML format
- [ ] Save flux results to CSV
- [ ] Document model assumptions
- [ ] Create supplementary data files
- [ ] Write methods section draft

## Milestone 11: Sensitivity Analysis
- [ ] Test butyrate concentration variations (2-20 mM)
- [ ] Simulate hypoxia gradient (O₂: 0.1-2.0 mmol/gDW/h)
- [ ] Analyze SCFA ratio effects (but:ac:pro)
- [ ] Identify critical parameters
- [ ] Document robustness

## Milestone 12: Dysbiosis Scenarios
- [ ] Simulate reduced butyrate availability (-50%, -80%)
- [ ] Model increased O₂ exposure (2x, 5x)
- [ ] Predict metabolic shifts
- [ ] Compare healthy vs dysbiotic flux profiles
- [ ] Identify biomarker candidates

## Future Milestones (Phase 2)
- [ ] Expand to full colonocyte metabolism
  - [ ] Glycolysis
  - [ ] TCA cycle
  - [ ] Amino acid metabolism
  - [ ] Lipid metabolism
- [ ] Multi-compartment model (lumen-epithelium-blood)
- [ ] Microbiota integration (community FBA)
- [ ] Time-course simulations (dynamic FBA)
- [ ] Clinical data integration

---

## Notes
- Mark tasks as completed with `[x]` as you progress
- Add comments/findings under each milestone
- Link commits to specific tasks
- Update README with results

## References
- Human-GEM: Robinson et al. (2020) *Science Signaling*
- COBRApy: Ebrahim et al. (2013) *BMC Systems Biology*
- Butyrate metabolism: Minamoto et al. (2019), Palmqvist et al. (2023)
