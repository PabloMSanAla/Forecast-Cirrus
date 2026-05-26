#!/usr/bin/env python
"""
Batch process multiple TNG snapshots for FORECAST.

This script processes multiple snapshots in parallel or sequentially.
"""

import argparse
import sys
from pathlib import Path
from preprocessing.extract_forecast_data import TNGDataExtractor
from tqdm import tqdm


def process_snapshot(base_dir, snapshot_num, output_dir):
    """
    Process a single snapshot.
    
    Parameters:
    -----------
    base_dir : str
        Base TNG directory (e.g., 'TNG100/')
    snapshot_num : int
        Snapshot number
    output_dir : str
        Output directory
        
    Returns:
    --------
    tuple : (snapshot_num, success, message)
    """
    try:
        base_path = Path(base_dir)
        snapshot_dir = base_path / f"snapdir_{snapshot_num:03d}"
        groupcat_dir = base_path / f"groups_{snapshot_num:03d}"
        
        # Check if directories exist
        if not snapshot_dir.exists():
            return (snapshot_num, False, f"Snapshot directory not found: {snapshot_dir}")
        
        if not groupcat_dir.exists():
            print(f"Warning: Group catalog directory not found: {groupcat_dir}")
            print(f"Continuing without subhalo information...")
        
        # Create extractor
        extractor = TNGDataExtractor(
            snapshot_dir=str(snapshot_dir),
            groupcat_dir=str(groupcat_dir) if groupcat_dir.exists() else str(snapshot_dir),
            output_dir=output_dir,
            snapshot_num=snapshot_num
        )
        
        # Extract
        output_file = extractor.extract()
        
        return (snapshot_num, True, f"Success: {output_file}")
        
    except Exception as e:
        return (snapshot_num, False, f"Error: {str(e)}")


def main():
    parser = argparse.ArgumentParser(
        description='Batch process multiple TNG snapshots for FORECAST'
    )
    
    parser.add_argument('--base-dir', type=str, required=True,
                       help='Base TNG directory (e.g., TNG100/)')
    parser.add_argument('--snapshots', type=int, nargs='+', required=True,
                       help='Snapshot numbers to process (e.g., 99 98 97)')
    parser.add_argument('--output-dir', type=str, required=True,
                       help='Output directory for all snapshots')
    
    args = parser.parse_args()
    
    print(f"\n{'='*60}")
    print(f"BATCH PROCESSING {len(args.snapshots)} SNAPSHOTS")
    print(f"{'='*60}\n")
    
    print(f"Base directory: {args.base_dir}")
    print(f"Output directory: {args.output_dir}")
    print(f"Snapshots: {args.snapshots}\n")
    
    # Create output directory
    Path(args.output_dir).mkdir(parents=True, exist_ok=True)
    
    # Process each snapshot
    results = []
    for snap_num in tqdm(args.snapshots, desc="Processing snapshots"):
        print(f"\n{'-'*60}")
        print(f"Processing snapshot {snap_num}...")
        print(f"{'-'*60}")
        
        result = process_snapshot(args.base_dir, snap_num, args.output_dir)
        results.append(result)
        
        snap_num, success, message = result
        if success:
            print(f"✓ Snapshot {snap_num}: {message}")
        else:
            print(f"✗ Snapshot {snap_num}: {message}")
    
    # Summary
    print(f"\n{'='*60}")
    print(f"BATCH PROCESSING COMPLETE")
    print(f"{'='*60}\n")
    
    successful = sum(1 for _, success, _ in results if success)
    failed = len(results) - successful
    
    print(f"Total snapshots: {len(results)}")
    print(f"Successful: {successful}")
    print(f"Failed: {failed}")
    
    if failed > 0:
        print(f"\nFailed snapshots:")
        for snap_num, success, message in results:
            if not success:
                print(f"  Snapshot {snap_num}: {message}")
    
    print()
    
    return 0 if failed == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
