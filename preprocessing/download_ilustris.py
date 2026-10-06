#!/usr/bin/env python3
"""
Download TNG Snapshot Data

This script downloads IllustrisTNG snapshot data:
1. Group catalogs (subhalo information)
2. Offsets files (particle-subhalo mapping)
3. Snapshot chunks (particle data)

No extraction or processing is performed - this just downloads the raw data.

Usage:
    # Download all files for snapshot 99
    python process_tng_snapshot.py --api-key YOUR_KEY --snapshot-num 99 --simulation TNG300-3
    
    # Test with first chunk only
    python process_tng_snapshot.py --api-key YOUR_KEY --snapshot-num 99 --simulation TNG300-3 --test
"""

import os

import os

import requests
import h5py
import numpy as np
from pathlib import Path
from tqdm import tqdm
import argparse
import sys
import time
from concurrent.futures import ThreadPoolExecutor, as_completed


class TNGSnapshotProcessor:
    """
    Processes TNG snapshots: downloads and extracts to FORECAST format one chunk at a time.
    """
    
    def __init__(self, api_key, snapshot_num, output_dir, simulation='TNG300-3', temp_dir='TNG100_temp'):
        """
        Initialize processor.
        
        Parameters:
        -----------
        api_key : str
            TNG API key
        snapshot_num : int
            Snapshot number to process
        output_dir : str
            Directory for final FORECAST format files
        simulation : str
            Simulation name (default: TNG300-3)
        temp_dir : str
            Temporary directory for downloads (will be cleaned up)
        """
        self.api_key = api_key
        self.snapshot_num = snapshot_num
        self.simulation = simulation
        self.base_url = 'https://www.tng-project.org/api'
        
        # Setup directories
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
        self.temp_dir = Path(temp_dir)
        self.groupcat_dir = self.temp_dir / f'groups_{snapshot_num:03d}'
        self.offsets_dir = self.temp_dir / f'offsets_{snapshot_num:03d}'
        self.snapshot_dir = self.temp_dir / f'snapdir_{snapshot_num:03d}'
        
        # FORECAST required fields
        self.gas_fields = ['Coordinates', 'Masses', 'Velocities', 'ParticleIDs']
        self.star_fields = ['Coordinates', 'Masses', 'Velocities', 'GFM_StellarFormationTime', 'ParticleIDs']
        
        # Statistics
        self.stats = {
            'chunks_processed': 0,
            'chunks_failed': 0,
            'total_gas_particles': 0,
            'total_star_particles': 0,
            'gas_in_subhalos': 0,
            'stars_in_subhalos': 0
        }
    
    def _make_request(self, endpoint):
        """Make API request with authentication."""
        headers = {'api-key': self.api_key}
        url = f"{self.base_url}/{endpoint}"
        
        response = requests.get(url, headers=headers)
        if response.status_code != 200:
            raise Exception(f"API request failed: {response.status_code} - {response.text}")
        
        return response.json()
    
    def _download_file(self, url, output_path, desc="Downloading", max_retries=5, timeout=500):
        """Download file with progress bar and retry logic."""
        headers = {'api-key': self.api_key}
        
        # Check if file exists and verify its size
        if output_path.exists():
            try:
                # Get remote file size
                response = requests.head(url, headers=headers, timeout=30)
                remote_size = int(response.headers.get('content-length', 0))
                local_size = output_path.stat().st_size
                
                # If sizes match, skip download
                if remote_size > 0 and local_size > 0.99*remote_size and local_size < 1.01*remote_size:
                    print(f"  ✓ Already exists (verified {local_size:,} bytes): {output_path.name}")
                    return True
                else:
                    # Size mismatch - incomplete download, remove and re-download
                    print(f"  ⚠ Incomplete file detected: {output_path.name} ({local_size:,}/{remote_size:,} bytes)")
                    output_path.unlink()
                    print(f"  ↻ Removed incomplete file, will re-download...")
            except Exception as e:
                # If we can't verify, try to remove and re-download
                print(f"  ⚠ Could not verify file size: {e}")
                print(f"  ↻ Will re-download to be safe...")
                try:
                    output_path.unlink()
                except:
                    pass
        
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        for attempt in range(max_retries):
            try:
                response = requests.get(url, headers=headers, stream=True, timeout=timeout)
                response.raise_for_status()
                
                total_size = int(response.headers.get('content-length', 0))
                
                with open(output_path, 'wb') as f, tqdm(
                    total=total_size,
                    unit='B',
                    unit_scale=True,
                    desc=f"  {desc}",
                    leave=False
                ) as pbar:
                    for chunk in response.iter_content(chunk_size=8192):
                        if chunk:
                            f.write(chunk)
                            pbar.update(len(chunk))
                
                return True
                
            except Exception as e:
                if output_path.exists():
                    output_path.unlink()
                
                if attempt < max_retries - 1:
                    wait_time = (attempt + 1) * 5  # 5, 10, 15 seconds
                    print(f"  ⚠ Download failed (attempt {attempt + 1}/{max_retries}): {e}")
                    print(f"    Retrying in {wait_time} seconds...")
                    time.sleep(wait_time)
                else:
                    print(f"  ✗ Download failed after {max_retries} attempts: {e}")
                    return False
        
        return False
    
    def download_group_catalogs(self):
        """
        Download all group catalog files for the snapshot.
        
        Returns:
        --------
        list : List of downloaded group catalog file paths
        """
        print(f"\n{'='*60}")
        print(f"STEP 1: DOWNLOADING GROUP CATALOGS")
        print(f"Snapshot: {self.snapshot_num}")
        print(f"{'='*60}\n")
        
        # Get list of group catalog files from API
        endpoint = f"{self.simulation}/files/groupcat-{self.snapshot_num}/"
        print(f"Querying: {endpoint}")
        
        try:
            response = self._make_request(endpoint)
            
            if 'files' in response:
                file_urls = response['files']
            elif isinstance(response, list):
                file_urls = response
            else:
                print(f"Unexpected API response format: {response}")
                return []
            
            print(f"Found {len(file_urls)} group catalog files\n")
            
            # Check which files already exist
            existing_files = set()
            if self.groupcat_dir.exists():
                existing_files = {f.name for f in self.groupcat_dir.glob('*.hdf5')}
                if len(existing_files) > 0:
                    print(f"Found {len(existing_files)} existing files")
            
            # Determine which files need to be downloaded
            files_to_download = []
            expected_filenames = set()
            
            for file_url in file_urls:
                filename = file_url.split('/')[-1]
                expected_filenames.add(filename)
                if filename not in existing_files:
                    files_to_download.append((file_url, filename))
            
            # Check if we have all expected files
            if len(existing_files) == len(expected_filenames) and existing_files == expected_filenames:
                print(f"✓ All {len(expected_filenames)} group catalog files already downloaded")
                return sorted(self.groupcat_dir.glob('*.hdf5'))
            
            # Download missing files
            if len(files_to_download) > 0:
                print(f"Downloading {len(files_to_download)} missing files...\n")
                
                failed_downloads = []
                for file_url, filename in tqdm(files_to_download, desc="Downloading group catalogs"):
                    output_path = self.groupcat_dir / filename
                    
                    if not self._download_file(file_url, output_path, filename):
                        failed_downloads.append(filename)
                
                if len(failed_downloads) > 0:
                    print(f"\n⚠ Warning: {len(failed_downloads)} files failed to download:")
                    for fname in failed_downloads[:5]:  # Show first 5
                        print(f"  - {fname}")
                    if len(failed_downloads) > 5:
                        print(f"  ... and {len(failed_downloads) - 5} more")
            
            # Return all successfully downloaded files
            downloaded_files = sorted(self.groupcat_dir.glob('*.hdf5'))
            print(f"\n✓ Have {len(downloaded_files)} of {len(expected_filenames)} group catalog files")
            
            if len(downloaded_files) < len(expected_filenames):
                print(f"⚠ Warning: Missing {len(expected_filenames) - len(downloaded_files)} files")
                print(f"  Subhalo assignment may be incomplete")
            
            return downloaded_files
            
        except Exception as e:
            print(f"✗ Failed to download group catalogs: {e}")
            return []
    
    def download_offsets_files(self):
        """
        Download all offsets files for the snapshot.
        
        Returns:
        --------
        list : List of downloaded offsets file paths
        """
        print(f"\n{'='*60}")
        print(f"STEP 2: DOWNLOADING OFFSETS FILES")
        print(f"Snapshot: {self.snapshot_num}")
        print(f"{'='*60}\n")
        
        # Get list of offsets files from API
        endpoint = f"{self.simulation}/files/offsets-{self.snapshot_num}/"
        print(f"Querying: {endpoint}")
        
        try:
            response = self._make_request(endpoint)
            
            if 'files' in response:
                file_urls = response['files']
            elif isinstance(response, list):
                file_urls = response
            else:
                print(f"Unexpected API response format: {response}")
                return []
            
            print(f"Found {len(file_urls)} offsets files\n")
            
            # Check which files already exist
            existing_files = set()
            if self.offsets_dir.exists():
                existing_files = {f.name for f in self.offsets_dir.glob('*.hdf5')}
                if len(existing_files) > 0:
                    print(f"Found {len(existing_files)} existing files")
            
            # Determine which files need to be downloaded
            files_to_download = []
            expected_filenames = set()
            
            for file_url in file_urls:
                filename = file_url.split('/')[-1]
                expected_filenames.add(filename)
                if filename not in existing_files:
                    files_to_download.append((file_url, filename))
            
            # Check if we have all expected files
            if len(existing_files) == len(expected_filenames) and existing_files == expected_filenames:
                print(f"✓ All {len(expected_filenames)} offsets files already downloaded")
                return sorted(self.offsets_dir.glob('*.hdf5'))
            
            # Download missing files
            if len(files_to_download) > 0:
                print(f"Downloading {len(files_to_download)} missing files...\n")
                
                failed_downloads = []
                for file_url, filename in tqdm(files_to_download, desc="Downloading offsets files"):
                    output_path = self.offsets_dir / filename
                    
                    if not self._download_file(file_url, output_path, filename):
                        failed_downloads.append(filename)
                
                if len(failed_downloads) > 0:
                    print(f"\n⚠ Warning: {len(failed_downloads)} files failed to download:")
                    for fname in failed_downloads[:5]:  # Show first 5
                        print(f"  - {fname}")
                    if len(failed_downloads) > 5:
                        print(f"  ... and {len(failed_downloads) - 5} more")
            
            # Return all successfully downloaded files
            downloaded_files = sorted(self.offsets_dir.glob('*.hdf5'))
            print(f"\n✓ Have {len(downloaded_files)} of {len(expected_filenames)} offsets files")
            
            if len(downloaded_files) < len(expected_filenames):
                print(f"⚠ Warning: Missing {len(expected_filenames) - len(downloaded_files)} files")
                print(f"  Subhalo assignment may be incomplete")
            
            return downloaded_files
            
        except Exception as e:
            print(f"✗ Failed to download offsets files: {e}")
            print(f"  Note: Not all simulations provide offsets files")
            return []
    
    def build_subhalo_membership_map_from_offsets(self, offsets_files, groupcat_files):
        """
        Build subhalo membership map using offsets files.
        
        The TNG offsets files contain information about where particles for each
        subhalo are located in the snapshot files. The format is:
        - Subhalo/SnapByType[subhalo_id, part_type] = starting GLOBAL offset in snapshot
        - Group catalog SubhaloLenType[subhalo_id, part_type] = number of particles
        
        This builds a global mapping that will be converted to chunk-local indices
        during extraction.
        
        Parameters:
        -----------
        offsets_files : list
            List of offsets file paths
        groupcat_files : list
            List of group catalog file paths
            
        Returns:
        --------
        dict : {'offsets': {particle_type: {global_index: subhalo_id}}, 
                'num_chunks': int}
        """
        print(f"\n{'='*60}")
        print(f"BUILDING SUBHALO MEMBERSHIP MAP FROM OFFSETS")
        print(f"{'='*60}\n")
        
        if len(offsets_files) == 0:
            print("✗ No offsets files available!")
            return {}
        
        print("Reading offsets and group catalogs...")
        
        # Load offsets file (usually just one file for the entire snapshot)
        offsets_path = offsets_files[0]
        
        with h5py.File(offsets_path, 'r') as of:
            if 'Subhalo' not in of or 'SnapByType' not in of['Subhalo']:
                print("✗ Offsets file missing Subhalo/SnapByType dataset!")
                return {}
            
            # Shape: (n_subhalos, 6) - GLOBAL offsets for each subhalo and particle type
            subhalo_offsets = of['Subhalo/SnapByType'][:]
            n_subhalos = len(subhalo_offsets)
            print(f"  Found offsets for {n_subhalos:,} subhalos")
        
        # Load subhalo lengths from group catalogs
        print("  Reading subhalo lengths...")
        all_subhalo_lengths = []
        
        for groupcat_path in groupcat_files:
            with h5py.File(groupcat_path, 'r') as gf:
                if 'Subhalo' in gf and 'SubhaloLenType' in gf['Subhalo']:
                    subhalo_lens = gf['Subhalo/SubhaloLenType'][:]
                    all_subhalo_lengths.append(subhalo_lens)
        
        if len(all_subhalo_lengths) == 0:
            print("✗ No subhalo lengths found in group catalogs!")
            return {}
        
        # Concatenate all subhalo lengths
        subhalo_lengths = np.vstack(all_subhalo_lengths)
        print(f"  Loaded lengths for {len(subhalo_lengths):,} subhalos")
        
        # Build mapping: global_particle_index -> subhalo_id
        # These are GLOBAL indices across the entire simulation
        particle_to_subhalo = {0: {}, 4: {}}  # Gas and Stars
        
        print("  Building global particle->subhalo mapping...")
        for subhalo_id in tqdm(range(min(n_subhalos, len(subhalo_lengths))), desc="Processing subhalos"):
            for part_type in [0, 4]:  # Gas and Stars
                offset = subhalo_offsets[subhalo_id, part_type]
                length = subhalo_lengths[subhalo_id, part_type]
                
                if length > 0:
                    # Map GLOBAL particle indices to this subhalo
                    for particle_idx in range(offset, offset + length):
                        particle_to_subhalo[part_type][particle_idx] = subhalo_id
        
        total_gas = len(particle_to_subhalo[0])
        total_stars = len(particle_to_subhalo[4])
        
        print(f"\nGlobal offset-based mapping built:")
        print(f"  Gas particles mapped: {total_gas:,}")
        print(f"  Star particles mapped: {total_stars:,}")
        print(f"\n  Note: These are GLOBAL indices across all chunks")
        print(f"        Will be converted to chunk-local indices during extraction")
        
        return {
            'type': 'offsets',
            'offsets': particle_to_subhalo
        }
    
    def build_subhalo_membership_map(self, groupcat_files):
        """
        Build global subhalo membership map from group catalogs.
        
        Parameters:
        -----------
        groupcat_files : list
            List of group catalog file paths
            
        Returns:
        --------
        dict : {particle_type: {particle_id: subhalo_id}}
        """
        print(f"\n{'='*60}")
        print(f"BUILDING SUBHALO MEMBERSHIP MAP")
        print(f"{'='*60}\n")
        
        membership_maps = {0: {}, 4: {}}  # Gas and Stars
        
        for file_path in tqdm(groupcat_files, desc="Processing group catalogs"):
            with h5py.File(file_path, 'r') as f:
                
                if 'Subhalo' not in f or 'SubhaloLenType' not in f['Subhalo']:
                    continue
                
                subhalo_len_type = f['Subhalo/SubhaloLenType'][:]
                n_subhalos = len(subhalo_len_type)
                
                if 'IDs' not in f:
                    continue
                
                ids_group = f['IDs']
                
                for part_type in [0, 4]:  # Gas and Stars
                    part_key = f'PartType{part_type}'
                    
                    if part_key in ids_group:
                        particle_ids = ids_group[part_key][:]
                        
                        offset = 0
                        for subhalo_id in range(n_subhalos):
                            n_particles = subhalo_len_type[subhalo_id, part_type]
                            
                            if n_particles > 0:
                                for i in range(offset, offset + n_particles):
                                    if i < len(particle_ids):
                                        pid = particle_ids[i]
                                        membership_maps[part_type][pid] = subhalo_id
                            
                            offset += n_particles
        
        print(f"\nMembership map built:")
        print(f"  Gas particles mapped: {len(membership_maps[0]):,}")
        print(f"  Star particles mapped: {len(membership_maps[4]):,}")
        
        return membership_maps
    
    def download_snapshot_chunk(self, chunk_num):
        """
        Download a single snapshot chunk.
        
        Parameters:
        -----------
        chunk_num : int
            Chunk number to download
            
        Returns:
        --------
        Path or None : Path to downloaded file, or None if failed
        """
        # Get list of snapshot files
        endpoint = f"{self.simulation}/files/snapshot-{self.snapshot_num}/"
        
        try:
            response = self._make_request(endpoint)
            
            if 'files' in response:
                file_urls = response['files']
            elif isinstance(response, list):
                file_urls = response
            else:
                print(f"Unexpected API response: {response}")
                return None
            
            # Find the specific chunk
            # Try different filename formats (TNG100-1 uses snap_XXX, TNG300-3 uses snapshot-XXX)
            possible_filenames = [
                f"snap_{self.snapshot_num:03d}.{chunk_num}.hdf5",
                f"snapshot-{self.snapshot_num}.{chunk_num}.hdf5"
            ]
            
            chunk_url = None
            chunk_filename = None
            
            for filename in possible_filenames:
                for url in file_urls:
                    if filename in url:
                        chunk_url = url
                        chunk_filename = filename
                        break
                if chunk_url:
                    break
            
            if chunk_url is None:
                print(f"  ✗ Chunk {chunk_num} not found in file list")
                print(f"    Tried: {', '.join(possible_filenames)}")
                return None
            
            # Download the chunk
            output_path = self.snapshot_dir / chunk_filename
            
            if self._download_file(chunk_url, output_path, chunk_filename):
                return output_path
            else:
                return None
                
        except Exception as e:
            print(f"  ✗ Failed to download chunk {chunk_num}: {e}")
            return None
    
    def get_chunk_offsets(self):
        """
        Get cumulative particle counts for each chunk to understand global offsets.
        
        Returns:
        --------
        dict : {particle_type: [cumulative counts per chunk]}
        """
        # Query for all chunk files
        endpoint = f"{self.simulation}/files/snapshot-{self.snapshot_num}/"
        
        try:
            response = self._make_request(endpoint)
            file_urls = response.get('files', response if isinstance(response, list) else [])
            
            # Sort chunk URLs
            patterns = [
                f"snap_{self.snapshot_num:03d}.",
                f"snapshot-{self.snapshot_num}."
            ]
            chunk_urls = []
            for pattern in patterns:
                urls = sorted([url for url in file_urls if pattern in url and url.endswith('.hdf5')])
                if urls:
                    chunk_urls = urls
                    break
            
            # Read headers from each chunk
            chunk_offsets = {0: [0], 4: [0]}  # Cumulative offsets
            
            for i, url in enumerate(chunk_urls):
                # Download header only if needed, or use existing file
                chunk_filename = url.split('/')[-1]
                chunk_path = self.snapshot_dir / chunk_filename
                
                if chunk_path.exists():
                    with h5py.File(chunk_path, 'r') as f:
                        header = f['Header'].attrs
                        for part_type in [0, 4]:
                            n_part = header[f'NumPart_ThisFile'][part_type]
                            chunk_offsets[part_type].append(chunk_offsets[part_type][-1] + n_part)
            
            return chunk_offsets
            
        except Exception as e:
            print(f"Warning: Could not determine chunk offsets: {e}")
            return {0: [0], 4: [0]}
    
    def extract_chunk_data(self, chunk_path, membership_maps, chunk_num, chunk_offsets=None):
        """
        Extract FORECAST-required fields from a single chunk.
        
        Parameters:
        -----------
        chunk_path : Path
            Path to snapshot chunk file
        membership_maps : dict
            Either:
            - {'type': 'offsets', 'offsets': {particle_type: {global_index: subhalo_id}}}
            - {particle_type: {particle_id: subhalo_id}} (legacy particle ID method)
        chunk_num : int
            Chunk number being processed
        chunk_offsets : dict, optional
            {particle_type: [cumulative counts]} for global-to-local index conversion
            
        Returns:
        --------
        dict : Extracted data with subhalo IDs
        """
        data = {
            0: {field: None for field in self.gas_fields + ['SubhaloID']},
            4: {field: None for field in self.star_fields + ['SubhaloID']}
        }
        
        # Detect mapping type
        uses_offsets = isinstance(membership_maps, dict) and membership_maps.get('type') == 'offsets'
        
        with h5py.File(chunk_path, 'r') as f:
            
            # Process Gas particles (PartType0)
            if 'PartType0' in f:
                part_group = f['PartType0']
                
                if 'ParticleIDs' in part_group:
                    pids = part_group['ParticleIDs'][:]
                    n_particles = len(pids)
                    
                    # Determine subhalo IDs based on mapping type
                    if uses_offsets and 'offsets' in membership_maps:
                        # Use offset-based mapping (convert global to local indices)
                        global_offsets = membership_maps['offsets']
                        
                        # Get global offset for this chunk
                        if chunk_offsets and 0 in chunk_offsets and chunk_num < len(chunk_offsets[0]) - 1:
                            chunk_start = chunk_offsets[0][chunk_num]
                            subhalo_ids = np.full(n_particles, -1, dtype=np.int32)
                            
                            # Map each particle using global index
                            for local_idx in range(n_particles):
                                global_idx = chunk_start + local_idx
                                if global_idx in global_offsets[0]:
                                    subhalo_ids[local_idx] = global_offsets[0][global_idx]
                        else:
                            subhalo_ids = np.full(n_particles, -1, dtype=np.int32)
                    
                    elif not uses_offsets and 0 in membership_maps:
                        # Use particle ID-based mapping
                        subhalo_ids = np.array([membership_maps[0].get(pid, -1) for pid in pids], dtype=np.int32)
                    else:
                        # No mapping available
                        subhalo_ids = np.full(n_particles, -1, dtype=np.int32)
                    
                    for field in self.gas_fields:
                        if field in part_group:
                            data[0][field] = part_group[field][:]
                    
                    data[0]['SubhaloID'] = subhalo_ids
            
            # Process Star particles (PartType4)
            if 'PartType4' in f:
                part_group = f['PartType4']
                
                if 'ParticleIDs' in part_group:
                    pids = part_group['ParticleIDs'][:]
                    n_particles = len(pids)
                    
                    # Determine subhalo IDs based on mapping type
                    if uses_offsets and 'offsets' in membership_maps:
                        # Use offset-based mapping (convert global to local indices)
                        global_offsets = membership_maps['offsets']
                        
                        # Get global offset for this chunk
                        if chunk_offsets and 4 in chunk_offsets and chunk_num < len(chunk_offsets[4]) - 1:
                            chunk_start = chunk_offsets[4][chunk_num]
                            subhalo_ids = np.full(n_particles, -1, dtype=np.int32)
                            
                            # Map each particle using global index
                            for local_idx in range(n_particles):
                                global_idx = chunk_start + local_idx
                                if global_idx in global_offsets[4]:
                                    subhalo_ids[local_idx] = global_offsets[4][global_idx]
                        else:
                            subhalo_ids = np.full(n_particles, -1, dtype=np.int32)
                    
                    elif not uses_offsets and 4 in membership_maps:
                        # Use particle ID-based mapping
                        subhalo_ids = np.array([membership_maps[4].get(pid, -1) for pid in pids], dtype=np.int32)
                    else:
                        # No mapping available
                        subhalo_ids = np.full(n_particles, -1, dtype=np.int32)
                    
                    for field in self.star_fields:
                        if field in part_group:
                            data[4][field] = part_group[field][:]
                    
                    data[4]['SubhaloID'] = subhalo_ids
        
        return data
    
    def verify_subhalo_assignment(self, data, chunk_num):
        """
        Verify that subhalo IDs were assigned correctly.
        
        Parameters:
        -----------
        data : dict
            Extracted particle data
        chunk_num : int
            Chunk number being processed
            
        Returns:
        --------
        bool : True if verification passed, False otherwise
        """
        print(f"    Verifying subhalo assignments...")
        
        verification_passed = True
        
        # Check Gas particles
        if data[0]['SubhaloID'] is not None:
            gas_subhalo_ids = data[0]['SubhaloID']
            n_gas = len(gas_subhalo_ids)
            n_gas_in_subhalos = np.sum(gas_subhalo_ids >= 0)
            
            self.stats['total_gas_particles'] += n_gas
            self.stats['gas_in_subhalos'] += n_gas_in_subhalos
            
            print(f"      Gas: {n_gas:,} particles, {n_gas_in_subhalos:,} in subhalos ({100*n_gas_in_subhalos/n_gas:.1f}%)")
        
        # Check Star particles
        if data[4]['SubhaloID'] is not None:
            star_subhalo_ids = data[4]['SubhaloID']
            n_stars = len(star_subhalo_ids)
            n_stars_in_subhalos = np.sum(star_subhalo_ids >= 0)
            
            self.stats['total_star_particles'] += n_stars
            self.stats['stars_in_subhalos'] += n_stars_in_subhalos
            
            print(f"      Stars: {n_stars:,} particles, {n_stars_in_subhalos:,} in subhalos ({100*n_stars_in_subhalos/n_stars:.1f}%)")
        
        # Verification checks
        checks = []
        
        # Check 1: SubhaloID field exists
        if data[0]['SubhaloID'] is not None or data[4]['SubhaloID'] is not None:
            checks.append(("SubhaloID field exists", True))
        else:
            checks.append(("SubhaloID field exists", False))
            verification_passed = False
        
        # Check 2: SubhaloID has correct dtype
        if data[0]['SubhaloID'] is not None:
            if data[0]['SubhaloID'].dtype == np.int32:
                checks.append(("Gas SubhaloID dtype is int32", True))
            else:
                checks.append(("Gas SubhaloID dtype is int32", False))
                verification_passed = False
        
        if data[4]['SubhaloID'] is not None:
            if data[4]['SubhaloID'].dtype == np.int32:
                checks.append(("Star SubhaloID dtype is int32", True))
            else:
                checks.append(("Star SubhaloID dtype is int32", False))
                verification_passed = False
        
        # Check 3: SubhaloID matches ParticleIDs length
        if data[0]['SubhaloID'] is not None and data[0]['ParticleIDs'] is not None:
            if len(data[0]['SubhaloID']) == len(data[0]['ParticleIDs']):
                checks.append(("Gas SubhaloID length matches ParticleIDs", True))
            else:
                checks.append(("Gas SubhaloID length matches ParticleIDs", False))
                verification_passed = False
        
        if data[4]['SubhaloID'] is not None and data[4]['ParticleIDs'] is not None:
            if len(data[4]['SubhaloID']) == len(data[4]['ParticleIDs']):
                checks.append(("Star SubhaloID length matches ParticleIDs", True))
            else:
                checks.append(("Star SubhaloID length matches ParticleIDs", False))
                verification_passed = False
        
        # Print verification summary
        print(f"    Verification checks:")
        for check_name, passed in checks:
            status = "✓" if passed else "✗"
            print(f"      {status} {check_name}")
        
        return verification_passed
    
    def write_forecast_file(self, data, chunk_num, chunk_path):
        """
        Write extracted data to FORECAST format HDF5 file.
        
        Parameters:
        -----------
        data : dict
            Extracted particle data
        chunk_num : int
            Chunk number
        chunk_path : Path
            Original chunk path (for header)
            
        Returns:
        --------
        Path : Output file path
        """
        output_file = self.output_dir / f"forecast_snap_{self.snapshot_num:03d}.{chunk_num}.hdf5"
        
        with h5py.File(output_file, 'w') as out_f:
            
            # Copy header from original chunk
            with h5py.File(chunk_path, 'r') as in_f:
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
            out_f.attrs['OriginalSnapshot'] = str(chunk_path)
            out_f.attrs['SnapshotNumber'] = self.snapshot_num
            out_f.attrs['ChunkNumber'] = chunk_num
            out_f.attrs['ProcessedDate'] = time.strftime('%Y-%m-%d %H:%M:%S')
        
        # Get file size for reporting
        file_size_mb = output_file.stat().st_size / (1024**2)
        print(f"    Written: {output_file.name} ({file_size_mb:.1f} MB)")
        
        return output_file
    
    def process_chunk(self, chunk_num, membership_maps):
        """
        Process a single chunk: download, extract, verify, cleanup.
        
        Parameters:
        -----------
        chunk_num : int
            Chunk number to process
        membership_maps : dict
            Global subhalo membership map
            
        Returns:
        --------
        bool : True if successful, False otherwise
        """
        print(f"\n  Chunk {chunk_num}:")
        
        try:
            # Step 1: Download chunk
            print(f"    Downloading chunk {chunk_num}...")
            chunk_path = self.download_snapshot_chunk(chunk_num)
            
            if chunk_path is None:
                print(f"    ✗ Download failed")
                self.stats['chunks_failed'] += 1
                return False
            
            original_size_mb = chunk_path.stat().st_size / (1024**2)
            print(f"    Downloaded: {chunk_path.name} ({original_size_mb:.1f} MB)")
            
            # Step 2: Extract data
            print(f"    Extracting FORECAST fields...")
            data = self.extract_chunk_data(chunk_path, membership_maps, chunk_num)
            
            # Step 3: Verify subhalo assignment
            verification_passed = self.verify_subhalo_assignment(data, chunk_num)
            
            if not verification_passed:
                print(f"    ⚠ Verification warnings detected")
            
            # Step 4: Write output file
            output_file = self.write_forecast_file(data, chunk_num, chunk_path)
            output_size_mb = output_file.stat().st_size / (1024**2)
            
            compression_ratio = 100 * (1 - output_size_mb / original_size_mb)
            print(f"    Size reduction: {original_size_mb:.1f} MB → {output_size_mb:.1f} MB ({compression_ratio:.1f}% saved)")
            
            # Step 5: Cleanup original chunk
            print(f"    Removing original chunk...")
            chunk_path.unlink()
            
            self.stats['chunks_processed'] += 1
            print(f"    ✓ Chunk {chunk_num} completed")
            
            return True
            
        except Exception as e:
            print(f"    ✗ Error processing chunk {chunk_num}: {e}")
            self.stats['chunks_failed'] += 1
            return False
    
    def get_total_chunks(self):
        """
        Query TNG API to get total number of chunks for the snapshot.
        
        Returns:
        --------
        int : Number of chunks
        """
        endpoint = f"{self.simulation}/files/snapshot-{self.snapshot_num}/"
        
        try:
            response = self._make_request(endpoint)
            
            if 'files' in response:
                file_urls = response['files']
            elif isinstance(response, list):
                file_urls = response
            else:
                return 0
            
            # Count snapshot chunks (handle both naming conventions)
            # TNG100-1: snap_099.X.hdf5, TNG300-3: snapshot-99.X.hdf5
            patterns = [
                f"snap_{self.snapshot_num:03d}.",
                f"snapshot-{self.snapshot_num}."
            ]
            
            chunks = []
            for pattern in patterns:
                chunks.extend([url for url in file_urls if pattern in url and url.endswith('.hdf5')])
            
            return len(chunks)
            
        except Exception as e:
            print(f"Error getting chunk count: {e}")
            return 0
    
    def download_all_snapshot_chunks(self, test_mode=False):
        """
        Download all snapshot chunks.
        
        Parameters:
        -----------
        test_mode : bool
            If True, only download first chunk
            
        Returns:
        --------
        list : List of downloaded chunk paths
        """
        print(f"\n{'='*60}")
        print(f"STEP 3: DOWNLOADING SNAPSHOT CHUNKS")
        print(f"Snapshot: {self.snapshot_num}")
        print(f"{'='*60}\n")
        
        # Get total chunks
        total_chunks = self.get_total_chunks()
        
        if total_chunks == 0:
            print("✗ Could not determine number of chunks")
            return []
        
        if test_mode:
            chunks_to_download = [0]
            print(f"Downloading 1 chunk (TEST MODE)\n")
        else:
            chunks_to_download = range(total_chunks)
            print(f"Downloading {total_chunks} chunks\n")
        
        downloaded_chunks = []
        failed_chunks = []
        
        for chunk_num in tqdm(chunks_to_download, desc="Downloading snapshot chunks"):
            chunk_path = self.download_snapshot_chunk(chunk_num)
            
            if chunk_path:
                downloaded_chunks.append(chunk_path)
            else:
                failed_chunks.append(chunk_num)
        
        print(f"\n✓ Downloaded {len(downloaded_chunks)} of {len(chunks_to_download)} chunks")
        
        if len(failed_chunks) > 0:
            print(f"⚠ Warning: {len(failed_chunks)} chunks failed to download:")
            for chunk_num in failed_chunks[:5]:
                print(f"  - Chunk {chunk_num}")
            if len(failed_chunks) > 5:
                print(f"  ... and {len(failed_chunks) - 5} more")
        
        return downloaded_chunks
    
    def process(self, test_mode=False, max_retry_attempts=5):
        """
        Main download pipeline - downloads all required data without processing.
        Includes retry logic with exponential backoff for network errors.
        
        Parameters:
        -----------
        test_mode : bool
            If True, only download first chunk
        max_retry_attempts : int
            Maximum number of retry attempts for each download phase
            
        Returns:
        --------
        bool : True if successful, False otherwise
        """
        print(f"\n{'='*60}")
        print(f"TNG DATA DOWNLOADER")
        print(f"Simulation: {self.simulation}")
        print(f"Snapshot: {self.snapshot_num}")
        print(f"Mode: {'TEST (first chunk only)' if test_mode else 'FULL'}")
        print(f"Max retry attempts: {max_retry_attempts}")
        print(f"{'='*60}")
        print(f"\nThis will download:")
        print(f"  1. Group catalogs (for subhalo information)")
        print(f"  2. Offsets files (for particle-subhalo matching)")
        print(f"  3. Snapshot chunks (particle data)")
        print(f"\nNo extraction or matching will be performed yet.\n")
        
        start_time = time.time()
        
        # Step 1: Download group catalogs with retry logic
        print(f"\n{'='*60}")
        print(f"STEP 1: DOWNLOADING GROUP CATALOGS")
        print(f"{'='*60}\n")
        
        groupcat_files = []
        for attempt in range(1, max_retry_attempts + 1):
            try:
                print(f"Attempt {attempt}/{max_retry_attempts}...")
                groupcat_files = self.download_group_catalogs()
                
                if len(groupcat_files) > 0:
                    print(f"✓ Group catalogs downloaded successfully")
                    break
                else:
                    if attempt < max_retry_attempts:
                        wait_time = min(60 * attempt, 300)  # Cap at 5 minutes
                        print(f"⚠ No group catalogs downloaded. Retrying in {wait_time} seconds...")
                        time.sleep(wait_time)
                    
            except (requests.ConnectionError, requests.Timeout, ConnectionResetError, BrokenPipeError) as e:
                print(f"✗ Connection error: {type(e).__name__}")
                if attempt < max_retry_attempts:
                    wait_time = min(60 * attempt, 300)  # Exponential backoff, capped at 5 min
                    print(f"⚠ Network disconnection detected. Retrying in {wait_time} seconds...")
                    time.sleep(wait_time)
                else:
                    print(f"✗ Failed after {max_retry_attempts} attempts to download group catalogs")
                    return False
                    
            except Exception as e:
                print(f"✗ Error during group catalogs download: {e}")
                if attempt < max_retry_attempts:
                    wait_time = min(60 * attempt, 300)
                    print(f"⚠ Retrying in {wait_time} seconds...")
                    time.sleep(wait_time)
                else:
                    print(f"✗ Failed after {max_retry_attempts} attempts to download group catalogs")
                    return False
        
        if len(groupcat_files) == 0:
            print("\n✗ Failed to download group catalogs after all retry attempts. Aborting.")
            return False
        
        # Step 2: Download offsets files with retry logic
        print(f"\n{'='*60}")
        print(f"STEP 2: DOWNLOADING OFFSETS FILES")
        print(f"{'='*60}\n")
        
        offsets_files = []
        for attempt in range(1, max_retry_attempts + 1):
            try:
                print(f"Attempt {attempt}/{max_retry_attempts}...")
                offsets_files = self.download_offsets_files()
                
                if len(offsets_files) > 0:
                    print(f"✓ Offsets files downloaded successfully")
                    break
                else:
                    if attempt < max_retry_attempts:
                        print(f"⚠ No offsets files downloaded. Retrying in 30 seconds...")
                        time.sleep(30)
                        
            except (requests.ConnectionError, requests.Timeout, ConnectionResetError, BrokenPipeError) as e:
                print(f"✗ Connection error: {type(e).__name__}")
                if attempt < max_retry_attempts:
                    wait_time = min(60 * attempt, 300)
                    print(f"⚠ Network disconnection detected. Retrying in {wait_time} seconds...")
                    time.sleep(wait_time)
                else:
                    print(f"⚠ Warning: Failed to download offsets files after {max_retry_attempts} attempts")
                    print("  Subhalo matching may require alternative methods")
                    
            except Exception as e:
                print(f"✗ Error during offsets download: {e}")
                if attempt < max_retry_attempts:
                    wait_time = min(60 * attempt, 300)
                    print(f"⚠ Retrying in {wait_time} seconds...")
                    time.sleep(wait_time)
                else:
                    print(f"⚠ Warning: Failed to download offsets files after {max_retry_attempts} attempts")
                    print("  Subhalo matching may require alternative methods")
        
        if len(offsets_files) == 0:
            print("\n⚠ Warning: No offsets files could be downloaded")
            print("  Continuing with snapshot download - subhalo matching may require alternative methods")
        
        # Step 3: Download all snapshot chunks with retry logic
        print(f"\n{'='*60}")
        print(f"STEP 3: DOWNLOADING SNAPSHOT CHUNKS")
        print(f"{'='*60}\n")
        
        snapshot_chunks = []
        for attempt in range(1, max_retry_attempts + 1):
            try:
                print(f"Attempt {attempt}/{max_retry_attempts}...")
                snapshot_chunks = self.download_all_snapshot_chunks(test_mode=test_mode)
                
                if len(snapshot_chunks) > 0:
                    print(f"✓ Snapshot chunks downloaded successfully")
                    break
                else:
                    if attempt < max_retry_attempts:
                        wait_time = min(60 * attempt, 300)
                        print(f"⚠ No snapshot chunks downloaded. Retrying in {wait_time} seconds...")
                        time.sleep(wait_time)
                    
            except (requests.ConnectionError, requests.Timeout, ConnectionResetError, BrokenPipeError) as e:
                print(f"✗ Connection error: {type(e).__name__}")
                if attempt < max_retry_attempts:
                    wait_time = min(60 * attempt, 300)
                    print(f"⚠ Network disconnection detected. Retrying in {wait_time} seconds...")
                    time.sleep(wait_time)
                else:
                    print(f"✗ Failed after {max_retry_attempts} attempts to download snapshot chunks")
                    return False
                    
            except Exception as e:
                print(f"✗ Error during snapshot download: {e}")
                if attempt < max_retry_attempts:
                    wait_time = min(60 * attempt, 300)
                    print(f"⚠ Retrying in {wait_time} seconds...")
                    time.sleep(wait_time)
                else:
                    print(f"✗ Failed after {max_retry_attempts} attempts to download snapshot chunks")
                    return False
        
        if len(snapshot_chunks) == 0:
            print("\n✗ Failed to download snapshot chunks after all retry attempts. Aborting.")
            return False
        
        elapsed_time = time.time() - start_time
        
        # Print final summary
        print(f"\n{'='*60}")
        print(f"DOWNLOAD COMPLETE")
        print(f"{'='*60}")
        print(f"Time elapsed: {elapsed_time/60:.1f} minutes")
        print(f"\nDownloaded files:")
        print(f"  Group catalogs: {len(groupcat_files)} files")
        print(f"  Offsets files: {len(offsets_files)} files")
        print(f"  Snapshot chunks: {len(snapshot_chunks)} files")
        print(f"\nData location:")
        print(f"  Group catalogs: {self.groupcat_dir}")
        print(f"  Offsets: {self.offsets_dir}")
        print(f"  Snapshots: {self.snapshot_dir}")
        print(f"\nNext steps:")
        print(f"  - Use illustris_python to match particles to subhalos")
        print(f"  - Extract FORECAST-required fields from snapshots")
        print(f"  - Compress data to save space")
        print(f"\n{'='*60}\n")
        
        return True


def process_single_snapshot(simulation, snapshot_num, api_key, output_path):
    """
    Process a single snapshot.
    
    Parameters:
    -----------
    simulation : str
        Simulation name
    snapshot_num : int
        Snapshot number
    api_key : str
        TNG API key
    output_path : str
        Output directory path
        
    Returns:
    --------
    tuple : (simulation, snapshot_num, success)
    """
    try:
        processor = TNGSnapshotProcessor(
            api_key=api_key,
            snapshot_num=snapshot_num,
            output_dir=output_path,
            simulation=simulation,
            temp_dir=output_path
        )
        
        success = processor.process(test_mode=False)
        return (simulation, snapshot_num, success)
    
    except Exception as e:
        print(f"✗ Error processing {simulation} snapshot {snapshot_num}: {e}")
        return (simulation, snapshot_num, False)


def main():

    # Original snapshot lists (can be adjusted as needed)
    # snapshot_dict = {'TNG50-1': np.array([73, 76, 81, 85, 89, 93, 97]),
    #                  'TNG50-2': np.array([60, 61, 62, 64, 65, 68, 69, 71]),
    #                  'TNG100-1': np.array([26, 29, 32, 36, 39, 44, 47, 51, 54, 58])}

    # Failed snapshot lists 

    snapshot_dict = {'TNG50-2': np.array([98]),}

    outputPath = "/Volumes/PMSAdrive/pmsa/storage/TNG/"
    YOUR_KEY = "8a23973c71dfa5b08a074e900b1411ea"
    
    # Create list of all (simulation, snapshot_num) pairs to process
    tasks = []
    for simulation, snapshot_nums in snapshot_dict.items():
        for snapshot_num in snapshot_nums:
            tasks.append((simulation, int(snapshot_num), YOUR_KEY, os.path.join(outputPath, simulation)))
    
    total_tasks = len(tasks)
    print(f"\n{'='*60}")
    print(f"TNG DATA DOWNLOADER - PARALLEL MODE")
    print(f"{'='*60}")
    print(f"Total tasks: {total_tasks}")
    print(f"Simulations: {list(snapshot_dict.keys())}")
    print(f"Output directory: {outputPath}\n")
    
    # Process snapshots in parallel using ThreadPoolExecutor
    # Using max_workers to limit concurrent downloads (adjust based on network/CPU)
    max_workers = 5  # Parallel downloads
    
    results = []
    start_time = time.time()
    
    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        # Submit all tasks
        future_to_task = {
            executor.submit(process_single_snapshot, sim, snap_num, api_key, out_path): 
            (sim, snap_num) 
            for sim, snap_num, api_key, out_path in tasks
        }
        
        # Process completed tasks as they finish
        completed = 0
        for future in as_completed(future_to_task):
            completed += 1
            try:
                simulation, snapshot_num, success = future.result()
                results.append((simulation, snapshot_num, success))
                status = "✓ SUCCESS" if success else "✗ FAILED"
                print(f"\n[{completed}/{total_tasks}] {status}: {simulation} snapshot {snapshot_num}")
            except Exception as e:
                sim, snap_num = future_to_task[future]
                print(f"\n[{completed}/{total_tasks}] ✗ EXCEPTION: {sim} snapshot {snap_num}: {e}")
                results.append((sim, snap_num, False))
    
    elapsed_time = time.time() - start_time
    
    # Print summary
    successful = sum(1 for _, _, success in results if success)
    failed = total_tasks - successful
    
    print(f"\n{'='*60}")
    print(f"PARALLEL PROCESSING COMPLETE")
    print(f"{'='*60}")
    print(f"Time elapsed: {elapsed_time/60:.1f} minutes")
    print(f"\nResults:")
    print(f"  Successful: {successful}/{total_tasks}")
    print(f"  Failed: {failed}/{total_tasks}")
    print(f"\nDetails:")
    
    for simulation, snapshot_num, success in sorted(results):
        status = "✓" if success else "✗"
        print(f"  {status} {simulation:12} snapshot {snapshot_num:2}")
    
    print(f"\n{'='*60}\n")
    
    # Exit with appropriate code
    sys.exit(0 if failed == 0 else 1)


if __name__ == "__main__":
    main()
