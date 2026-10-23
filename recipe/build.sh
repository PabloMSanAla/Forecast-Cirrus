#!/bin/bash
set -ex

# 1. Compile C++ modules
make all

# 2. Install C++ binaries and batch scripts into Conda bin directory
mkdir -p "${PREFIX}/bin"
cp lc/executable_lc "${PREFIX}/bin/"
cp df/executable_df "${PREFIX}/bin/"
cp dc/executable_dc "${PREFIX}/bin/"
cp igm/executable_igm "${PREFIX}/bin/"
cp postprocessing/create_image/create_image "${PREFIX}/bin/"
cp tools/make_lc_plane/make_lc_plane "${PREFIX}/bin/"
cp forecast.sh "${PREFIX}/bin/"
cp postprocessing/create_image/im.sh "${PREFIX}/bin/"
chmod +x "${PREFIX}/bin/"*

# 3. Install Python package and CLI console script entry point
${PYTHON} -m pip install . --no-deps --no-build-isolation -vv
