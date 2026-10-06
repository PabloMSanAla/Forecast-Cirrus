#############################################################################
# Makefile adapted for macOS Homebrew (Apple Silicon)
# - Uses Homebrew prefix for includes/libs
# - Uses clang++ by default and links against cfitsio, CCfits, gsl, fftw3
#############################################################################

# executable name 
PROG = ./create_image

MAIN = create_image.cpp functions.cpp

# Detect Homebrew prefix (fallback to /opt/homebrew for Apple Silicon)
BREW_PREFIX ?= $(shell brew --prefix 2>/dev/null || echo /opt/homebrew)

CXX := clang++
CXXFLAGS := -std=c++17 -O2 -g

# Include paths
CPPFLAGS := -I$(BREW_PREFIX)/include \
            -I$(BREW_PREFIX)/include/CCfits \
            -I$(BREW_PREFIX)/include/eigen3 \
            -I./

# Linker flags: search Homebrew libs and set rpath so runtime finds dynamic libraries
LDFLAGS := -L$(BREW_PREFIX)/lib -Wl,-rpath,$(BREW_PREFIX)/lib

# Libraries
LIBS := -lcfitsio -lCCfits -lgsl -lgslcblas -lfftw3 -lm

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

