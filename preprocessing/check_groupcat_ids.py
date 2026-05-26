#!/usr/bin/env python3
"""Check if group catalog files contain particle IDs for subhalo assignment."""

import h5py
import glob
import sys

if len(sys.argv) > 1:
    pattern = sys.argv[1]
else:
    pattern = 'TNG300_temp/groups_099/*.hdf5'

groupcat_files = sorted(glob.glob(pattern))
print(f'Found {len(groupcat_files)} group catalog files\n')

for i, gfile in enumerate(groupcat_files):
    with h5py.File(gfile, 'r') as f:
        print(f'File {i}: {gfile.split("/")[-1]}')
        
        # Check if IDs group exists
        if 'IDs' in f:
            ids_group = f['IDs']
            keys = list(ids_group.keys())
            print(f'  IDs group keys: {keys}')
            
            if len(keys) == 0:
                print('  WARNING: IDs group is EMPTY!')
            
            # Check each particle type
            for ptype in [0, 4]:
                key = f'PartType{ptype}'
                if key in ids_group:
                    ids = ids_group[key]
                    print(f'    {key}: shape={ids.shape}, dtype={ids.dtype}')
        else:
            print('  No IDs group found')
        
        # Check subhalo lengths
        if 'Subhalo' in f and 'SubhaloLenType' in f['Subhalo']:
            subhalo_len = f['Subhalo/SubhaloLenType'][:]
            n_subhalos = len(subhalo_len)
            print(f'  Subhalos: {n_subhalos}')
            if n_subhalos > 0:
                total_gas = int(subhalo_len[:, 0].sum())
                total_stars = int(subhalo_len[:, 4].sum())
                print(f'    Total gas in subhalos: {total_gas:,}')
                print(f'    Total stars in subhalos: {total_stars:,}')
        print()
