import h5py
import numpy as np
import os
import sys

def check_subhalo_id_in_snapshot(snapshot_path, verbose=True):
    """
    Check if subhalo ID fields exist in a TNG snapshot file.
    
    Parameters:
    -----------
    snapshot_path : str
        Path to the HDF5 snapshot file (e.g., 'snap_099.0.hdf5')
    verbose : bool
        Print detailed information
    
    Returns:
    --------
    dict : Dictionary with results for each particle type
    """
    
    results = {}
    
    if not os.path.exists(snapshot_path):
        print(f"Error: File not found: {snapshot_path}")
        return None
    
    try:
        with h5py.File(snapshot_path, 'r') as f:
            
            if verbose:
                print(f"\n{'='*60}")
                print(f"Analyzing: {snapshot_path}")
                print(f"{'='*60}\n")
            
            # Check each particle type
            particle_types = {
                'PartType0': 'Gas',
                'PartType1': 'Dark Matter',
                'PartType4': 'Stars',
                'PartType5': 'Black Holes'
            }
            
            for part_key, part_name in particle_types.items():
                if part_key in f.keys():
                    if verbose:
                        print(f"\n{part_name} ({part_key}):")
                        print("-" * 40)
                    
                    part_group = f[part_key]
                    
                    # List all available fields
                    available_fields = list(part_group.keys())
                    
                    if verbose:
                        print(f"Available fields: {available_fields}")
                    
                    # Check for subhalo ID fields (various possible names)
                    subhalo_fields = [
                        'SubfindHaloID',
                        'SubhaloID', 
                        'GFM_SubhaloID',
                        'SubfindID'
                    ]
                    
                    found_fields = []
                    for field in subhalo_fields:
                        if field in available_fields:
                            found_fields.append(field)
                            
                            if verbose:
                                data = part_group[field][:]
                                print(f"\n✓ Found: '{field}'")
                                print(f"  Shape: {data.shape}")
                                print(f"  Dtype: {data.dtype}")
                                print(f"  Min value: {np.min(data)}")
                                print(f"  Max value: {np.max(data)}")
                                print(f"  Unique values: {len(np.unique(data))}")
                                print(f"  Particles in subhalos (ID >= 0): {np.sum(data >= 0)}")
                                print(f"  Unbound particles (ID < 0): {np.sum(data < 0)}")
                    
                    results[part_key] = {
                        'particle_type': part_name,
                        'exists': True,
                        'num_particles': len(part_group[available_fields[0]]),
                        'available_fields': available_fields,
                        'subhalo_fields_found': found_fields,
                        'has_subhalo_info': len(found_fields) > 0
                    }
                    
                    if not found_fields and verbose:
                        print(f"\n✗ No subhalo ID field found for {part_name}")
                        print(f"  Searched for: {subhalo_fields}")
                else:
                    results[part_key] = {
                        'particle_type': part_name,
                        'exists': False
                    }
            
            # Check header information
            if 'Header' in f.keys():
                if verbose:
                    print(f"\n{'='*60}")
                    print("Header Information:")
                    print("-" * 40)
                header = f['Header'].attrs
                for key in header.keys():
                    if verbose:
                        print(f"{key}: {header[key]}")
            
            if verbose:
                print(f"\n{'='*60}")
                print("SUMMARY:")
                print("-" * 40)
                for part_key, info in results.items():
                    if info['exists']:
                        status = "✓ YES" if info['has_subhalo_info'] else "✗ NO"
                        print(f"{info['particle_type']:15s}: Subhalo IDs found? {status}")
                print(f"{'='*60}\n")
    
    except Exception as e:
        print(f"Error reading file: {e}")
        return None
    
    return results


def check_snapshot_directory(snapdir_path, snap_number=99):
    """
    Check all files in a snapshot directory.
    
    Parameters:
    -----------
    snapdir_path : str
        Path to snapshot directory (e.g., 'TNG100/snapdir_099/')
    snap_number : int
        Snapshot number (default: 99 for z=0)
    """
    
    print(f"\nChecking snapshot directory: {snapdir_path}")
    print(f"Looking for snap_{snap_number:03d}.*.hdf5 files\n")
    
    # Find all files for this snapshot
    if os.path.isdir(snapdir_path):
        files = sorted([f for f in os.listdir(snapdir_path) 
                       if f.startswith(f'snap_{snap_number:03d}') and f.endswith('.hdf5')])
        
        if not files:
            print(f"No snapshot files found for snap_{snap_number:03d}")
            return
        
        print(f"Found {len(files)} files. Checking first file...\n")
        first_file = os.path.join(snapdir_path, files[0])
        results = check_subhalo_id_in_snapshot(first_file)
        
        return results
    else:
        print(f"Directory not found: {snapdir_path}")
        return None


if __name__ == "__main__":
    
    # Example usage:
    
    # Option 1: Check a single snapshot file
    # snapshot_file = "../TNG100/snapdir_099/snap_099.0.hdf5"
    # results = check_subhalo_id_in_snapshot(snapshot_file)
    
    # Option 2: Check a snapshot directory
    snapshot_dir = "./"
    results = check_snapshot_directory(snapshot_dir, snap_number=98)
    
    # Option 3: Use command line argument
    if len(sys.argv) > 1:
        input_path = sys.argv[1]
        if os.path.isdir(input_path):
            snap_num = int(sys.argv[2]) if len(sys.argv) > 2 else 99
            results = check_snapshot_directory(input_path, snap_num)
        else:
            results = check_subhalo_id_in_snapshot(input_path)