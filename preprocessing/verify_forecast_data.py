#!/usr/bin/env python
"""
Verify extracted FORECAST data files are correctly formatted.

Checks that files contain all required fields and are compatible with
the FORECAST lc module.
"""

import h5py
import numpy as np
import sys
from pathlib import Path
import argparse


def verify_forecast_file(filepath, verbose=True):
    """
    Verify a FORECAST data file.
    
    Parameters:
    -----------
    filepath : str
        Path to HDF5 file
    verbose : bool
        Print detailed information
        
    Returns:
    --------
    bool : True if file is valid
    """
    
    filepath = Path(filepath)
    
    if not filepath.exists():
        print(f"✗ File not found: {filepath}")
        return False
    
    if verbose:
        print(f"\nVerifying: {filepath}")
        print(f"{'='*60}")
    
    try:
        with h5py.File(filepath, 'r') as f:
            
            # Check required groups
            required_groups = ['Header', 'PartType0', 'PartType4']
            missing_groups = []
            
            for group in required_groups:
                if group not in f:
                    missing_groups.append(group)
            
            if missing_groups:
                print(f"✗ Missing required groups: {missing_groups}")
                return False
            
            # Check Gas (PartType0) fields
            required_gas_fields = ['Coordinates', 'Velocities', 'Masses', 'ParticleIDs', 'SubhaloID']
            gas_group = f['PartType0']
            missing_gas = []
            
            for field in required_gas_fields:
                if field not in gas_group:
                    missing_gas.append(field)
            
            if missing_gas:
                print(f"✗ PartType0 missing fields: {missing_gas}")
                return False
            
            # Check Stars (PartType4) fields
            required_star_fields = ['Coordinates', 'Velocities', 'Masses', 'ParticleIDs', 
                                   'SubhaloID', 'GFM_StellarFormationTime']
            star_group = f['PartType4']
            missing_star = []
            
            for field in required_star_fields:
                if field not in star_group:
                    missing_star.append(field)
            
            if missing_star:
                print(f"✗ PartType4 missing fields: {missing_star}")
                return False
            
            # Check data shapes and types
            n_gas = len(gas_group['ParticleIDs'])
            n_star = len(star_group['ParticleIDs'])
            
            if verbose:
                print(f"\n✓ All required groups and fields present")
                print(f"\nParticle counts:")
                print(f"  Gas (PartType0): {n_gas:,}")
                print(f"  Stars (PartType4): {n_star:,}")
            
            # Check array shapes
            issues = []
            
            # Gas
            if gas_group['Coordinates'].shape != (n_gas, 3):
                issues.append(f"PartType0/Coordinates has wrong shape: {gas_group['Coordinates'].shape}")
            if gas_group['Velocities'].shape != (n_gas, 3):
                issues.append(f"PartType0/Velocities has wrong shape: {gas_group['Velocities'].shape}")
            if gas_group['Masses'].shape != (n_gas,):
                issues.append(f"PartType0/Masses has wrong shape: {gas_group['Masses'].shape}")
            if gas_group['SubhaloID'].shape != (n_gas,):
                issues.append(f"PartType0/SubhaloID has wrong shape: {gas_group['SubhaloID'].shape}")
            
            # Stars
            if star_group['Coordinates'].shape != (n_star, 3):
                issues.append(f"PartType4/Coordinates has wrong shape: {star_group['Coordinates'].shape}")
            if star_group['Velocities'].shape != (n_star, 3):
                issues.append(f"PartType4/Velocities has wrong shape: {star_group['Velocities'].shape}")
            if star_group['Masses'].shape != (n_star,):
                issues.append(f"PartType4/Masses has wrong shape: {star_group['Masses'].shape}")
            if star_group['SubhaloID'].shape != (n_star,):
                issues.append(f"PartType4/SubhaloID has wrong shape: {star_group['SubhaloID'].shape}")
            if star_group['GFM_StellarFormationTime'].shape != (n_star,):
                issues.append(f"PartType4/GFM_StellarFormationTime has wrong shape")
            
            if issues:
                print(f"\n✗ Shape validation failed:")
                for issue in issues:
                    print(f"  {issue}")
                return False
            
            if verbose:
                print(f"\n✓ All arrays have correct shapes")
            
            # Check subhalo statistics
            gas_subhalo = gas_group['SubhaloID'][:]
            star_subhalo = star_group['SubhaloID'][:]
            
            n_gas_assigned = np.sum(gas_subhalo >= 0)
            n_star_assigned = np.sum(star_subhalo >= 0)
            
            if verbose:
                print(f"\nSubhalo assignment:")
                print(f"  Gas particles in subhalos: {n_gas_assigned:,} ({100*n_gas_assigned/n_gas:.1f}%)")
                print(f"  Star particles in subhalos: {n_star_assigned:,} ({100*n_star_assigned/n_star:.1f}%)")
            
            if n_gas_assigned == 0 and n_star_assigned == 0:
                print(f"\n  ⚠ WARNING: No particles assigned to subhalos!")
                print(f"  This is expected if:")
                print(f"    - Only partial data was downloaded (test mode)")
                print(f"    - Group catalogs were not available")
                print(f"  The file is still valid for FORECAST.")
            
            # Check Header
            header = f['Header'].attrs
            if verbose:
                print(f"\nHeader information:")
                print(f"  BoxSize: {header['BoxSize']:.1f} kpc/h")
                print(f"  Redshift: {header['Redshift']:.6f}")
                print(f"  Scale factor (Time): {header['Time']:.6f}")
                print(f"  Hubble parameter: {header['HubbleParam']:.4f}")
            
            # Check for original file metadata
            if 'ExtractedForFORECAST' in f.attrs:
                if verbose:
                    print(f"\nExtraction metadata:")
                    print(f"  Extracted for FORECAST: Yes")
                    if 'SnapshotNumber' in f.attrs:
                        print(f"  Original snapshot: {f.attrs['SnapshotNumber']}")
            
            # File size
            file_size = filepath.stat().st_size / (1024**3)
            if verbose:
                print(f"\nFile size: {file_size:.2f} GB")
            
            if verbose:
                print(f"\n{'='*60}")
                print(f"✓ FILE IS VALID FOR FORECAST")
                print(f"{'='*60}\n")
            
            return True
            
    except Exception as e:
        print(f"✗ Error reading file: {e}")
        return False


def main():
    parser = argparse.ArgumentParser(
        description='Verify FORECAST data files'
    )
    
    parser.add_argument('files', nargs='+',
                       help='HDF5 files to verify')
    parser.add_argument('--quiet', action='store_true',
                       help='Only show pass/fail, no details')
    
    args = parser.parse_args()
    
    print(f"\nVerifying {len(args.files)} file(s)...\n")
    
    results = []
    for filepath in args.files:
        valid = verify_forecast_file(filepath, verbose=not args.quiet)
        results.append((filepath, valid))
        
        if args.quiet:
            status = "✓ VALID" if valid else "✗ INVALID"
            print(f"{status}: {filepath}")
    
    # Summary
    if len(results) > 1:
        print(f"\n{'='*60}")
        print(f"SUMMARY")
        print(f"{'='*60}\n")
        
        valid_count = sum(1 for _, v in results if v)
        invalid_count = len(results) - valid_count
        
        print(f"Total files: {len(results)}")
        print(f"Valid: {valid_count}")
        print(f"Invalid: {invalid_count}\n")
        
        if invalid_count > 0:
            print(f"Invalid files:")
            for filepath, valid in results:
                if not valid:
                    print(f"  {filepath}")
            print()
    
    # Return exit code
    all_valid = all(v for _, v in results)
    return 0 if all_valid else 1


if __name__ == "__main__":
    sys.exit(main())
