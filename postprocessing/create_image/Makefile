#############################################################################
# Makefile adapted for macOS Homebrew (Apple Silicon)
# - Uses Homebrew prefix for includes/libs
# - Uses clang++ by default and links against cfitsio, CCfits, gsl, fftw3
#############################################################################

# executable name 
PROG = ./create_image

MAIN = create_image.cpp functions.cpp

# Detect Homebrew and Conda prefixes
BREW_PREFIX ?= $(shell brew --prefix 2>/dev/null || echo /opt/homebrew)
CONDA_PREFIX ?= $(shell echo "$$CONDA_PREFIX")

CXX := clang++
CXXFLAGS := -std=c++17 -O2 -g

# Include paths
CPPFLAGS := -I../../common
LDFLAGS :=

# Prefer Homebrew on macOS if present, otherwise fallback to Conda
ifneq ($(wildcard $(BREW_PREFIX)/include/.*),)
CPPFLAGS += -I$(BREW_PREFIX)/include -I$(BREW_PREFIX)/include/CCfits -I$(BREW_PREFIX)/include/eigen3
LDFLAGS += -L$(BREW_PREFIX)/lib -Wl,-rpath,$(BREW_PREFIX)/lib
else ifneq ($(CONDA_PREFIX),)
CPPFLAGS += -I$(CONDA_PREFIX)/include -I$(CONDA_PREFIX)/include/CCfits -I$(CONDA_PREFIX)/include/eigen3
LDFLAGS += -L$(CONDA_PREFIX)/lib -Wl,-rpath,$(CONDA_PREFIX)/lib
endif

CPPFLAGS += -I./

# Libraries
LIBS := -lyaml-cpp -lcfitsio -lCCfits -lgsl -lgslcblas -lfftw3 -lm

# Default target
default: main

main:
	$(CXX) $(CXXFLAGS) $(CPPFLAGS) $(MAIN) $(LDFLAGS) $(LIBS) -o $(PROG)

# Check Homebrew and expected libraries
check:
	@echo "Homebrew prefix: $(BREW_PREFIX)"
	@test -d "$(BREW_PREFIX)" || (echo "Homebrew not found at $(BREW_PREFIX). Install Homebrew."; exit 1)
	@missing=""
	@for lib in libcfitsio libCCfits libgsl libfftw3; do \
	  if ls $(BREW_PREFIX)/lib/$$lib*.dylib > /dev/null 2>&1 || ls $(BREW_PREFIX)/lib/$$lib*.a > /dev/null 2>&1; then \
	    echo "$$lib: found"; \
	  else \
	    echo "$$lib: MISSING"; missing="yes"; \
	  fi; \
	done; \
	if [ -n "$$missing" ]; then echo "Some libraries missing. Install via Homebrew: brew install cfitsio ccfits gsl fftw"; exit 1; fi

clean:
	rm -f $(PROG) *.o *~

