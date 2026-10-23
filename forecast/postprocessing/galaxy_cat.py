"""
Galaxy Catalog Generator from FORECAST Particle Catalogs.
Computes mass-weighted, flux-weighted, and radial galaxy attributes.
"""

import os
from pathlib import Path
import numpy as np
import pandas as pd
from astropy.io import ascii


def load_particle_data(file_path):
    """Load particle table detecting column count."""
    with open(file_path, "r") as f:
        fline = f.readline()
        ncols = len(fline.split())
    data = np.loadtxt(file_path, dtype="double", unpack=True, usecols=range(ncols))
    return data.tolist()


def build_galaxy_catalog(planes_file, module="igm", input_path="./", filter_pos=0, fov_deg=0.0, res_as=0.0):
    """
    Generate galaxy catalogs from plane particle catalogs.

    Parameters
    ----------
    planes_file : str or Path
        Planes list with #pl, snap, z.
    module : str
        Module name: 'df', 'dc', or 'igm'.
    input_path : str or Path
        Directory where flux/catalog files are located.
    filter_pos : int
        Index of filter used for centroid flux-weighting.
    fov_deg : float
        Field of view in degrees.
    res_as : float
        Resolution in arcseconds.

    Returns
    -------
    list of str
        List of generated catalog file paths.
    """
    inp = ascii.read(str(planes_file))
    snap = inp["snap"]
    pl = inp["pl"] - 1

    truenpix = int(fov_deg * 3600.0 / res_as) if res_as > 0 else 1024
    bufferpix = int(((truenpix + 1) * 20 / 14142))
    npix = truenpix + bufferpix

    generated_catalogs = []
    input_dir = Path(input_path)

    for i, j in zip(snap, pl):
        in_path = input_dir / f"flux.{module}.{i}_{j}.txt"
        out_path = input_dir / f"outcat.{module}.{i}_{j}.txt"

        if not in_path.is_file():
            continue

        data = load_particle_data(str(in_path))
        ncols = len(data)
        flux = []

        arrays = [[] for _ in range(ncols)]
        for row_idx in range(len(data[0])):
            for col_idx in range(ncols):
                arrays[col_idx].append(data[col_idx][row_idx])

        if module in ("dc", "igm"):
            idsh = [int(v) for v in arrays[0]]
            x = [int(int(arrays[1][k] * npix + 1) - bufferpix / 2.0 + 1) for k in range(len(data[0]))]
            y = [int(int(arrays[2][k] * npix + 1) - bufferpix / 2.0 + 1) for k in range(len(data[0]))]
            zred = arrays[3]
            mass = arrays[4]
            met = arrays[6]
            age = arrays[7]
            ZHI = arrays[8]
            NHI = arrays[9]
            npF = [int(v) for v in arrays[10]]
            npTNG = [int(v) for v in arrays[11]]

            nfilters = ncols - 12
            if ncols > 12:
                for k in range(12, nfilters + 12):
                    flux.append(arrays[k])

            fixed_cols = {
                "id": idsh, "x": x, "y": y, "zr": zred, "m": mass,
                "age": age, "met": met, "Npsh": npF, "NpTNG": npTNG,
                "ZHI": ZHI, "NHI": NHI
            }
            df = pd.DataFrame(fixed_cols)
            for k in range(nfilters):
                df[f"f{k}"] = flux[k]

        elif module == "df":
            idsh = [int(v) for v in arrays[0]]
            x = [int(int(arrays[1][k] * npix + 1) - bufferpix / 2.0 + 1) for k in range(len(data[0]))]
            y = [int(int(arrays[2][k] * npix + 1) - bufferpix / 2.0 + 1) for k in range(len(data[0]))]
            zred = arrays[3]
            mass = arrays[4]
            met = arrays[6]
            age = arrays[8]
            npTNG = [int(v) for v in arrays[9]]

            nfilters = ncols - 10
            if ncols > 10:
                for k in range(10, nfilters + 10):
                    flux.append(arrays[k])

            fixed_cols = {
                "id": idsh, "x": x, "y": y, "zr": zred, "m": mass,
                "age": age, "met": met, "NpTNG": npTNG
            }
            df = pd.DataFrame(fixed_cols)
            for k in range(nfilters):
                df[f"f{k}"] = flux[k]

        # Mass-weighted metallicity & age
        al = df.groupby("id").apply(lambda dfx: (dfx["met"] * dfx["m"]).sum() / dfx["m"].sum(), include_groups=False).reset_index()
        al.columns = ["id", "w_met"]

        al2 = df.groupby("id").apply(lambda dfx: (dfx["age"] * dfx["m"]).sum() / dfx["m"].sum(), include_groups=False).reset_index()
        al2.columns = ["id", "w_age"]

        h3 = df.groupby("id")["age"].max().reset_index()
        h3.columns = ["id", "o_age"]

        # Center weighted with flux
        xct = df.groupby("id").apply(lambda dfx: (dfx["x"] * dfx[f"f{filter_pos}"]).sum() / dfx[f"f{filter_pos}"].sum(), include_groups=False).reset_index()
        yct = df.groupby("id").apply(lambda dfx: (dfx["y"] * dfx[f"f{filter_pos}"]).sum() / dfx[f"f{filter_pos}"].sum(), include_groups=False).reset_index()
        xct.rename(columns={"id": "idx", 0: "x_c"}, inplace=True)
        yct.rename(columns={"id": "idy", 0: "y_c"}, inplace=True)
        dfc = pd.concat([xct["idx"], xct["x_c"], yct["y_c"]], axis=1)
        dfc.rename(columns={"idx": "id"}, inplace=True)
        df = df.merge(dfc, on="id", how="left")

        # Radius calculations
        df["dy"] = (df["y"] - df["y_c"]) ** 2
        df["dx"] = (df["x"] - df["x_c"]) ** 2
        df["R"] = (df["dx"] + df["dy"]) ** 0.5

        h2 = df.groupby("id")["R"].max().reset_index()
        h2.columns = ["id", "Rmax"]

        df = df.sort_values(["id", "R"])
        for k in range(nfilters):
            df[f"flux_cumsum{k}"] = df.groupby("id")[f"f{k}"].cumsum()
            df_half_flux = df.groupby("id").apply(lambda x: x[f"f{k}"].sum() / 2.0, include_groups=False).reset_index().rename(columns={0: f"half_flux{k}"})
            df = pd.merge(df, df_half_flux, how="left", on="id")
            df[f"flux_diff{k}"] = abs(df[f"half_flux{k}"] - df[f"flux_cumsum{k}"])
            df_new = df.loc[df.groupby("id")[f"flux_diff{k}"].idxmin()].reset_index()
            df_R = df_new[["id", "R"]].copy()
            df_R.columns = ["id", f"R_hl{k}"]
            df = pd.merge(df, df_R, how="left", on="id")

        if module in ("dc", "igm"):
            sumcols = ["m", "zr", "Npsh", "NpTNG", "ZHI", "NHI"] + [f"f{k}" for k in range(nfilters)] + [f"R_hl{k}" for k in range(nfilters)] + [f"half_flux{k}" for k in range(nfilters)]
        else:
            sumcols = ["m", "zr", "NpTNG"] + [f"f{k}" for k in range(nfilters)] + [f"R_hl{k}" for k in range(nfilters)] + [f"half_flux{k}" for k in range(nfilters)]

        g = df.groupby("id")[sumcols].sum().reset_index()

        for k in range(nfilters):
            filter_name = f"f{k}"
            df_filter = df.groupby("id").apply(lambda x: x[x["R"] < 3][filter_name].sum(), include_groups=False).reset_index()
            df_filter.columns = ["id", f"{filter_name}_3"]
            g = pd.merge(g, df_filter, how="left", on="id")

        g["w_met"] = al["w_met"]
        g["w_age"] = al2["w_age"]
        g["older_age"] = h3["o_age"]
        g["x_c"] = dfc["x_c"]
        g["y_c"] = dfc["y_c"]
        g["Rmax"] = h2["Rmax"]
        g["count"] = g["id"].map(df["id"].value_counts())
        g["av_zr"] = g["zr"] / g["count"]
        g["NPTNG"] = (g["NpTNG"] / g["count"]).astype(int)

        if module in ("dc", "igm"):
            g["NPsh"] = (g["Npsh"] / g["count"]).astype(int)
            g["Zhi"] = g["ZHI"] / g["count"]
            g["Nhi"] = g["NHI"] / g["count"]
        else:
            g["NPsh"] = g["count"]
            g["Zhi"] = 0.0
            g["Nhi"] = 0.0

        for k in range(nfilters):
            g[f"r_hlf{k}"] = g[f"R_hl{k}"] / g["count"]
            g[f"hlf{k}"] = g[f"half_flux{k}"] / g["count"]

        cols = ["id", "x_c", "y_c", "av_zr", "m", "w_met", "w_age", "older_age", "Rmax", "NPsh", "NPTNG", "Zhi", "Nhi"] + [f"f{k}" for k in range(nfilters)] + [f"f{k}_3" for k in range(nfilters)] + [f"hlf{k}" for k in range(nfilters)] + [f"r_hlf{k}" for k in range(nfilters)]

        with open(out_path, "w") as outfile:
            outfile.write("#")
        g[cols].to_csv(out_path, sep=" ", mode="a", index=False)
        generated_catalogs.append(str(out_path))

    return generated_catalogs
