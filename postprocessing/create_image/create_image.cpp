#include <cmath>
#include <chrono> 
#include <iostream>
#include <string>
#include <sstream>
#include <fstream>
#include <vector>
#include <iterator>
#include <algorithm>
#include <functional>
#include <stdio.h>     
#include <stdlib.h>     
#include <ctime>
#include <typeinfo>
#include <cassert>
#include <limits>
#include <memory>
#include <valarray>
#include <CCfits/CCfits>
#include <CCfits/FitsError.h>
#include <fitsio.h>
#include "functions.h"

/***************************************************************************/
/*                                                                         */
/*            postprocessing FORECAST - creating the raw image             */
/*                                                                         */
/*  if you use it or do any mods, please cite Fortuni et al. (2023).       */
/*                                         flaminia.fortuni@inaf.it        */
/*                                                                         */
/*                                                                         */  
/*  this is a postprocessing module for the FORECAST code;                 */
/*  it creates the raw image from the particle catalog                     */
/*  it runs on one snapshot/plane per time.                                */
/*  - input: particle catalog created from either df,dc or igm module      */
/*  - output: raw image in the chosen filter, one snapshot/plane per time  */ 
/*                                                                         */
/*                                                                         */
/*  for a comprehensive guide of FORECAST, visit                           */
/*                          https://github.com/flaminiafortuni/FORECAST    */
/*  for a full description of the software                                 */     
/*       https://ui.adsabs.harvard.edu/abs/2023arXiv230519166F/abstract    */
/*                                                                         */   
/***************************************************************************/

using namespace std;
using namespace std::chrono;
using namespace CCfits;

const double h0 = 0.6774;

struct ImageParticle {
  float x;
  float y;
  float flux;
};

int main(int argc, char** argv) {
  auto start = high_resolution_clock::now();

  cout << "----------------------------------------------------------------------" << endl;
  cout << " " << endl; 
  cout << "   ------------------------------------------------------ " << endl;
  cout << "   -                                                    - " << endl;
  cout << "   -           2D Mapping Simulation Snapshot           - " << endl;
  cout << "   -                                                    - " << endl;
  cout << "   -               creating the final image             - " << endl;
  cout << "   ------------------------------------------------------ " << endl;

  // 1. CLI Parsing & Validation
  int sourceID = -1;
  int iplrestart = -1;
  double memory_ceiling_gb = 4.0;
  bool cli_mem_specified = false;
  string custom_ini = "";
  vector<string> positional_args;

  for (int i = 1; i < argc; i++) {
    string arg = argv[i];
    if (arg == "-ini" || arg == "-config" || arg == "-c") {
      if (i + 1 < argc) {
        custom_ini = argv[++i];
      } else {
        cerr << "Error: " << arg << " option requires a file path." << endl;
        exit(1);
      }
    } else if (arg == "-h" || arg == "--help") {
      cout << "Usage: " << argv[0] << " <snapshot> <plane_number> [memory_ceiling_gb] [-ini <image.ini> | -c <forecast.yaml>]" << endl;
      exit(0);
    } else {
      positional_args.push_back(arg);
    }
  }

  if (positional_args.size() < 2 || positional_args.size() > 3) {
    cerr << "Usage: " << argv[0] << " <snapshot> <plane_number> [memory_ceiling_gb] [-ini <image.ini> | -c <forecast.yaml>]" << endl;
    exit(1);
  }

  try {
    sourceID = std::stoi(positional_args[0]);
    iplrestart = std::stoi(positional_args[1]);
  } catch (...) {
    cerr << "Error: Both snapshot and plane number must be integers." << endl;
    exit(1);
  }

  if (sourceID < 0 || iplrestart < 0) {
    cerr << "Error: Snapshot and plane number must be non-negative integers." << endl;
    exit(1);
  }

  if (positional_args.size() == 3) {
    try {
      memory_ceiling_gb = std::stod(positional_args[2]);
      if (memory_ceiling_gb <= 0.0) {
        cerr << "Error: Memory ceiling must be a positive number." << endl;
        exit(1);
      }
      cli_mem_specified = true;
    } catch (...) {
      cerr << "Error: Memory ceiling must be a valid number." << endl;
      exit(1);
    }
  }

  // Startup memory check
  checkMemoryCeiling(memory_ceiling_gb);

  string snappl = std::to_string(sourceID);
  string plane = std::to_string(iplrestart);

  // Check if restart file exists (for legacy compatibility)
  std::string fileplstart = plane + ".d";
  std::ifstream infileplstart(fileplstart.c_str());
  if (infileplstart.is_open()) {
    cout << " I will read the restart file >> " << fileplstart << endl;
    infileplstart >> iplrestart;
    cout << " iplrestart = " << iplrestart << endl;
    infileplstart.close();
  }

  // 2. Read Configuration from YAML or image.ini
  float fov = 0.0f, res = 0.0f;
  string filter, filfilters, planes_file, module, catpath, rdir;
  double config_mem_gb = memory_ceiling_gb;

  readParameters(&fov, &res,
                 &filter,
                 &filfilters,
                 &planes_file,
                 &module,
                 &catpath,
                 &rdir,
                 &config_mem_gb,
                 custom_ini);

  if (!cli_mem_specified && config_mem_gb > 0.0) {
    memory_ceiling_gb = config_mem_gb;
  }

  cout << "Snapshot: " << sourceID << ", plane: " << iplrestart
       << ", memory ceiling: " << memory_ceiling_gb << " GB" << endl;

  // 3. Resolve and read planes_list.txt from configuration
  int n_pl = 0;
  float blD = 0.0f, blD2 = 0.0f, zsim = 0.0f, invh0 = 1.0f / h0;
  bool plane_matched = false;

  ifstream oplane(planes_file.c_str());
  if (oplane.is_open()) {
    int npl, reppl, blsnappl;
    float zpl, blDpl, blD2pl, zpltrue;
    
    while (oplane >> npl >> zpl >> blDpl >> blD2pl >> reppl >> blsnappl >> zpltrue) {
      if ((reppl == iplrestart || npl - 1 == iplrestart) && blsnappl == sourceID) {
        n_pl = npl;
        blD = blDpl;
        blD2 = blD2pl;
        zsim = zpl;
        plane_matched = true;
        break;
      }
    }
    oplane.close();
  } else {
    cerr << "Error: planes list file " << planes_file << " could not be opened." << endl;
    exit(2);
  }

  if (!plane_matched) {
    cerr << "Error: Snapshot " << sourceID << " and plane " << iplrestart
         << " do not match any entry in " << planes_file << "." << endl;
    exit(1);
  }

  // Pixels of the image
  unsigned long int truenpix = static_cast<unsigned long int>(fov * 3600.0f / res);
  int bufferpix = static_cast<int>(ceil((truenpix + 1) * 20 / 14142));
  unsigned long int npix = truenpix + bufferpix;
  int extrapixside = bufferpix / 2;
  double inv_dl = static_cast<double>(npix);

  cout << "N. pixels: " << truenpix << "; buffer pixels: " << bufferpix << endl;
  cout << endl;

  // 4. Read filter list from configuration
  cout << "... Reading filter list from " << filfilters << " ..." << endl;
  ifstream listfilter(filfilters.c_str());
  vector<string> nfilter;
  if (listfilter.is_open()) {
    string buta;
    while (listfilter >> buta) {
      nfilter.push_back(buta);
    }
    listfilter.close();
  } else {
    cerr << "Error: filter list file " << filfilters << " could not be opened." << endl;
    exit(2);
  }

  // Find filter position in filter list
  int pos = -1;
  int Nfilters = static_cast<int>(nfilter.size());
  for (int i = 0; i < Nfilters; i++) {
    if (nfilter[i] == filter) {
      pos = i;
      break;
    }
  }

  if (pos == -1) {
    cerr << "Error: filter '" << filter << "' not found in filter list file " << filfilters << "." << endl;
    exit(1);
  }

  // 5. Ingest input particle catalog with compact memory representation
  string filoutcat = catpath + "flux." + module + "." + snappl + "_" + plane + ".txt";
  cout << "... Reading input catalog (" << filoutcat << ") from " << module << " module ..." << endl;

  vector<ImageParticle> particles;
  ifstream ocf(filoutcat.c_str());
  if (!ocf.is_open()) {
    cerr << "Error: catalog file " << filoutcat << " does not exist." << endl;
    exit(2);
  }

  vector<char> cat_io_buf(65536);
  ocf.rdbuf()->pubsetbuf(cat_io_buf.data(), cat_io_buf.size());

  if (module == "dc" || module == "igm") {
    int shid, npsh, npshtng;
    float xi, yi, zri, mi, imi, ai, Zmi;
    double NHImi;
    long double meti;
    while (ocf >> shid >> xi >> yi >> zri >> mi >> imi >> meti >> ai >> Zmi >> NHImi >> npsh >> npshtng) {
      double target_flux = 0.0;
      double temp_val = 0.0;
      for (int cf = 0; cf < Nfilters; cf++) {
        if (ocf >> temp_val) {
          if (cf == pos) {
            target_flux = temp_val;
          }
        } else {
          break;
        }
      }
      particles.push_back({xi, yi, static_cast<float>(target_flux)});
      ocf.ignore(std::numeric_limits<std::streamsize>::max(), '\n');
    }
  } else if (module == "df") {
    int shid, NPTNG;
    float xi, yi, zri, mi, imi, ai, cmzsh;
    long double meti;
    while (ocf >> shid >> xi >> yi >> zri >> mi >> imi >> meti >> cmzsh >> ai >> NPTNG) {
      double target_flux = 0.0;
      double temp_val = 0.0;
      for (int cf = 0; cf < Nfilters; cf++) {
        if (ocf >> temp_val) {
          if (cf == pos) {
            target_flux = temp_val;
          }
        } else {
          break;
        }
      }
      particles.push_back({xi, yi, static_cast<float>(target_flux)});
      ocf.ignore(std::numeric_limits<std::streamsize>::max(), '\n');
    }
  } else {
    cerr << "Error: Unknown module '" << module << "'. Must be df, dc, or igm." << endl;
    exit(1);
  }
  ocf.close();

  checkMemoryCeiling(memory_ceiling_gb);

  int ntotxy4 = static_cast<int>(particles.size());
  cout << "N. particles: " << ntotxy4 << " at snapshot " << snappl << " and plane " << plane << endl;
  cout << endl;

  // 6. Dynamic RAM-Aware Slab Sizing & Streaming FITS Generation
  if (ntotxy4 > 0) {
    double current_rss_mb = getPeakRSS_MB();
    double target_ceiling_mb = memory_ceiling_gb * 1024.0;
    double available_slab_mb = (target_ceiling_mb - current_rss_mb) * 0.75;
    if (available_slab_mb < 256.0) available_slab_mb = 256.0;

    double bytes_per_row = static_cast<double>(truenpix) * sizeof(float);
    size_t rows_per_slab = static_cast<size_t>((available_slab_mb * 1024.0 * 1024.0) / bytes_per_row);
    if (rows_per_slab > truenpix) rows_per_slab = truenpix;
    if (rows_per_slab < 100) rows_per_slab = 100;

    const char* env_slab = std::getenv("FORECAST_IMAGE_ROWS_PER_SLAB");
    if (env_slab) {
      try {
        size_t forced_slab = std::stoull(env_slab);
        if (forced_slab > 0) rows_per_slab = forced_slab;
      } catch (...) {}
    }

    size_t num_slabs = (truenpix + rows_per_slab - 1) / rows_per_slab;
    double slab_mb = (rows_per_slab * truenpix * sizeof(float)) / (1024.0 * 1024.0);
    cout << "Dynamic RAM-aware slab sizing: " << rows_per_slab << " rows/slab ("
         << num_slabs << " slab" << (num_slabs > 1 ? "s" : "")
         << " total, memory ceiling = " << memory_ceiling_gb << " GB, "
         << "slab buffer = " << slab_mb << " MB)" << endl;

    long naxis = 2;
    long naxes[2] = { static_cast<long>(truenpix), static_cast<long>(truenpix) };
    string pixu = "flux [uJ]";
    string fileoutput = rdir + filter + "." + module + "." + snappl + "_" + plane + ".fits";

    cout << "@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@" << endl;
    cout << "@  ... Writing .fits file " << fileoutput << " ... @" << endl;
    cout << "@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@" << endl;
    cout << " " << endl;

    std::remove(fileoutput.c_str());
    std::unique_ptr<FITS> ffxy(new FITS(fileoutput, FLOAT_IMG, naxis, naxes));
    PHDU *phxy = &ffxy->pHDU();
    fitsfile* fptr = ffxy->fitsPointer();

    // Process each horizontal slab sequentially
    for (size_t s = 0; s < num_slabs; s++) {
      size_t y_start = s * rows_per_slab;
      size_t y_end = std::min(y_start + rows_per_slab, static_cast<size_t>(truenpix));
      size_t current_slab_rows = y_end - y_start;
      size_t slab_pix_count = current_slab_rows * truenpix;

      vector<float> slab_data(slab_pix_count, 0.0f);

      // Rasterize particles into this slab
      for (const auto& p : particles) {
        int grx = int(p.x * inv_dl) + 1;
        int gry = int(p.y * inv_dl) + 1;
        int pix_x = grx - extrapixside;
        int pix_y = gry - extrapixside;
        if (pix_y >= static_cast<int>(y_start) && pix_y < static_cast<int>(y_end) &&
            pix_x >= 0 && pix_x < static_cast<int>(truenpix)) {
          slab_data[(pix_y - y_start) * truenpix + pix_x] += p.flux;
        }
      }

      // Stream slab into FITS file via direct memory pointer (zero extra copies)
      long fpixel = 1 + static_cast<long>(y_start) * static_cast<long>(truenpix);
      int fits_status = 0;
      fits_write_img(fptr, TFLOAT, fpixel, static_cast<long>(slab_pix_count), slab_data.data(), &fits_status);
      if (fits_status != 0) {
        cerr << "Error writing FITS image slab (CFITSIO status: " << fits_status << ")" << endl;
        exit(2);
      }

      checkMemoryCeiling(memory_ceiling_gb);
    }

    // Add metadata header keywords
    phxy->addKey("N_PIXEL_BY_SIDE", truenpix, " ");
    phxy->addKey("BUFFER_PIXELS", bufferpix, " ");
    phxy->addKey("PIXELUNIT", pixu, " ");
    phxy->addKey("N_STELLAR_PARTICLES", ntotxy4, " ");
    phxy->addKey("FILTER", filter, " ");
    phxy->addKey("REDSHIFT", zsim, " ");
    phxy->addKey("PHYSICALSIZE_BY_SIDE", fov, "degrees ");
    phxy->addKey("Dl_LOW", blD * invh0, "comoving distance in Mpc");
    phxy->addKey("Dl_UP", blD2 * invh0, "comoving distance in Mpc");
    phxy->addKey("HUBBLE", h0, " ");
  }

  double final_peak_rss = getPeakRSS_MB();
  auto end = high_resolution_clock::now();
  duration<double> elapsed = end - start;

  cout << endl;
  cout << "Peak RSS: " << final_peak_rss << " MB (Enforced Ceiling: " << memory_ceiling_gb << " GB)" << endl;
  cout << "Execution time: " << elapsed.count() << " s (" << (elapsed.count() / 3600.0) << " h)" << endl;
  cout << "--------------------------" << endl;
  return 0;
}
