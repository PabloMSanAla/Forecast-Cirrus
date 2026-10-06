CXX := clang++
CXXFLAGS := -std=c++17 -O2 -g

PROG := make_lc_plane
SRCS := make_lc_plane.cpp

default: $(PROG)

$(PROG): $(SRCS)
	$(CXX) $(CXXFLAGS) $(SRCS) -o $(PROG)

clean:
	rm -f $(PROG) *.o *~

.PHONY: default clean
