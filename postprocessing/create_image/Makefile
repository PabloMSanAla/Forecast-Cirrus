# Executable name 
PROG = ./create_image

MAIN = create_image.cpp functions.cpp

# Conda paths (dynamically grabbed from active environment)
CONDA_PREFIX ?= $(shell echo "$$CONDA_PREFIX")
ifeq ($(wildcard $(CONDA_PREFIX)/include/CCfits),)
  ifneq ($(wildcard $(HOME)/miniforge3/envs/forecast/include/CCfits),)
    CONDA_PREFIX = $(HOME)/miniforge3/envs/forecast
  else ifneq ($(wildcard $(HOME)/miniconda3/envs/forecast/include/CCfits),)
    CONDA_PREFIX = $(HOME)/miniconda3/envs/forecast
  else ifneq ($(wildcard $(HOME)/anaconda3/envs/forecast/include/CCfits),)
    CONDA_PREFIX = $(HOME)/anaconda3/envs/forecast
  else ifneq ($(wildcard /opt/conda/include/CCfits),)
    CONDA_PREFIX = /opt/conda
  endif
endif

ifeq ($(CONDA_PREFIX),)
$(error CONDA_PREFIX is not set. Please activate your Conda environment: conda activate forecast)
endif

CONDA_INC = $(CONDA_PREFIX)/include
CONDA_LIB = $(CONDA_PREFIX)/lib

# Core Compiler and Standard Settings
UNAME_S := $(shell uname -s)
ifeq ($(UNAME_S),Darwin)
  # On macOS, use host clang++ to match host SDK headers and avoid Conda's clang/libc++ mismatch (__builtin_clzg)
  ifeq ($(findstring apple-darwin,$(CXX)),apple-darwin)
    CXX := clang++
  else ifeq ($(origin CXX),default)
    CXX := clang++
  endif
  CXXFLAGS := -std=c++17 -O2 -Wall

  CONDA_ARCH := $(shell file $(CONDA_LIB)/libc++.dylib 2>/dev/null | grep -q "x86_64" && echo "x86_64" || (file $(CONDA_LIB)/libc++.dylib 2>/dev/null | grep -q "arm64" && echo "arm64"))
  ifeq ($(CONDA_ARCH),)
    CONDA_ARCH := $(shell file $(CONDA_PREFIX)/bin/python 2>/dev/null | grep -q "x86_64" && echo "x86_64" || (file $(CONDA_PREFIX)/bin/python 2>/dev/null | grep -q "arm64" && echo "arm64"))
  endif
  ifneq ($(CONDA_ARCH),)
    ARCH_FLAGS ?= -arch $(CONDA_ARCH)
  endif
else
  CXX ?= g++
  CXXFLAGS ?= -std=c++17 -O2 -Wall
endif

CPPFLAGS = $(ARCH_FLAGS) -I$(CONDA_INC) -I$(CONDA_INC)/CCfits -I$(CONDA_INC)/eigen3 -I../../common -I./

# Linker Flags (Tells the loader to find libraries inside Conda at runtime)
LDFLAGS := $(ARCH_FLAGS) -L$(CONDA_LIB) -Wl,-rpath,$(CONDA_LIB)

# Libraries
LIBS = -lyaml-cpp -lcfitsio -lCCfits -lgsl -lgslcblas -lfftw3 -lm

RM = rm -f -r

default: main

main:
	$(CXX) $(CXXFLAGS) $(CPPFLAGS) $(MAIN) $(LDFLAGS) $(LIBS) -o $(PROG)

clean:
	$(RM) $(PROG) *.o *~ *.dSYM

.PHONY: default main clean

