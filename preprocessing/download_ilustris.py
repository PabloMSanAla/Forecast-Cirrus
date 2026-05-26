import requests
import os
import sys
import argparse
from pathlib import Path

class TNGDownloader:
    """
    Download TNG/Illustris snapshots with specific fields for FORECAST lightcone code.
    Only downloads gas (PartType0) and star (PartType4) particles with subhalo IDs.
    """
    
    def __init__(self, api_key, simulation='TNG100-1', output_dir='./TNG100'):
        """
        Initialize the TNG downloader.
        
        Parameters:
        -----------
        api_key : str
            Your IllustrisTNG API key
        simulation : str
            Simulation name (e.g., 'TNG100-1', 'TNG100-3', 'TNG50-1')
        output_dir : str
            Directory where snapshots will be saved
        """
        self.api_key = api_key
        self.simulation = simulation
        self.output_dir = Path(output_dir)
        self.base_url = 'https://www.tng-project.org/api'
        self.headers = {'api-key': api_key}
        
        # Create output directory
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
        print(f"Initialized TNG Downloader")
        print(f"Simulation: {simulation}")
        print(f"Output directory: {output_dir}")
    
    def get_snapshot_number_from_redshift(self, target_redshift):
        """
        Find the snapshot number closest to the target redshift.
        
        Parameters:
        -----------
        target_redshift : float
            Target redshift
            
        Returns:
        --------
        int : Snapshot number
        """
        url = f"{self.base_url}/{self.simulation}/snapshots/"
        response = requests.get(url, headers=self.headers)
        
        if response.status_code != 200:
            print(f"Error: Could not retrieve snapshot list. Status code: {response.status_code}")
            return None
        
        # TNG API returns a list directly or a dict with 'results'
        data = response.json()
        snapshots = data if isinstance(data, list) else data.get('results', [])
        
        # Find closest snapshot to target redshift
        min_diff = float('inf')
        best_snap = None
        
        for snap in snapshots:
            redshift = snap['redshift']
            diff = abs(redshift - target_redshift)
            if diff < min_diff:
                min_diff = diff
                best_snap = snap['number']
                best_z = redshift
        
        print(f"\nTarget redshift: {target_redshift}")
        print(f"Closest snapshot: {best_snap} (z = {best_z:.4f})")
        
        return best_snap
    
    def download_snapshot_file(self, snapshot_num, file_num=0, test_mode=False):
        """
        Download a single snapshot file.
        
        Parameters:
        -----------
        snapshot_num : int
            Snapshot number (e.g., 99 for z=0)
        file_num : int
            File number within the snapshot (default: 0)
        test_mode : bool
            If True, only download first file for testing
            
        Returns:
        --------
        str : Path to downloaded file
        """
        
        # Create snapshot directory
        snap_dir = self.output_dir / f"snapdir_{snapshot_num:03d}"
        snap_dir.mkdir(parents=True, exist_ok=True)
        
        output_file = snap_dir / f"snap_{snapshot_num:03d}.{file_num}.hdf5"
        
        # Check if file already exists
        if output_file.exists():
            file_size = output_file.stat().st_size
            # If file is less than 1MB, it's probably an error message, re-download
            if file_size > 1024 * 1024:
                print(f"File already exists: {output_file} ({file_size / (1024**3):.2f} GB)")
                return str(output_file)
            else:
                print(f"File exists but is too small ({file_size} bytes), re-downloading...")
                output_file.unlink()
        
        return self._download_file_from_api(
            snapshot_num, file_num, output_file, 
            file_type='snapshot', test_mode=test_mode
        )
    
    def download_groupcat_file(self, snapshot_num, file_num=0, test_mode=False):
        """
        Download a single group catalog file (contains subhalo membership).
        
        Parameters:
        -----------
        snapshot_num : int
            Snapshot number (e.g., 99 for z=0)
        file_num : int
            File number within the group catalog (default: 0)
        test_mode : bool
            If True, only download first file for testing
            
        Returns:
        --------
        str : Path to downloaded file
        """
        
        # Create groups directory
        groups_dir = self.output_dir / f"groups_{snapshot_num:03d}"
        groups_dir.mkdir(parents=True, exist_ok=True)
        
        output_file = groups_dir / f"fof_subhalo_tab_{snapshot_num:03d}.{file_num}.hdf5"
        
        # Check if file already exists
        if output_file.exists():
            file_size = output_file.stat().st_size
            if file_size > 1024 * 1024:
                print(f"File already exists: {output_file} ({file_size / (1024**3):.2f} GB)")
                return str(output_file)
            else:
                print(f"File exists but is too small ({file_size} bytes), re-downloading...")
                output_file.unlink()
        
        return self._download_file_from_api(
            snapshot_num, file_num, output_file,
            file_type='groupcat', test_mode=test_mode
        )
    
    def _download_file_from_api(self, snapshot_num, file_num, output_file, file_type='snapshot', test_mode=False):
        """
        Internal method to download a file from TNG API.
        
        Parameters:
        -----------
        snapshot_num : int
            Snapshot number
        file_num : int
            File number
        output_file : Path
            Output file path
        file_type : str
            'snapshot' or 'groupcat'
        test_mode : bool
            Test mode flag
        """
        print(f"Note: Downloading full snapshot file (includes all particle types)")
        print(f"Filter to Gas and Stars during processing with C++ code.")
        
        
        file_type_name = "snapshot" if file_type == 'snapshot' else "group catalog"
        print(f"\nDownloading {file_type_name} {snapshot_num}, file {file_num}...")
        
        if file_type == 'groupcat':
            print(f"Note: Group catalogs contain subhalo membership information")
        else:
            print(f"Note: Downloading full snapshot file (includes all particle types)")
            print(f"Filter to Gas and Stars during processing with C++ code.")
        
        # Get the actual download URL from TNG API
        # First, get the file list to find the correct file URL
        if file_type == 'snapshot':
            files_url = f"{self.base_url}/{self.simulation}/files/snapshot-{snapshot_num}/"
            target_filename = f"snapshot-{snapshot_num}.{file_num}.hdf5"
        else:  # groupcat
            files_url = f"{self.base_url}/{self.simulation}/files/groupcat-{snapshot_num}/"
            target_filename = f"groupcat-{snapshot_num}.{file_num}.hdf5"
        
        print(f"Querying file list: {files_url}")
        files_response = requests.get(files_url, headers=self.headers)
        
        if files_response.status_code != 200:
            print(f"Error: Could not get file list. Status code: {files_response.status_code}")
            print(f"Response: {files_response.text[:500]}")
            return None
        
        files_data = files_response.json()
        
        # Find the specific file we want
        # target_filename set above based on file_type
        file_url = None
        
        # API returns: {'files': ['http://...', 'http://...', ...]}
        if isinstance(files_data, dict) and 'files' in files_data:
            files_list = files_data['files']
        elif isinstance(files_data, list):
            files_list = files_data
        else:
            print(f"Unexpected API response format: {type(files_data)}")
            print(f"Keys: {files_data.keys() if isinstance(files_data, dict) else 'N/A'}")
            return None
        
        # Find the file URL that matches our target
        for file_path in files_list:
            if target_filename in file_path:
                file_url = file_path
                break
        
        if not file_url:
            print(f"Error: Could not find file {target_filename} in snapshot {snapshot_num}")
            print(f"Available files (first 3): {files_list[:3]}")
            return None
        
        print(f"File URL: {file_url}")
        
        # Make the request with allow_redirects to follow the download link
        response = requests.get(file_url, headers=self.headers, stream=True, allow_redirects=True)
        
        if response.status_code != 200:
            print(f"Error downloading file. Status code: {response.status_code}")
            print(f"Response: {response.text[:500]}")
            return None
        
        # Get file size
        total_size = int(response.headers.get('content-length', 0))
        total_size_gb = total_size / (1024**3)
        print(f"Download size: {total_size_gb:.2f} GB ({total_size / (1024**2):.0f} MB)")
        
        if test_mode and total_size > 100 * 1024 * 1024:  # If test mode and > 100 MB
            print(f"\n⚠ TEST MODE: File is {total_size_gb:.2f} GB")
            print(f"This is a full snapshot download and will take time.")
            print(f"File will be downloaded to: {output_file}")
        
        # Download with progress bar
        downloaded = 0
        chunk_size = 1024 * 1024  # 1 MB chunks for faster download
        with open(output_file, 'wb') as f:
            for chunk in response.iter_content(chunk_size=chunk_size):
                if chunk:
                    f.write(chunk)
                    downloaded += len(chunk)
                    progress = (downloaded / total_size) * 100 if total_size > 0 else 0
                    downloaded_mb = downloaded / (1024**2)
                    total_mb = total_size / (1024**2)
                    print(f"\rProgress: {progress:.1f}% ({downloaded_mb:.1f}/{total_mb:.0f} MB)", end='', flush=True)
        
        print(f"\n✓ Downloaded: {output_file}")
        
        if test_mode:
            print("\n** TEST MODE: Only downloaded one file **")
        
        return str(output_file)
    
    def download_full_snapshot(self, snapshot_num, test_mode=False, download_groupcat=True):
        """
        Download all files for a snapshot and optionally group catalogs.
        
        Parameters:
        -----------
        snapshot_num : int
            Snapshot number
        test_mode : bool
            If True, only download first file
        download_groupcat : bool
            If True, also download group catalog files (contains subhalo IDs)
            
        Returns:
        --------
        dict : Dictionary with 'snapshots' and 'groupcats' file lists
        """
        
        # Get number of files in snapshot
        url = f"{self.base_url}/{self.simulation}/snapshots/{snapshot_num}/"
        response = requests.get(url, headers=self.headers)
        
        if response.status_code != 200:
            print(f"Error: Could not retrieve snapshot info. Status code: {response.status_code}")
            return None
        
        snapshot_info = response.json()
        num_files = snapshot_info.get('num_files', 1)
        
        print(f"\nSnapshot {snapshot_num} has {num_files} snapshot files")
        
        if test_mode:
            print("TEST MODE: Downloading only first file of each type")
            num_files = 1
        
        # Download snapshot files
        print(f"\n{'='*60}")
        print(f"DOWNLOADING SNAPSHOT FILES")
        print(f"{'='*60}")
        downloaded_snapshots = []
        for file_num in range(num_files):
            filepath = self.download_snapshot_file(snapshot_num, file_num, test_mode=test_mode)
            if filepath:
                downloaded_snapshots.append(filepath)
        
        print(f"\n✓ Successfully downloaded {len(downloaded_snapshots)} snapshot file(s)")
        
        # Download group catalog files (contains subhalo membership)
        downloaded_groupcats = []
        if download_groupcat:
            print(f"\n{'='*60}")
            print(f"DOWNLOADING GROUP CATALOG FILES (SUBHALO INFO)")
            print(f"{'='*60}")
            
            # Get number of group catalog files
            groupcat_url = f"{self.base_url}/{self.simulation}/files/groupcat-{snapshot_num}/"
            groupcat_response = requests.get(groupcat_url, headers=self.headers)
            
            if groupcat_response.status_code == 200:
                groupcat_data = groupcat_response.json()
                if isinstance(groupcat_data, dict) and 'files' in groupcat_data:
                    num_groupcat_files = len(groupcat_data['files'])
                    print(f"Snapshot {snapshot_num} has {num_groupcat_files} group catalog files")
                    
                    if test_mode:
                        num_groupcat_files = 1
                    
                    for file_num in range(num_groupcat_files):
                        filepath = self.download_groupcat_file(snapshot_num, file_num, test_mode=test_mode)
                        if filepath:
                            downloaded_groupcats.append(filepath)
                    
                    print(f"\n✓ Successfully downloaded {len(downloaded_groupcats)} group catalog file(s)")
                else:
                    print(f"Warning: Could not determine number of group catalog files")
            else:
                print(f"Warning: Could not retrieve group catalog info (status {groupcat_response.status_code})")
                print(f"Snapshot files downloaded, but no group catalogs.")
        
        return {
            'snapshots': downloaded_snapshots,
            'groupcats': downloaded_groupcats
        }
    
    def download_by_redshift(self, redshift, test_mode=False):
        """
        Download snapshot closest to given redshift.
        
        Parameters:
        -----------
        redshift : float
            Target redshift
        test_mode : bool
            If True, only download first file
            
        Returns:
        --------
        list : Paths to downloaded files
        """
        snapshot_num = self.get_snapshot_number_from_redshift(redshift)
        if snapshot_num is None:
            return None
        
        return self.download_full_snapshot(snapshot_num, test_mode=test_mode)
    
    def download_multiple_redshifts(self, redshift_list, test_mode=False):
        """
        Download multiple snapshots for a list of redshifts.
        
        Parameters:
        -----------
        redshift_list : list
            List of redshifts
        test_mode : bool
            If True, only download first file of each snapshot
        """
        print(f"\nDownloading {len(redshift_list)} snapshots...")
        
        for i, z in enumerate(redshift_list, 1):
            print(f"\n{'='*60}")
            print(f"Downloading snapshot {i}/{len(redshift_list)} at z={z}")
            print(f"{'='*60}")
            self.download_by_redshift(z, test_mode=test_mode)


def main():
    parser = argparse.ArgumentParser(
        description='Download TNG snapshots for FORECAST lightcone code'
    )
    
    parser.add_argument('--api-key', type=str, required=True,
                       help='Your IllustrisTNG API key')
    parser.add_argument('--simulation', type=str, default='TNG100-1',
                       help='Simulation name (default: TNG100-1)')
    parser.add_argument('--redshift', type=float, nargs='+',
                       help='Redshift(s) to download (e.g., --redshift 0.0 1.0 2.0)')
    parser.add_argument('--snapshot', type=int,
                       help='Specific snapshot number to download')
    parser.add_argument('--output-dir', type=str, default='./TNG100',
                       help='Output directory (default: ./TNG100)')
    parser.add_argument('--test', action='store_true',
                       help='Test mode: only download first file of snapshot')
    parser.add_argument('--no-groupcat', action='store_true',
                       help='Skip downloading group catalog files (subhalo info)')
    
    args = parser.parse_args()
    
    # Initialize downloader
    downloader = TNGDownloader(
        api_key=args.api_key,
        simulation=args.simulation,
        output_dir=args.output_dir
    )
    
    download_groupcat = not args.no_groupcat
    
    # Download based on arguments
    if args.snapshot is not None:
        print(f"\nDownloading snapshot {args.snapshot}...")
        downloader.download_full_snapshot(args.snapshot, test_mode=args.test, download_groupcat=download_groupcat)
    
    elif args.redshift:
        if len(args.redshift) == 1:
            print(f"\nDownloading snapshot at z={args.redshift[0]}...")
            results = downloader.download_by_redshift(args.redshift[0], test_mode=args.test)
        else:
            print(f"\nDownloading {len(args.redshift)} snapshots...")
            downloader.download_multiple_redshifts(args.redshift, test_mode=args.test)
    
    else:
        print("Error: Must specify either --redshift or --snapshot")
        parser.print_help()


if __name__ == "__main__":
    
    # Example usage within script (comment out main() above and uncomment below):
    
    # API_KEY = "your_api_key_here"
    # 
    # downloader = TNGDownloader(
    #     api_key=API_KEY,
    #     simulation='TNG100-1',
    #     output_dir='./TNG100'
    # )
    # 
    # # Test mode: download only first file of snapshot at z=0
    # downloader.download_by_redshift(0.0, test_mode=True)
    # 
    # # Full download: all files for snapshot at z=0
    # downloader.download_by_redshift(0.0, test_mode=False)
    # 
    # # Download multiple redshifts
    # downloader.download_multiple_redshifts([0.0, 1.0, 2.0], test_mode=True)
    
    main()