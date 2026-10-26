# Top-level Makefile for FORECAST pipeline

# Conda paths (dynamically grabbed from active environment with fallbacks)
CONDA_PREFIX ?= $(shell echo "$$CONDA_PREFIX")
ifeq ($(wildcard $(CONDA_PREFIX)/include/H5Cpp.h),)
  ifneq ($(wildcard $(HOME)/miniforge3/envs/forecast/include/H5Cpp.h),)
    CONDA_PREFIX = $(HOME)/miniforge3/envs/forecast
  else ifneq ($(wildcard $(HOME)/miniconda3/envs/forecast/include/H5Cpp.h),)
    CONDA_PREFIX = $(HOME)/miniconda3/envs/forecast
  else ifneq ($(wildcard $(HOME)/anaconda3/envs/forecast/include/H5Cpp.h),)
    CONDA_PREFIX = $(HOME)/anaconda3/envs/forecast
  else ifneq ($(wildcard /opt/conda/include/H5Cpp.h),)
    CONDA_PREFIX = /opt/conda
  endif
endif
export CONDA_PREFIX

PREFIX ?= $(CONDA_PREFIX)
BINDIR ?= $(PREFIX)/bin

.PHONY: all clean lc df dc igm create_image make_lc_plane cli install uninstall docs html test help

all: lc df dc igm create_image make_lc_plane cli

lc:
	$(MAKE) -C lc

df:
	$(MAKE) -C df

dc:
	$(MAKE) -C dc

igm:
	$(MAKE) -C igm

create_image:
	$(MAKE) -C postprocessing/create_image

make_lc_plane:
	$(MAKE) -C tools/make_lc_plane

cli:
	chmod +x bin/forecast 2>/dev/null || true

install: all
	@if [ -z "$(CONDA_PREFIX)" ] || [ ! -d "$(CONDA_PREFIX)" ]; then \
		echo "Error: CONDA_PREFIX is not set or not a valid directory."; \
		echo "Please activate your Conda environment (e.g. 'conda activate forecast') before running 'make install'."; \
		exit 1; \
	fi
	@mkdir -p $(BINDIR)
	@echo "Installing FORECAST CLI and tools into Conda environment: $(BINDIR)..."
	ln -sf $(CURDIR)/bin/forecast $(BINDIR)/forecast
	ln -sf $(CURDIR)/lc/executable_lc $(BINDIR)/executable_lc
	ln -sf $(CURDIR)/df/executable_df $(BINDIR)/executable_df
	ln -sf $(CURDIR)/dc/executable_dc $(BINDIR)/executable_dc
	ln -sf $(CURDIR)/igm/executable_igm $(BINDIR)/executable_igm
	ln -sf $(CURDIR)/postprocessing/create_image/create_image $(BINDIR)/create_image
	ln -sf $(CURDIR)/tools/make_lc_plane/make_lc_plane $(BINDIR)/make_lc_plane
	ln -sf $(CURDIR)/forecast.sh $(BINDIR)/forecast.sh
	ln -sf $(CURDIR)/postprocessing/create_image/im.sh $(BINDIR)/im.sh
	@# Clean up legacy symlinks from ~/.local/bin so tools are only active when Conda is active
	@rm -f $(HOME)/.local/bin/forecast $(HOME)/.local/bin/executable_lc $(HOME)/.local/bin/executable_df \
	       $(HOME)/.local/bin/executable_dc $(HOME)/.local/bin/executable_igm $(HOME)/.local/bin/create_image \
	       $(HOME)/.local/bin/make_lc_plane $(HOME)/.local/bin/forecast.sh $(HOME)/.local/bin/im.sh 2>/dev/null || true
	@echo "Installing Python library (forecast) into Conda environment..."
	@python3 -m pip install -e . --no-deps --no-build-isolation 2>/dev/null || python3 -m pip install -e . --no-deps
	@echo "Installation complete."
	@echo "FORECAST C++ executables and Python library (forecast.postprocessing) are now available in your Conda environment."

uninstall:
	@echo "Uninstalling FORECAST CLI tools from $(BINDIR)..."
	rm -f $(BINDIR)/forecast $(BINDIR)/executable_lc $(BINDIR)/executable_df $(BINDIR)/executable_dc \
	      $(BINDIR)/executable_igm $(BINDIR)/create_image $(BINDIR)/make_lc_plane $(BINDIR)/forecast.sh $(BINDIR)/im.sh
	@rm -f $(HOME)/.local/bin/forecast $(HOME)/.local/bin/executable_lc $(HOME)/.local/bin/executable_df \
	       $(HOME)/.local/bin/executable_dc $(HOME)/.local/bin/executable_igm $(HOME)/.local/bin/create_image \
	       $(HOME)/.local/bin/make_lc_plane $(HOME)/.local/bin/forecast.sh $(HOME)/.local/bin/im.sh 2>/dev/null || true
	@python3 -m pip uninstall -y forecast-sim 2>/dev/null || true
	@echo "Uninstallation complete."

clean:
	$(MAKE) -C lc clean
	$(MAKE) -C df clean
	$(MAKE) -C dc clean
	$(MAKE) -C igm clean
	$(MAKE) -C postprocessing/create_image clean
	$(MAKE) -C tools/make_lc_plane clean
	rm -f bin/executable_* bin/create_image bin/make_lc_plane executable_lc executable_df executable_dc executable_igm
	$(MAKE) -C docs clean 2>/dev/null || true

docs: html

html:
	$(MAKE) -C docs html

test:
	python3 -m unittest discover -s tests -p "test_*.py" -v

