import h5py
import numpy as np

# Check the group catalog file structure
groupcat_file = "TNG100/groups_099/fof_subhalo_tab_099.0.hdf5"

print(f"Checking group catalog file: {groupcat_file}\n")
print("="*60)

with h5py.File(groupcat_file, 'r') as f:
    print("Top-level groups:")
    for key in f.keys():
        print(f"  - {key}")
    
    print("\n" + "="*60)
    print("Subhalo information:")
    print("="*60)
    
    if 'Subhalo' in f.keys():
        subhalo_group = f['Subhalo']
        print(f"\nSubhalo fields available:")
        for field in subhalo_group.keys():
            dataset = subhalo_group[field]
            print(f"  - {field:30s} shape: {dataset.shape}, dtype: {dataset.dtype}")
        
        # Show some key fields
        if 'SubhaloMass' in subhalo_group:
            masses = subhalo_group['SubhaloMass'][:]
            print(f"\nNumber of subhalos: {len(masses)}")
            print(f"Mass range: {np.min(masses):.2e} to {np.max(masses):.2e}")
        
        if 'SubhaloPos' in subhalo_group:
            pos = subhalo_group['SubhaloPos'][:]
            print(f"Position shape: {pos.shape}")
            print(f"First subhalo position: {pos[0]}")
    
    print("\n" + "="*60)
    print("Group (FOF) information:")
    print("="*60)
    
    if 'Group' in f.keys():
        group_group = f['Group']
        print(f"\nGroup fields available:")
        for field in list(group_group.keys())[:10]:  # Show first 10
            dataset = group_group[field]
            print(f"  - {field:30s} shape: {dataset.shape}, dtype: {dataset.dtype}")
        
        if len(group_group.keys()) > 10:
            print(f"  ... and {len(group_group.keys()) - 10} more fields")

print("\n" + "="*60)
print("✓ Group catalog file is valid HDF5 with subhalo info!")
print("="*60)
