import h5py
import numpy as np

groupcat_file = "TNG100/groups_099/fof_subhalo_tab_099.0.hdf5"

print(f"Checking group catalog structure: {groupcat_file}\n")

with h5py.File(groupcat_file, 'r') as f:
    print("Top-level groups:")
    for key in f.keys():
        print(f"  - {key}")
    
    print("\nIDs group structure:")
    if 'IDs' in f:
        ids_group = f['IDs']
        print(f"  Keys in IDs: {list(ids_group.keys())}")
        for key in ids_group.keys():
            data = ids_group[key]
            print(f"    {key}: shape={data.shape}, dtype={data.dtype}")
            if len(data) > 0:
                print(f"      First few IDs: {data[:5]}")
    else:
        print("  No 'IDs' group found!")
    
    print("\nSubhalo/SubhaloLenType:")
    if 'Subhalo' in f and 'SubhaloLenType' in f['Subhalo']:
        subhalo_len = f['Subhalo/SubhaloLenType'][:]
        print(f"  Shape: {subhalo_len.shape}")
        print(f"  First 5 subhalos particle counts (all types):")
        for i in range(min(5, len(subhalo_len))):
            print(f"    Subhalo {i}: Gas={subhalo_len[i,0]}, DM={subhalo_len[i,1]}, Stars={subhalo_len[i,4]}")
        
        print(f"\n  Total particles by type:")
        totals = np.sum(subhalo_len, axis=0)
        print(f"    Gas (type 0): {totals[0]:,}")
        print(f"    DM (type 1): {totals[1]:,}")  
        print(f"    Stars (type 4): {totals[4]:,}")

