import os
import glob
import numpy as np
from astropy.io import fits
from tqdm import tqdm

def sum_massive_fits(input_dir, output_file, chunk_size=1024, out_dtype=np.float32):
    """
    Sums all FITS images in a directory in a RAM-aware manner using spatial chunking.
    
    Parameters:
    - input_dir: Path to the directory containing the .fits files.
    - output_file: Path to save the final summed FITS file.
    - chunk_size: Number of rows to process at once. (1024 is usually a good balance).
    - out_dtype: Output numpy datatype. Default is float32 to prevent overflow 
                 when summing many images.
    """
    # 1. Find all FITS files
    file_list = glob.glob(os.path.join(input_dir, '*.fits'))
    if not file_list:
        raise FileNotFoundError(f"No .fits files found in {input_dir}")
        
    print(f"Found {len(file_list)} files. Extracting metadata...")
    
    # 2. Get header and dimensions from the first file
    with fits.open(file_list[0], memmap=True) as hdul:
        # Assuming the image data is in the Primary HDU (index 0)
        base_header = hdul[0].header.copy()
        shape = hdul[0].shape
        
    if len(shape) < 2:
        raise ValueError("The FITS file does not contain 2D/3D image data in HDU 0.")


    # Create an empty header block to write to disk
    empty_hdu = fits.PrimaryHDU(header=base_header)
    empty_array = np.zeros(shape, dtype=out_dtype)
    fits.writeto(output_file, empty_array, header=base_header, overwrite=True)

    # 4. Stream-write the output
    print(f"Pre-allocating and streaming data to {output_file}...")
    
    num_rows = shape[0]
    # Iterate over the image in row chunks
    for start_row in tqdm(range(0, num_rows, chunk_size), desc="Processing chunks"):
        end_row = min(start_row + chunk_size, num_rows)
        chunk_shape = (end_row - start_row,) + shape[1:]
            
        # Initialize a zeroed array for this chunk
        chunk_sum = np.zeros(chunk_shape, dtype=out_dtype)
        
        # Open every file, grab *only* this specific chunk, and add it
        for file in file_list:
            with fits.open(file, memmap=True) as hdul:
                # .section directly pulls only the requested slice from disk
                data_chunk = hdul[0].section[start_row:end_row, ...]
                chunk_sum += data_chunk.astype(out_dtype)
                    
        with fits.open(output_file, mode='update', memmap=True) as hdul_out:
            hdul_out[0].data[start_row:end_row, ...] = chunk_sum
            hdul_out.flush()  # Ensure data is written to disk

            
    print(f"Success! Summed image saved to {output_file}")


def sum_massive_fits_fast(input_dir, output_file, chunk_size=1024):
    """
    A faster version of sum_massive_fits that uses memory mapping and avoids 
    loading entire images into RAM at once. This is especially useful for very 
    large FITS files.
    
    Parameters:
    - input_dir: Path to the directory containing the .fits files.
    - output_file: Path to save the final summed FITS file.
    - chunk_size: Number of rows to process at once. (1024 is usually a good balance).
    """
    # 1. Find all FITS files
    file_list = glob.glob(os.path.join(input_dir, '*.fits'))
    if not file_list:
        raise FileNotFoundError(f"No .fits files found in {input_dir}")
        
    print(f"Found {len(file_list)} files. Extracting metadata...")
    
    # 2. Get header and dimensions from the first file
    with fits.open(file_list[0], memmap=True) as hdul:
        base_header = hdul[0].header.copy()
        shape = hdul[0].shape
        
    if len(shape) < 2:
        raise ValueError("The FITS file does not contain 2D/3D image data in HDU 0.")

    # Create an empty header block to write to disk
    empty_hdu = fits.PrimaryHDU(header=base_header)
    empty_hdu.header['NAXIS'] = len(shape)
    for i, dim in enumerate(shape[::-1]):
        empty_hdu.header[f'NAXIS{i+1}'] = dim

    empty_array = np.zeros(shape, dtype=np.float32)

    for file in tqdm(file_list, desc="Summing images"):
        empty_array += fits.getdata(file).astype(np.float32)

    # Write the summed array to a new FITS file
    hdu = fits.PrimaryHDU(data=empty_array, header=base_header)
    hdu.writeto(output_file, overwrite=True)

    return True

# ==========================================
# Example Usage:
# ==========================================
if __name__ == "__main__":
    DIRECTORY = "/Volumes/PMSAdrive/pmsa/storage/TNG/forecast/image/"
    OUTPUT = "/Volumes/PMSAdrive/pmsa/storage/TNG/forecast/image/summed_output.fits"
    
    # 1024 rows of a 10k x 10k float32 image is only ~40MB of RAM at a time.
    sum_massive_fits(DIRECTORY, OUTPUT, chunk_size=4096)