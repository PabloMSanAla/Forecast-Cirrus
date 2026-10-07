# Top-level Makefile for FORECAST pipeline

PREFIX ?= $(HOME)/.local
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
	@mkdir -p $(BINDIR)
	@echo "Installing FORECAST CLI and tools to $(BINDIR)..."
	ln -sf $(CURDIR)/bin/forecast $(BINDIR)/forecast
	ln -sf $(CURDIR)/lc/executable_lc $(BINDIR)/executable_lc
	ln -sf $(CURDIR)/df/executable_df $(BINDIR)/executable_df
	ln -sf $(CURDIR)/dc/executable_dc $(BINDIR)/executable_dc
	ln -sf $(CURDIR)/igm/executable_igm $(BINDIR)/executable_igm
	ln -sf $(CURDIR)/postprocessing/create_image/create_image $(BINDIR)/create_image
	ln -sf $(CURDIR)/tools/make_lc_plane/make_lc_plane $(BINDIR)/make_lc_plane
	ln -sf $(CURDIR)/forecast.sh $(BINDIR)/forecast.sh
	@if [ -n "$$CONDA_PREFIX" ] && [ -d "$$CONDA_PREFIX/bin" ] && [ "$$CONDA_PREFIX/bin" != "$(BINDIR)" ]; then \
		echo "Also linking into Conda environment: $$CONDA_PREFIX/bin"; \
		ln -sf $(CURDIR)/bin/forecast "$$CONDA_PREFIX/bin/forecast"; \
		ln -sf $(CURDIR)/lc/executable_lc "$$CONDA_PREFIX/bin/executable_lc"; \
		ln -sf $(CURDIR)/df/executable_df "$$CONDA_PREFIX/bin/executable_df"; \
		ln -sf $(CURDIR)/dc/executable_dc "$$CONDA_PREFIX/bin/executable_dc"; \
		ln -sf $(CURDIR)/igm/executable_igm "$$CONDA_PREFIX/bin/executable_igm"; \
		ln -sf $(CURDIR)/postprocessing/create_image/create_image "$$CONDA_PREFIX/bin/create_image"; \
		ln -sf $(CURDIR)/tools/make_lc_plane/make_lc_plane "$$CONDA_PREFIX/bin/make_lc_plane"; \
		ln -sf $(CURDIR)/forecast.sh "$$CONDA_PREFIX/bin/forecast.sh"; \
	fi
	@echo "Installation complete. 'forecast' and module executables are now available in your PATH."

uninstall:
	@echo "Uninstalling FORECAST CLI tools from $(BINDIR)..."
	rm -f $(BINDIR)/forecast $(BINDIR)/executable_lc $(BINDIR)/executable_df $(BINDIR)/executable_dc $(BINDIR)/executable_igm $(BINDIR)/create_image $(BINDIR)/make_lc_plane $(BINDIR)/forecast.sh
	@if [ -n "$$CONDA_PREFIX" ] && [ -d "$$CONDA_PREFIX/bin" ] && [ "$$CONDA_PREFIX/bin" != "$(BINDIR)" ]; then \
		echo "Removing from Conda environment: $$CONDA_PREFIX/bin"; \
		rm -f "$$CONDA_PREFIX/bin/forecast" "$$CONDA_PREFIX/bin/executable_lc" "$$CONDA_PREFIX/bin/executable_df" "$$CONDA_PREFIX/bin/executable_dc" "$$CONDA_PREFIX/bin/executable_igm" "$$CONDA_PREFIX/bin/create_image" "$$CONDA_PREFIX/bin/make_lc_plane" "$$CONDA_PREFIX/bin/forecast.sh"; \
	fi
	@echo "Uninstallation complete."

clean:
	$(MAKE) -C lc clean
	$(MAKE) -C df clean
	$(MAKE) -C dc clean
	$(MAKE) -C igm clean
	$(MAKE) -C postprocessing/create_image clean
	$(MAKE) -C tools/make_lc_plane clean
	rm -f bin/executable_* bin/create_image bin/make_lc_plane forecast executable_lc executable_df executable_dc executable_igm
	$(MAKE) -C docs clean 2>/dev/null || true

docs: html

html:
	$(MAKE) -C docs html

test:
	python3 -m unittest discover -s tests -p "test_*.py" -v

