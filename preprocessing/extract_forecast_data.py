#!/usr/bin/env python
"""
Extract required fields from TNG snapshots for FORECAST lightcone code.

This script reads TNG snapshot and group catalog files and creates new HDF5 files
containing only the fields required by FORECAST:
- Gas (PartType0): Coordinates, Velocities, Masses, ParticleIDs, SubhaloID
- Stars (PartType4): Coordinates, Velocities, Masses, ParticleIDs, SubhaloID, GFM_StellarFormationTime

The subhalo membership is extracted from the group catalog files.
"""

import h5py
import numpy as np
import os
import sys
import argparse
from pathlib import Path
from tqdm import tqdm


class TNGDataExtractor:
    """
    Extract FORECAST-required fields from TNG snapshots.
    """
    
    def __init__(self, snapshot_dir, groupcat_dir, output_dir, snapshot_num):
        """
        Initialize the extractor.
        
        Parameters:
        -----------
        snapshot_dir : str
            Directory containing snapshot files (e.g., 'TNG100/snapdir_099/')
        groupcat_dir : str
            Directory containing group catalog files (e.g., 'TNG100/groups_099/')
        output_dir : str
            Output directory for extracted data
        snapshot_num : int
            Snapshot number (e.g., 99)
        """
        self.snapshot_dir = Path(snapshot_dir)
        self.groupcat_dir = Path(groupcat_dir)
        self.output_dir = Path(output_dir)
        self.snapshot_num = snapshot_num
        
        # Create output directory
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
        # Fields to extract for each particle type
        self.gas_fields = ['Coordinates', 'Velocities', 'Masses', 'ParticleIDs']
        self.star_fields = ['Coordinates', 'Velocities', 'Masses', 'ParticleIDs', 'GFM_StellarFormationTime']
        
        print(f"TNG Data Extractor initialized")
        print(f"Snapshot dir: {self.snapshot_dir}")
        print(f"Groupcat dir: {self.groupcat_dir}")
        print(f"Output dir: {self.output_dir}")
    
    def find_snapshot_files(self):
        """Find all snapshot files."""
        pattern = f"snap_{self.snapshot_num:03d}.*.hdf5"
        files = sorted(list(self.snapshot_dir.glob(pattern)))
        print(f"Found {len(files)} snapshot files")
        return files
    
    def find_groupcat_files(self):
        """Find all group catalog files."""
        pattern = f"fof_subhalo_tab_{self.snapshot_num:03d}.*.hdf5"
        files = sorted(list(self.groupcat_dir.glob(pattern)))
        print(f"Found {len(files)} group catalog files")
        return files
    
    def build_subhalo_membership_map(self, groupcat_files):
        """
        Build a mapping from particle IDs to subhalo IDs.
        
        Parameters:
        -----------
        groupcat_files : list
            List of group catalog file paths
            
        Returns:
        --------
        dict : {particle_type: {particle_id: subhalo_id}}
        """
        print("\nBuilding subhalo membership map...")
        
        # Particle types: 0=Gas, 1=DM, 4=Stars, 5=BH
        membership_maps = {0: {}, 4: {}}  # Only gas and stars
        
        for file_path in tqdm(groupcat_files, desc="Reading group catalogs"):
            with h5py.File(file_path, 'r') as f:
                
                # Check if Subhalo group exists
                if 'Subhalo' not in f:
                    continue
                
                # Get subhalo lengths (number of particles per subhalo per type)
                if 'SubhaloLenType' not in f['Subhalo']:
                    continue
                
                subhalo_len_type = f['Subhalo/SubhaloLenType'][:]  # Shape: (n_subhalos, 6)
                n_subhalos = len(subhalo_len_type)
                
                # Process particle IDs stored in group catalog
                # The IDs are stored in order, grouped by subhalo
                if 'IDs' in f:
                    ids_group = f['IDs']
                    
                    # For each particle type we care about
                    for part_type in [0, 4]:  # Gas and Stars
                        part_key = f'PartType{part_type}'
                        
                        if part_key in ids_group:
                            particle_ids = ids_group[part_key][:]
                            
                            # Build mapping using subhalo lengths
                            offset = 0
                            for subhalo_id in range(n_subhalos):
                                n_particles = subhalo_len_type[subhalo_id, part_type]
                                
                                if n_particles > 0:
                                    # Particles from offset to offset+n_particles belong to this subhalo
                                    for i in range(offset, offset + n_particles):
                                        if i < len(particle_ids):
                                            pid = particle_ids[i]
                                            membership_maps[part_type][pid] = subhalo_id
                                
                                offset += n_particles
        
        print(f"  Gas particles mapped: {len(membership_maps[0]):,}")
        print(f"  Star particles mapped: {len(membership_maps[4]):,}")
        
        if len(membership_maps[0]) == 0 and len(membership_maps[4]) == 0:
            print("\n  ⚠ WARNING: No particles were mapped to subhalos!")
            print("  This can happen if:")
            print("    - Group catalog files don't contain particle IDs")
            print("    - Only some files were downloaded (test mode)")
            print("  All particles will have SubhaloID = -1 (unassigned)")
        
        return membership_maps
    
    def extract_particle_data_from_file(self, snapshot_file, membership_maps):
        """
        Extract particle data with subhalo IDs from a single snapshot file.
        
        Parameters:
        -----------
        snapshot_file : Path
            Single snapshot file path
        membership_maps : dict
            Mapping from particle IDs to subhalo IDs
            
        Returns:
        --------
        dict : {particle_type: {field_name: numpy_array}}
        """
        data = {
            0: {field: None for field in self.gas_fields + ['SubhaloID']},
            4: {field: None for field in self.star_fields + ['SubhaloID']}
        }
        
        with h5py.File(snapshot_file, 'r') as f:
            
            # Process Gas particles (PartType0)
            if 'PartType0' in f:
                part_group = f['PartType0']
                
                # Read particle IDs first to map to subhalos
                if 'ParticleIDs' in part_group:
                    pids = part_group['ParticleIDs'][:]
                    
                    # Get subhalo IDs for these particles
                    subhalo_ids = np.array([membership_maps[0].get(pid, -1) for pid in pids], dtype=np.int32)
                    
                    # Extract required fields
                    for field in self.gas_fields:
                        if field in part_group:
                            data[0][field] = part_group[field][:]
                    
                    data[0]['SubhaloID'] = subhalo_ids
            
            # Process Star particles (PartType4)
            if 'PartType4' in f:
                part_group = f['PartType4']
                
                # Read particle IDs first to map to subhalos
                if 'ParticleIDs' in part_group:
                    pids = part_group['ParticleIDs'][:]
                    
                    # Get subhalo IDs for these particles
                    subhalo_ids = np.array([membership_maps[4].get(pid, -1) for pid in pids], dtype=np.int32)
                    
                    # Extract required fields
                    for field in self.star_fields:
                        if field in part_group:
                            data[4][field] = part_group[field][:]
                    
                    data[4]['SubhaloID'] = subhalo_ids
        
        return data
    
    def write_output_file(self, data, snapshot_file, chunk_num):
        """
        Write extracted data to new HDF5 file.
        
        Parameters:
        -----------
        data : dict
            Extracted particle data
        snapshot_file : Path
            Original snapshot file (to copy header info)
        chunk_num : int
            Chunk number for output filename
        """
        output_file = self.output_dir / f"forecast_snap_{self.snapshot_num:03d}.{chunk_num}.hdf5"
        print(f"  Writing: {output_file.name}")
        
        with h5py.File(output_file, 'w') as out_f:
            
            # Copy header from snapshot file
            with h5py.File(snapshot_file, 'r') as in_f:
                if 'Header' in in_f:
                    in_f.copy('Header', out_f)
            
            # Write Gas particles (PartType0)
            if data[0]['ParticleIDs'] is not None and len(data[0]['ParticleIDs']) > 0:
                gas_group = out_f.create_group('PartType0')
                for field, arr in data[0].items():
                    if arr is not None and len(arr) > 0:
                        gas_group.create_dataset(field, data=arr, compression='gzip', compression_opts=4)
            
            # Write Star particles (PartType4)
            if data[4]['ParticleIDs'] is not None and len(data[4]['ParticleIDs']) > 0:
                star_group = out_f.create_group('PartType4')
                for field, arr in data[4].items():
                    if arr is not None and len(arr) > 0:
                        star_group.create_dataset(field, data=arr, compression='gzip', compression_opts=4)
            
            # Add metadata
            out_f.attrs['ExtractedForFORECAST'] = True
            out_f.attrs['OriginalSnapshot'] = str(self.snapshot_dir)
            out_f.attrs['OriginalGroupcat'] = str(self.groupcat_dir)
            out_f.attrs['SnapshotNumber'] = self.snapshot_num
            out_f.attrs['ChunkNumber'] = chunk_num
        
        return str(output_file)
    
    def extract(self):
        """
        Main extraction method.
        """
        print(f"\n{'='*60}")
        print(f"EXTRACTING DATA FOR FORECAST")
        print(f"Snapshot: {self.snapshot_num}")
        print(f"{'='*60}\n")
        
        # Step 1: Find files
        snapshot_files = self.find_snapshot_files()
        groupcat_files = self.find_groupcat_files()
        
        if len(snapshot_files) == 0:
            print("Error: No snapshot files found!")
            return None
        
        print(f"Found {len(snapshot_files)} snapshot files to process\n")
        
        # Step 2: Build global subhalo membership map from all group catalogs
        if len(groupcat_files) == 0:
            print("Warning: No group catalog files found. SubhaloID will be -1 for all particles.")
            membership_maps = {0: {}, 4: {}}
        else:
            membership_maps = self.build_subhalo_membership_map(groupcat_files)
        
        # Step 3: Process each snapshot file individually
        print("\nProcessing snapshot files...")
        output_files = []
        
        for snapshot_file in tqdm(snapshot_files, desc="Extracting"):
            # Extract chunk number from filename (e.g., snap_099.0.hdf5 -> 0)
            # Handle both formats: snap_099.0.hdf5 and snap_099.hdf5
            filename = snapshot_file.name
            if '.' in filename.replace('.hdf5', ''):
                # Has chunk number: snap_099.0.hdf5
                chunk_num = int(filename.split('.')[-2])
            else:
                # No chunk number: snap_099.hdf5
                chunk_num = 0
            
            # Extract data from this file
            data = self.extract_particle_data_from_file(snapshot_file, membership_maps)
            
            # Write output file with chunk number
            output_file = self.write_output_file(data, snapshot_file, chunk_num)
            output_files.append(output_file)
        
        print(f"\n{'='*60}")
        print(f"EXTRACTION COMPLETE!")
        print(f"Created {len(output_files)} files")
        print(f"{'='*60}")
        
        return output_files


def main():
    parser = argparse.ArgumentParser(
        description='Extract FORECAST-required fields from TNG snapshots'
    )
    
    parser.add_argument('--snapshot-dir', type=str, required=True,
                       help='Directory containing snapshot files (e.g., TNG100/snapdir_099/)')
    parser.add_argument('--groupcat-dir', type=str, required=True,
                       help='Directory containing group catalog files (e.g., TNG100/groups_099/)')
    parser.add_argument('--output-dir', type=str, required=True,
                       help='Output directory for extracted data')
    parser.add_argument('--snapshot-num', type=int, required=True,
                       help='Snapshot number (e.g., 99)')
    
    args = parser.parse_args()
    
    # Create extractor
    extractor = TNGDataExtractor(
        snapshot_dir=args.snapshot_dir,
        groupcat_dir=args.groupcat_dir,
        output_dir=args.output_dir,
        snapshot_num=args.snapshot_num
    )
    
    # Run extraction
    extractor.extract()


if __name__ == "__main__":
    
    # Example usage (uncomment to run directly):
    
    # extractor = TNGDataExtractor(
    #     snapshot_dir='TNG100/snapdir_099',
    #     groupcat_dir='TNG100/groups_099',
    #     output_dir='TNG100/forecast_data',
    #     snapshot_num=99
    # )
    # extractor.extract()
    
    main()
