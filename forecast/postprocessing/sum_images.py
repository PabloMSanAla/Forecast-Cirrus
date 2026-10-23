"""
FITS Image Stacking Module for FORECAST.
Provides RAM-aware chunked and memory-mapped FITS image summation.
"""

import os
import glob
import numpy as np
from astropy.io import fits
from tqdm import tqdm


def sum_massive_fits(input_dir, output_file, chunk_size=1024, out_dtype=np.float32):
    """
    Sums all FITS images in a directory in a RAM-aware manner using spatial row chunking.
    
    Parameters
    ----------
    input_dir : str or Path
        Directory containing the .fits files.
    output_file : str or Path
        Target destination file for the summed FITS image.
    chunk_size : int, default=1024
        Number of rows processed per chunk to bound peak RAM.
    out_dtype : numpy datatype, default=np.float32
        Output numpy data type.
    """
    file_list = sorted(glob.glob(os.path.join(input_dir, "*.fits")))
    if not file_list:
        raise FileNotFoundError(f"No .fits files found in {input_dir}")

    # Extract metadata from the first file
    with fits.open(file_list[0], memmap=True) as hdul:
        base_header = hdul[0].header.copy()
        shape = hdul[0].shape

    if len(shape) < 2:
        raise ValueError("The FITS file does not contain 2D/3D image data in HDU 0.")

    # Pre-allocate output file on disk
    empty_array = np.zeros(shape, dtype=out_dtype)
    fits.writeto(output_file, empty_array, header=base_header, overwrite=True)

    num_rows = shape[0]
    for start_row in tqdm(range(0, num_rows, chunk_size), desc="Processing chunks"):
        end_row = min(start_row + chunk_size, num_rows)
        chunk_shape = (end_row - start_row,) + shape[1:]
        chunk_sum = np.zeros(chunk_shape, dtype=out_dtype)

        for file in file_list:
            with fits.open(file, memmap=True) as hdul:
                data_chunk = hdul[0].section[start_row:end_row, ...]
                chunk_sum += data_chunk.astype(out_dtype)

        with fits.open(output_file, mode="update", memmap=True) as hdul_out:
            hdul_out[0].data[start_row:end_row, ...] = chunk_sum
            hdul_out.flush()

    return output_file


def sum_massive_fits_fast(input_dir, output_file, chunk_size=1024):
    """
    Fast version of sum_massive_fits using memory mapping.
    
    Parameters
    ----------
    input_dir : str or Path
        Directory containing .fits files.
    output_file : str or Path
        Destination path for stacked FITS file.
    chunk_size : int, default=1024
        Row chunk size.
    """
    file_list = sorted(glob.glob(os.path.join(input_dir, "*.fits")))
    if not file_list:
        raise FileNotFoundError(f"No .fits files found in {input_dir}")

    with fits.open(file_list[0], memmap=True) as hdul:
        base_header = hdul[0].header.copy()
        shape = hdul[0].shape

    if len(shape) < 2:
        raise ValueError("The FITS file does not contain 2D/3D image data in HDU 0.")

    empty_hdu = fits.PrimaryHDU(header=base_header)
    empty_hdu.header["NAXIS"] = len(shape)
    for i, dim in enumerate(shape[::-1]):
        empty_hdu.header[f"NAXIS{i+1}"] = dim

    empty_array = np.zeros(shape, dtype=np.float32)

    for file in tqdm(file_list, desc="Summing images"):
        empty_array += fits.getdata(file).astype(np.float32)

    hdu = fits.PrimaryHDU(data=empty_array, header=base_header)
    hdu.writeto(output_file, overwrite=True)
    return output_file
