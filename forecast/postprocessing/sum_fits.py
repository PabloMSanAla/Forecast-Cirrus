"""
Metadata-driven FITS Image Stacker across lightcone planes.
"""

import os
from pathlib import Path
import numpy as np
from astropy.io import fits, ascii


def stack_fits_images(planes_file, filter_name="no_filter", module="igm", input_path="./", output_file=None, add_tag=""):
    """
    Stack plane FITS images into a final lightcone mosaic with consolidated header metadata.

    Parameters
    ----------
    planes_file : str or Path
        File containing lightcone planes list (#pl, snap, z columns).
    filter_name : str
        Target filter name.
    module : str
        Module name: 'df', 'dc', or 'igm'.
    input_path : str or Path
        Directory where plane FITS images are stored.
    output_file : str or Path, optional
        Destination file path. Defaults to 'stacked.<filter><module>.<add_tag>.fits'.
    add_tag : str, optional
        Extra tag to append to default filename.

    Returns
    -------
    str
        Path to written stacked FITS file.
    """
    inp = ascii.read(str(planes_file))
    snap = inp["snap"]
    pl = inp["pl"] - 1

    input_dir = Path(input_path)
    image_list = [
        str(input_dir / f"{filter_name}.{module}.{n}_{m}.fits")
        for n, m in zip(snap, pl)
    ]

    image_concat = []
    header_list = []
    for image in image_list:
        if not os.path.isfile(image):
            raise FileNotFoundError(f"Missing required plane FITS file: {image}")
        image_concat.append(fits.getdata(image))
        header_list.append(fits.getheader(image))

    z_first = header_list[0].get("REDSHIFT", 0.0)
    z_last = header_list[-1].get("REDSHIFT", 0.0)
    truenpix = header_list[0].get("N_PIXEL_BY_SIDE", image_concat[0].shape[0])
    bufferpix = header_list[0].get("BUFFER_PIXELS", 0)
    pixu = header_list[0].get("PIXELUNIT", "flux")
    ntotxy4 = sum(h.get("N_STELLAR_PARTICLES", 0) for h in header_list)
    fov = header_list[0].get("PHYSICALSIZE_BY_SIDE", 0.0)
    h0 = header_list[0].get("HUBBLE", 0.6774)
    dl_first = float(header_list[0].get("Dl_UP", 0.0)) * h0
    dl_last = float(header_list[-1].get("Dl_UP", 0.0)) * h0

    final_image = np.zeros(shape=image_concat[0].shape, dtype=np.float32)
    for img in image_concat:
        final_image += img.astype(np.float32)

    if not output_file:
        tag_str = f".{add_tag}." if add_tag else "."
        output_file = str(input_dir / f"stacked.{filter_name}.{module}{tag_str}fits")

    header = fits.Header()
    header["HIERARCH N_PIXEL_BY_SIDE"] = truenpix
    header["HIERARCH BUFFER_PIXELS"] = bufferpix
    header["HIERARCH PHYSICALSIZE_BY_SIDE_DEG"] = fov
    header["HIERARCH PIXEL_UNIT"] = pixu
    header["HIERARCH N_STELLAR_PARTICLES"] = ntotxy4
    header["HIERARCH FILTER"] = filter_name
    header["HIERARCH LOWER_REDSHIFT"] = z_first
    header["HIERARCH UPPER_REDSHIFT"] = z_last
    header["HIERARCH LOWER_Dl_Mpc"] = dl_first
    header["HIERARCH UPPER_Dl_Mpc"] = dl_last
    header["h0"] = h0

    hdu = fits.PrimaryHDU(data=final_image, header=header)
    hdu.writeto(str(output_file), overwrite=True)
    return str(output_file)
