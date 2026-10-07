BREW_PREFIX ?= $(shell brew --prefix 2>/dev/null || echo /opt/homebrew)
CONDA_PREFIX ?= $(shell echo "$$CONDA_PREFIX")

CXX := clang++
CXXFLAGS := -std=c++17 -O2 -g

CPPFLAGS := -I../../common
LDFLAGS :=

# Prefer Homebrew on macOS if present, otherwise fallback to Conda
ifneq ($(wildcard $(BREW_PREFIX)/include/.*),)
CPPFLAGS += -I$(BREW_PREFIX)/include
LDFLAGS += -L$(BREW_PREFIX)/lib -Wl,-rpath,$(BREW_PREFIX)/lib
else ifneq ($(CONDA_PREFIX),)
CPPFLAGS += -I$(CONDA_PREFIX)/include
LDFLAGS += -L$(CONDA_PREFIX)/lib -Wl,-rpath,$(CONDA_PREFIX)/lib
endif

LIBS := -lyaml-cpp

PROG := make_lc_plane
SRCS := make_lc_plane.cpp

default: $(PROG)

$(PROG): $(SRCS)
	$(CXX) $(CXXFLAGS) $(CPPFLAGS) $(SRCS) $(LDFLAGS) $(LIBS) -o $(PROG)

clean:
	rm -f $(PROG) *.o *~

.PHONY: default clean
