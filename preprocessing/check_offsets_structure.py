#!/usr/bin/env python3
"""Check structure of TNG offsets file."""

import h5py
import sys

if len(sys.argv) > 1:
    filepath = sys.argv[1]
else:
    filepath = 'TNG300_temp/offsets_099/offsets.99.hdf5'

print(f"Analyzing: {filepath}\n")

with h5py.File(filepath, 'r') as f:
    print("Top-level keys:")
    for key in f.keys():
        print(f"  - {key}")
    
    print("\nChecking PartType0 (Gas):")
    if 'PartType0' in f:
        for key in f['PartType0'].keys():
            data = f['PartType0'][key]
            print(f"  {key}: shape={data.shape}, dtype={data.dtype}")
            if len(data.shape) == 1 and data.shape[0] < 20:
                print(f"    Values: {data[:]}")
    
    print("\nChecking PartType4 (Stars):")
    if 'PartType4' in f:
        for key in f['PartType4'].keys():
            data = f['PartType4'][key]
            print(f"  {key}: shape={data.shape}, dtype={data.dtype}")
            if len(data.shape) == 1 and data.shape[0] < 20:
                print(f"    Values: {data[:]}")
    
    print("\nHeader information:")
    if 'Header' in f.attrs:
        print(f"  Header attrs: {dict(f.attrs)}")
    
    for attr_name in f.attrs.keys():
        print(f"  {attr_name}: {f.attrs[attr_name]}")
