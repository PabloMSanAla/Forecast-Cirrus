#!/bin/bash
# Batch script to run the lightcone generation for multiple snapshots in parallel using GNU parallel

init_plane=36  # Starting plane number
max_planes=52  # Maximum number of planes to process in one run
num_processors=3  # Default number of processors

# Parse command line arguments
while [[ $# -gt 0 ]]; do
    case $1 in
        -n)
            num_processors="$2"
            shift 2
            ;;
        *)
            echo "Unknown option: $1"
            exit 1
            ;;
    esac
done

# Check if GNU parallel is installed
if ! command -v parallel &> /dev/null; then
    echo "GNU parallel is not installed. Please install it with: brew install parallel"
    exit 1
fi

# Create a temporary directory for plane files
PLANE_DIR=".plane_files"
mkdir -p "$PLANE_DIR"

# Clean up old plane files
rm -f "$PLANE_DIR"/*.d

# Pre-create all plane files with their respective plane numbers
for plane_num in $(seq $init_plane $max_planes); do
    echo $plane_num > "$PLANE_DIR/plane_${plane_num}.d"
done

echo "Starting batch processing with $num_processors processors"
echo "Processing planes $init_plane to $max_planes"
echo "Plane files created in directory: $PLANE_DIR"

# Define a function to run each plane
run_plane() {
    local plane_num=$1
    local plane_dir=$2
    echo "Processing plane number: $plane_num"
    
    # Run the lightcone generation with the unique plane file
    ./executable_lc $plane_num "$plane_dir/plane_${plane_num}"
    
    # Check if the command was successful
    if [ $? -ne 0 ]; then
        echo "Error processing plane number: $plane_num."
        return 1
    fi
    return 0
}

export -f run_plane

# Use GNU parallel to process planes in parallel
seq $init_plane $max_planes | parallel --jobs $num_processors run_plane {} "$PLANE_DIR"

echo "All planes processed."
echo "Cleaning up plane files in $PLANE_DIR..."
rm -rf "$PLANE_DIR"

