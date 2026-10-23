"""
Merge Lightcone Plane Catalogs into Final Full-Cone Galaxy Catalog.
"""

import os
from pathlib import Path
from astropy.io import ascii


def merge_galaxy_catalogs(planes_file, module="igm", input_path="./", output_file=None, add_tag=""):
    """
    Merge individual plane outcat files into a final lightcone galaxy catalog.

    Parameters
    ----------
    planes_file : str or Path
        Planes list with #pl, snap, z.
    module : str
        Module name: 'df', 'dc', or 'igm'.
    input_path : str or Path
        Directory where catalog files are stored.
    output_file : str or Path, optional
        Destination file path. Defaults to 'final_cat.<module>.<add_tag>.dat'.
    add_tag : str, optional
        Optional tag to append to output filename.

    Returns
    -------
    str
        Path to generated merged catalog.
    """
    inp = ascii.read(str(planes_file))
    snap = inp["snap"]
    pl = inp["pl"] - 1

    input_dir = Path(input_path)
    filenames = [
        str(input_dir / f"outcat.{module}.{n}_{m}.txt")
        for n, m in zip(snap, pl)
    ]

    if not output_file:
        tag_str = f".{add_tag}" if add_tag else ""
        output_file = str(input_dir / f"final_cat.{module}{tag_str}.dat")

    write_header = True
    found_any = False
    with open(output_file, "w") as outfile:
        for fname in filenames:
            if not os.path.isfile(fname):
                continue
            found_any = True
            with open(fname, "r") as infile:
                lines = infile.read().splitlines()
                if not lines:
                    continue
                if write_header:
                    outfile.write(lines[0] + "\n")
                    write_header = False
                outfile.write("\n".join(lines[1:]) + "\n")

    if not found_any:
        raise FileNotFoundError(f"No outcat files found for module '{module}' in {input_dir}")

    return str(output_file)
