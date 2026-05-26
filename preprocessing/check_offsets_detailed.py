#!/usr/bin/env python3
"""Check detailed structure of TNG offsets file."""

import h5py
import sys

filepath = sys.argv[1] if len(sys.argv) > 1 else 'TNG300_temp/offsets_099/offsets.99.hdf5'

print(f"Analyzing: {filepath}\n")

def explore_group(g, indent=0):
    """Recursively explore HDF5 group structure."""
    prefix = "  " * indent
    for key in g.keys():
        item = g[key]
        if isinstance(item, h5py.Dataset):
            print(f"{prefix}{key}: shape={item.shape}, dtype={item.dtype}")
            if item.shape[0] < 10:
                print(f"{prefix}    Values: {item[:]}")
        elif isinstance(item, h5py.Group):
            print(f"{prefix}{key}/ (group)")
            explore_group(item, indent + 1)

with h5py.File(filepath, 'r') as f:
    print("Full structure:")
    explore_group(f)
    
    # Check attributes
    print("\nFile attributes:")
    for attr in f.attrs.keys():
        print(f"  {attr}: {f.attrs[attr]}")
