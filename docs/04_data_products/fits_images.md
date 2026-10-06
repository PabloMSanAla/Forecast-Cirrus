# Scientific FITS Images

FORECAST produces publication-grade FITS images compatible with standard astronomical analysis tools (DS9, Astropy, SExtractor, Photutils).

---

## 1. Per-Plane FITS Images (`image.<snap>_<plane>_<filter>.fits`)
- **Format**: Single-extension FITS with 16-bit or 32-bit floating-point image arrays (`FLOAT32`).
- **Array Dimensions**: $N_{\text{pix}} \times N_{\text{pix}}$ (defined in `image.ini`).
- **Units**: Pixel values in microjanskys per pixel ($\mu\text{Jy}/\text{pixel}$) or surface brightness ($\text{mag}/\text{arcsec}^2$).

### Standard Header Keywords
```text
SIMPLE  =                    T / file does conform to FITS standard
BITPIX  =                  -32 / number of bits per data pixel
NAXIS   =                    2 / number of data axes
NAXIS1  =                 2048 / length of data axis 1 (X)
NAXIS2  =                 2048 / length of data axis 2 (Y)
CTYPE1  = 'RA---TAN'           / Gnomonic projection
CTYPE2  = 'DEC--TAN'           / Gnomonic projection
CRPIX1  =               1024.5 / Reference pixel in X
CRPIX2  =               1024.5 / Reference pixel in Y
CDELT1  =             -1.666E-5 / Pixel scale in X (deg/pix = 0.06 arcsec/pix)
CDELT2  =              1.666E-5 / Pixel scale in Y (deg/pix = 0.06 arcsec/pix)
CRVAL1  =                 0.00 / Reference RA (deg)
CRVAL2  =                 0.00 / Reference DEC (deg)
FILTER  = 'Roman_WFI_f158'     / Photometric bandpass
REDSHIFT=              0.54000 / Slice central redshift
BUNIT   = 'uJy/pixel'          / Brightness unit
```

---

## 2. Multi-Plane Stacks (`stacked_<filter>.fits`)
- Composite multi-plane deep-field mosaic covering the entire lightcone from $z = 0$ to $z_s$.
