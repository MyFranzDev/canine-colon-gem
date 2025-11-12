#!/usr/bin/env python3
"""
Quick setup verification script for Canine Colon GEM project
"""

import sys

def test_imports():
    """Test all required imports"""
    print("Testing imports...")
    try:
        import cobra
        import pandas as pd
        import numpy as np
        import matplotlib.pyplot as plt
        import seaborn as sns
        print("  ✓ All core packages imported")
        return True
    except ImportError as e:
        print(f"  ✗ Import error: {e}")
        return False

def test_model_loading():
    """Test Human-GEM loading"""
    print("\nTesting Human-GEM loading...")
    try:
        import cobra
        model = cobra.io.read_sbml_model('data/Human-GEM.xml')
        print(f"  ✓ Model loaded: {model.id}")
        print(f"    - Reactions: {len(model.reactions)}")
        print(f"    - Metabolites: {len(model.metabolites)}")
        print(f"    - Genes: {len(model.genes)}")
        return True
    except Exception as e:
        print(f"  ✗ Error loading model: {e}")
        return False

def test_data_files():
    """Test data files availability"""
    print("\nTesting data files...")
    import os
    files = [
        'data/01_physiological_bounds.xlsx',
        'data/02_human_dog_orthologs.xlsx',
        'data/03_kinetic_parameters.xlsx',
        'data/Human-GEM.xml'
    ]

    all_exist = True
    for f in files:
        if os.path.exists(f):
            size = os.path.getsize(f) / 1024  # KB
            print(f"  ✓ {f} ({size:.1f} KB)")
        else:
            print(f"  ✗ {f} NOT FOUND")
            all_exist = False

    return all_exist

def test_ortholog_data():
    """Test ortholog mapping file"""
    print("\nTesting ortholog mappings...")
    try:
        import pandas as pd
        df = pd.read_excel('data/02_human_dog_orthologs.xlsx')
        print(f"  ✓ Loaded {len(df)} ortholog mappings")
        print(f"    Columns: {list(df.columns)[:3]}...")
        return True
    except Exception as e:
        print(f"  ✗ Error reading orthologs: {e}")
        return False

def main():
    """Run all tests"""
    print("="*60)
    print("CANINE COLON GEM - SETUP VERIFICATION")
    print("="*60)

    tests = [
        test_imports,
        test_data_files,
        test_model_loading,
        test_ortholog_data
    ]

    results = [test() for test in tests]

    print("\n" + "="*60)
    if all(results):
        print("✓ ALL TESTS PASSED - Setup complete!")
        print("="*60)
        print("\nNext steps:")
        print("  1. Open Jupyter Lab: jupyter lab")
        print("  2. Navigate to notebooks/01_caninization_workflow.ipynb")
        print("  3. Run cells sequentially")
        return 0
    else:
        print("✗ SOME TESTS FAILED - Check errors above")
        print("="*60)
        return 1

if __name__ == '__main__':
    sys.exit(main())
