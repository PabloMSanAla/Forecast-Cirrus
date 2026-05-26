#!/usr/bin/env python3
"""
Create symbolic links to TNG files to match readTNGParticle.cpp naming convention.

This script creates symbolic links from the actual TNG file names to the format
expected by FORECAST's readTNGParticle.cpp:

Expected by readTNGParticle.cpp:
  - snapdir_0{snapNum}/snap_0{snapNum}.{chunk}.hdf5
  - groups_0{snapNum}/fof_subhalo_tab_0{snapNum}.{chunk}.hdf5
  - offsets_0{snapNum}.hdf5

Actual TNG file names:
  - snapdir_{snapNum:03d}/snapshot-{snapNum}.{chunk}.hdf5
  - groups_{snapNum:03d}/groupcat-{snapNum}.{chunk}.hdf5
  - offsets_{snapNum:03d}/offsets.{snapNum}.hdf5

Usage:
    python create_tng_symlinks.py /path/to/TNG/data 98
    python create_tng_symlinks.py /Volumes/T7/storage/TNG/TNG50-2 98 --dry-run
"""

import argparse
import os
from pathlib import Path
import sys


def create_symlinks(tng_dir, snapshot_num, dry_run=False, output_dir=None):
    """
    Create symbolic links for TNG files to match readTNGParticle naming.
    
    Parameters:
    -----------
    tng_dir : str
        Base directory containing TNG data
    snapshot_num : int
        Snapshot number
    dry_run : bool
        If True, only print what would be done without creating links
    output_dir : str
        Directory where symlinks will be created (default: same as tng_dir)
    """
    tng_path = Path(tng_dir).resolve()
    output_path = Path(output_dir).resolve() if output_dir else tng_path

    if not tng_path.exists():
        print(f"Error: Directory {tng_path} does not exist!")
        return False

    if not output_path.exists():
        if not dry_run:
            output_path.mkdir(parents=True, exist_ok=True)
            print(f"Created output directory: {output_path}")
        else:
            print(f"[DRY RUN] Would create output directory: {output_path}")

    print(f"\n{'='*70}")
    print(f"Creating TNG Symbolic Links")
    print(f"{'='*70}")
    print(f"Base directory: {tng_path}")
    print(f"Output directory: {output_path}")
    print(f"Snapshot number: {snapshot_num}")
    print(f"Mode: {'DRY RUN (no files will be created)' if dry_run else 'LIVE'}")
    print(f"{'='*70}\n")
    
    success_count = 0
    error_count = 0
    skip_count = 0
    
    # 1. Create snapdir symbolic links
    print("1. Processing SNAPSHOT files...")
    snapdir_actual = tng_path / f"snapdir_{snapshot_num:03d}"
    snapdir_link = output_path / f"snapdir_0{snapshot_num}"
    
    if snapdir_actual.exists():
        # Create directory if it doesn't exist
        if not snapdir_link.exists():
            if not dry_run:
                snapdir_link.mkdir(parents=True, exist_ok=True)
                print(f"  ✓ Created directory: {snapdir_link.name}")
            else:
                print(f"  [DRY RUN] Would create directory: {snapdir_link.name}")
        
        # Find snapshot files with different possible naming patterns
        snap_patterns = [
            f"snapshot-{snapshot_num}.*.hdf5",  # TNG300-3 format
            f"snapshot_{snapshot_num}.*.hdf5",  # Alternative
            f"snap_{snapshot_num:03d}.*.hdf5",  # TNG100-1 format
            f"snap_0{snapshot_num}.*.hdf5",     # Expected format
        ]
        
        snap_files = []
        for pattern in snap_patterns:
            found = list(snapdir_actual.glob(pattern))
            if found:
                snap_files = found
                break
        
        if snap_files:
            print(f"  Found {len(snap_files)} snapshot chunk files")
            print(f"  Creating individual file symlinks inside {snapdir_link.name}/...")
            
            for snap_file in snap_files:
                # Extract chunk number from various formats
                # snapshot-98.0.hdf5 → 0
                # snap_098.0.hdf5 → 0
                parts = snap_file.stem.split('.')
                if len(parts) >= 2:
                    chunk_str = parts[-1]
                else:
                    # Handle formats like snapshot_98_0.hdf5
                    chunk_str = snap_file.stem.split('_')[-1]
                
                # Create link: snap_098.0.hdf5
                link_name = f"snap_0{snapshot_num}.{chunk_str}.hdf5"
                link_path = snapdir_link / link_name
                
                if link_path.exists():
                    if link_path.is_symlink():
                        skip_count += 1
                    else:
                        print(f"    ⚠ File exists but is not a symlink: {link_name}")
                else:
                    if not dry_run:
                        # Create relative symlink
                        rel_path = os.path.relpath(snap_file, snapdir_link)
                        link_path.symlink_to(rel_path)
                        success_count += 1
                    else:
                        print(f"    [DRY RUN] Would create: {link_name} → {snap_file.name}")
            
            if not dry_run and snap_files:
                print(f"  ✓ Created {len(snap_files)} snapshot file symlinks")
        else:
            print(f"  ✗ No snapshot files found in {snapdir_actual}")
            error_count += 1
    else:
        print(f"  ✗ Snapshot directory not found: {snapdir_actual}")
        error_count += 1
    
    # 2. Create groups symbolic links
    print("\n2. Processing GROUP CATALOG files...")
    groupsdir_actual = tng_path / f"groups_{snapshot_num:03d}"
    groupsdir_link = output_path / f"groups_0{snapshot_num}"
    
    if groupsdir_actual.exists():
        # Create directory if it doesn't exist
        if not groupsdir_link.exists():
            if not dry_run:
                groupsdir_link.mkdir(parents=True, exist_ok=True)
                print(f"  ✓ Created directory: {groupsdir_link.name}")
            else:
                print(f"  [DRY RUN] Would create directory: {groupsdir_link.name}")
        
        # Find group catalog files with different naming patterns
        groupcat_patterns = [
            f"groupcat-{snapshot_num}.*.hdf5",  # TNG300-3 format
            f"fof_subhalo_tab_{snapshot_num:03d}.*.hdf5",  # Alternative
            f"fof_subhalo_tab_0{snapshot_num}.*.hdf5",  # Expected format
        ]
        
        groupcat_files = []
        for pattern in groupcat_patterns:
            found = list(groupsdir_actual.glob(pattern))
            if found:
                groupcat_files = found
                break
        
        if groupcat_files:
            print(f"  Found {len(groupcat_files)} group catalog files")
            print(f"  Creating individual file symlinks inside {groupsdir_link.name}/...")
            
            for groupcat_file in groupcat_files:
                # Extract chunk number: groupcat-98.0.hdf5 → 0
                parts = groupcat_file.stem.split('.')
                if len(parts) >= 2:
                    chunk_str = parts[-1]
                else:
                    chunk_str = groupcat_file.stem.split('_')[-1]
                
                # Create link: fof_subhalo_tab_098.0.hdf5
                link_name = f"fof_subhalo_tab_0{snapshot_num}.{chunk_str}.hdf5"
                link_path = groupsdir_link / link_name
                
                if link_path.exists():
                    if link_path.is_symlink():
                        skip_count += 1
                    else:
                        print(f"    ⚠ File exists but is not a symlink: {link_name}")
                else:
                    if not dry_run:
                        rel_path = os.path.relpath(groupcat_file, groupsdir_link)
                        link_path.symlink_to(rel_path)
                        success_count += 1
                    else:
                        print(f"    [DRY RUN] Would create: {link_name} → {groupcat_file.name}")
            
            if not dry_run and groupcat_files:
                print(f"  ✓ Created {len(groupcat_files)} group catalog file symlinks")
        else:
            print(f"  ✗ No group catalog files found in {groupsdir_actual}")
            error_count += 1
    else:
        print(f"  ✗ Groups directory not found: {groupsdir_actual}")
        error_count += 1
    
    # 3. Create offset symbolic link
    print("\n3. Processing OFFSETS file...")
    offsetsdir_actual = tng_path / f"offsets_{snapshot_num:03d}"
    offset_file_actual = offsetsdir_actual / f"offsets.{snapshot_num}.hdf5"
    offset_link = output_path / f"offsets_0{snapshot_num}.hdf5"
    
    if offset_file_actual.exists():
        if offset_link.exists():
            if offset_link.is_symlink():
                print(f"  ✓ Offset symlink already exists: {offset_link.name}")
                skip_count += 1
            else:
                print(f"  ⚠ Offset file exists but is not a symlink: {offset_link.name}")
        else:
            if not dry_run:
                # Create relative path for the symlink
                rel_path = os.path.relpath(offset_file_actual, tng_path)
                offset_link.symlink_to(rel_path)
                print(f"  ✓ Created offset symlink: {offset_link.name} → {rel_path}")
                success_count += 1
            else:
                print(f"  [DRY RUN] Would create: {offset_link.name} → {offset_file_actual}")
    else:
        print(f"  ✗ Offset file not found: {offset_file_actual}")
        print(f"    Note: Offsets are optional for some simulations")
    
    # Summary
    print(f"\n{'='*70}")
    print(f"Summary")
    print(f"{'='*70}")
    if dry_run:
        print(f"DRY RUN: No files were created")
    else:
        print(f"✓ Created: {success_count}")
        print(f"⊘ Skipped (already exist): {skip_count}")
        print(f"✗ Errors: {error_count}")
    print(f"{'='*70}\n")
    
    if not dry_run:
        print("Symlinks created successfully!")
        print(f"\nDirectory structure created:")
        print(f"  {snapdir_link.name}/")
        print(f"    ├── snap_0{snapshot_num}.0.hdf5 → ../snapdir_{snapshot_num:03d}/snapshot-{snapshot_num}.0.hdf5")
        print(f"    ├── snap_0{snapshot_num}.1.hdf5 → ...")
        print(f"  {groupsdir_link.name}/")
        print(f"    ├── fof_subhalo_tab_0{snapshot_num}.0.hdf5 → ../groups_{snapshot_num:03d}/groupcat-{snapshot_num}.0.hdf5")
        print(f"    ├── fof_subhalo_tab_0{snapshot_num}.1.hdf5 → ...")
        print(f"  offsets_0{snapshot_num}.hdf5 → offsets_{snapshot_num:03d}/offsets.{snapshot_num}.hdf5")
        print(f"\nYou can now use these in readTNGParticle.cpp with:")
        print(f"  workdir = \"{output_path}\"")
        print(f"  particleID = {snapshot_num}")
    
    return error_count == 0


def main():
    parser = argparse.ArgumentParser(
        description='Create symbolic links for TNG files to match readTNGParticle.cpp naming',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Create symlinks for snapshot 98
  python create_tng_symlinks.py /Volumes/T7/storage/TNG/TNG50-2 98
  
  # Dry run to see what would be created
  python create_tng_symlinks.py /Volumes/T7/storage/TNG/TNG50-2 98 --dry-run
  
  # Create symlinks for multiple snapshots
  for snap in 60 70 98; do
      python create_tng_symlinks.py /Volumes/T7/storage/TNG/TNG50-2 $snap
  done
        """
    )
    
    parser.add_argument('tng_dir', type=str,
                       help='Base directory containing TNG data')
    parser.add_argument('snapshot_num', type=int,
                       help='Snapshot number (e.g., 98)')
    parser.add_argument('--dry-run', action='store_true',
                       help='Show what would be done without creating links')
    parser.add_argument('--output-dir', type=str, default=None,
                   help='Directory where symlinks will be created (default: same as tng_dir)')
    
    args = parser.parse_args()
    
    success = create_symlinks(args.tng_dir, args.snapshot_num, args.dry_run, args.output_dir)
    
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()