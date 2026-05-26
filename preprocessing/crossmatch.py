import numpy as np
import h5py
import illustris_python as il
from pathlib import Path
from tqdm import tqdm
import time

# --- Configuration ---
basePath = '/Users/pmsanch1/code/FORECAST/TNG_download/'
snapNum = 98
output_file = f'/Users/pmsanch1/code/FORECAST/TNG300/forecast_data/TNG300-3_custom_snap{snapNum:02d}.hdf5'

# Ensure output directory exists
Path(output_file).parent.mkdir(parents=True, exist_ok=True)

start_time = time.time()

print("Initializing metadata and loading headers...")
# 1. Fetch total particle counts from the snapshot header
# Read header directly from first snapshot chunk
snap_file = f"{basePath}/snapdir_{snapNum:03d}/snapshot-{snapNum}.0.hdf5"
with h5py.File(snap_file, 'r') as f:
    header = dict(f['Header'].attrs)
    n_gas_total = header['NumPart_Total'][0]   # PartType0
    n_star_total = header['NumPart_Total'][4]  # PartType4

print(f"Total particles: Gas={n_gas_total:,}, Stars={n_star_total:,}")

# 2. Load subhalo lengths from Group Catalog and offsets from Offsets file
# Read SubhaloLenType from all group catalog chunks
print("Loading subhalo information from group catalogs...")
groupcat_dir = Path(f"{basePath}/groups_{snapNum:03d}")
groupcat_files = sorted(groupcat_dir.glob(f"groupcat-{snapNum}.*.hdf5"))

subhalo_lens_list = []
for gc_file in groupcat_files:
    with h5py.File(gc_file, 'r') as f:
        subhalo_lens_list.append(f['Subhalo/SubhaloLenType'][:])

# Concatenate all chunks: shape (N_subhalos, 6)
subhalo_lens = np.vstack(subhalo_lens_list)
n_subhalos = len(subhalo_lens)
n_subhalos_nonzero = np.sum(subhalo_lens.sum(axis=1) > 0)
print(f"Total subhalos: {n_subhalos:,}, Non-zero subhalos: {n_subhalos_nonzero:,}")

# Read global offsets directly from the offset file
offset_file_path = f"{basePath}/offsets_{snapNum:03d}/offsets.{snapNum}.hdf5"
with h5py.File(offset_file_path, 'r') as f_offset:
    # Subhalo/SnapByType shape: (N_subhalos, 6)
    subhalo_offsets = f_offset['Subhalo/SnapByType'][:]

# --- Reconstruct SubhaloIDs for all particles ---
print("Reconstructing Subhalo membership arrays...")
# Initialize tracking arrays with -1 (unbound/fuzz particles)
gas_subhalo_ids = np.full(n_gas_total, -1, dtype=np.int32)
star_subhalo_ids = np.full(n_star_total, -1, dtype=np.int32)

# Slicing loop to map particle blocks to their respective Subhalo ID
for sub_id in tqdm(range(n_subhalos), desc="Mapping particles to subhalos"):
    # Gas (PartType0)
    g_start = subhalo_offsets[sub_id, 0]
    g_end = g_start + subhalo_lens[sub_id, 0]
    if g_end > g_start:
        gas_subhalo_ids[g_start:g_end] = sub_id
        
    # Stars (PartType4)
    s_start = subhalo_offsets[sub_id, 4]
    s_end = s_start + subhalo_lens[sub_id, 4]
    if s_end > s_start:
        star_subhalo_ids[s_start:s_end] = sub_id

print(f"  Mapped {np.sum(gas_subhalo_ids >= 0):,} gas particles to subhalos")
print(f"  Mapped {np.sum(star_subhalo_ids >= 0):,} star particles to subhalos")

# --- Load Particle Data & Write directly to HDF5 ---
print("Loading snapshot fields and writing custom HDF5 dataset...")

# Helper function to load a field from all snapshot chunks
def load_field_from_snapshots(part_type, field_name):
    """Load a field from all snapshot chunks and concatenate."""
    snapdir = Path(f"{basePath}/snapdir_{snapNum:03d}")
    snap_files = sorted(snapdir.glob(f"snapshot-{snapNum}.*.hdf5"))
    
    data_list = []
    for snap_file in snap_files:
        with h5py.File(snap_file, 'r') as f:
            part_key = f'PartType{part_type}'
            if part_key in f and field_name in f[part_key]:
                data_list.append(f[part_key][field_name][:])
    
    # Concatenate along first axis
    return np.concatenate(data_list, axis=0) if data_list else None

with h5py.File(output_file, 'w') as f_out:
    # --- Copy Header and metadata from first snapshot chunk ---
    print("Copying Header and metadata...")
    with h5py.File(snap_file, 'r') as f_snap:
        # Copy Header group (attributes only)
        if 'Header' in f_snap:
            h_out = f_out.create_group('Header')
            for key, value in f_snap['Header'].attrs.items():
                h_out.attrs[key] = value
            print(f"  ✓ Header copied")
        
        # Copy Config group if it exists
        if 'Config' in f_snap:
            f_snap.copy('Config', f_out)
            print(f"  ✓ Config copied")
        
        # Copy Parameters group if it exists
        if 'Parameters' in f_snap:
            f_snap.copy('Parameters', f_out)
            print(f"  ✓ Parameters copied")
    
    # --- GAS PARTICLES (PartType0) ---
    print("Processing PartType0 (Gas)...")
    g0 = f_out.create_group('PartType0')
    
    gas_fields = ['Coordinates', 'Velocities', 'Masses', 'ParticleIDs', 'GFM_Metallicity']
    for field in gas_fields:
        print(f"  Loading {field}...")
        data = load_field_from_snapshots(0, field)
        if data is not None:
            g0.create_dataset(field, data=data, compression='gzip', compression_opts=4)
    
    # Append the calculated SubhaloID array
    print(f"  Writing SubhaloID...")
    g0.create_dataset('SubhaloID', data=gas_subhalo_ids, compression='gzip', compression_opts=4)

    # --- STAR PARTICLES (PartType4) ---
    print("Processing PartType4 (Stars)...")
    g4 = f_out.create_group('PartType4')
    
    star_fields = ['Coordinates', 'Velocities', 'Masses', 'ParticleIDs', 'GFM_Metallicity', 'GFM_StellarFormationTime']
    for field in star_fields:
        print(f"  Loading {field}...")
        data = load_field_from_snapshots(4, field)
        if data is not None:
            g4.create_dataset(field, data=data, compression='gzip', compression_opts=4)
        
    # Append the calculated SubhaloID array
    print(f"  Writing SubhaloID...")
    g4.create_dataset('SubhaloID', data=star_subhalo_ids, compression='gzip', compression_opts=4)
    
    # --- Add custom metadata ---
    print("Adding custom metadata...")
    f_out.attrs['CustomFile'] = True
    f_out.attrs['ProcessedWithCrossmatch'] = True
    f_out.attrs['ProcessingDate'] = time.strftime('%Y-%m-%d %H:%M:%S')
    f_out.attrs['SourceSnapshot'] = snapNum
    f_out.attrs['SubhaloIDAdded'] = 'Reconstructed from offsets file'
    f_out.attrs['TotalSubhalos'] = n_subhalos
    f_out.attrs['TotalGasParticles'] = n_gas_total
    f_out.attrs['TotalStarParticles'] = n_star_total
    f_out.attrs['GasInSubhalos'] = int(np.sum(gas_subhalo_ids >= 0))
    f_out.attrs['StarsInSubhalos'] = int(np.sum(star_subhalo_ids >= 0))
    f_out.attrs['FieldsIncluded'] = 'Coordinates,Velocities,Masses,ParticleIDs,GFM_Metallicity,GFM_StellarFormationTime(stars),SubhaloID'
    print(f"  ✓ Metadata added")

elapsed_time = time.time() - start_time

print(f"\n{'='*60}")
print(f"SUCCESS! Custom snapshot compiled")
print(f"{'='*60}")
print(f"Output file: {output_file}")
print(f"File size: {Path(output_file).stat().st_size / (1024**3):.2f} GB")
print(f"Processing time: {elapsed_time/60:.1f} minutes")
print(f"\nParticle Statistics:")
print(f"  Gas particles with subhalo: {np.sum(gas_subhalo_ids >= 0):,} / {n_gas_total:,} ({100*np.sum(gas_subhalo_ids >= 0)/n_gas_total:.1f}%)")
print(f"  Star particles with subhalo: {np.sum(star_subhalo_ids >= 0):,} / {n_star_total:,} ({100*np.sum(star_subhalo_ids >= 0)/n_star_total:.1f}%)")
print(f"  Total subhalos: {n_subhalos:,}, Non-zero subhalos: {n_subhalos_nonzero:,}")
print(f"\nFile Structure:")
print(f"  ✓ Header (with all simulation metadata)")
print(f"  ✓ Config (simulation configuration)")
print(f"  ✓ Parameters (simulation parameters)")
print(f"  ✓ PartType0 (Gas: {len(gas_fields)+1} fields)")
print(f"  ✓ PartType4 (Stars: {len(star_fields)+1} fields)")
print(f"{'='*60}\n")
