#!/bin/bash

help() {
    cat << EOF

          ~~~~~  FORECAST LC module batch processing script  ~~~~~

This script runs the LC module for multiple planes in parallel using GNU parallel.
It reads the plane numbers and their corresponding snapshot numbers from planes_list.txt,
checks if the output catalog file already exists to avoid redundant computation,
and then runs executable_lc for each plane-snapshot pair in parallel.

Usage: ./lc.sh [options]

Options:
  -n: Number of processors to use (default: 1)
  -i: Initial plane number (default: 0)
  -lc: Path to the planes_list.txt file (default: from lc.ini or planes_list.txt)
  -ini: Path to the lc.ini file (default: lc.ini)
  -m, --mem: Memory ceiling in GB (default: 4.0)
  -j, --joblog: Path to file where GNU parallel logs job run statistics (e.g. parallel_lc.log)
  -r, --results: Directory path where stdout/stderr of each job is stored
  -f, --force: Force recomputation even if output file already exists
  -h, --help: Show this help message and exit

Example usage:
  ./lc.sh -n 4 -i 0
  ./lc.sh -n 4 -i 0 -j lc_jobs.log -r lc_logs/
  ./lc.sh -n 4 -i 10 -m 8.0 -f
  ./lc.sh -n 2 -ini /path/to/custom_lc.ini

EOF
}

num_processors=1  # Default number of processors
init_plane=0     # Default initial plane number
planes_list_path=""
ini_file="lc.ini"
memory_ceiling_gb=4.0
output_dir=""
force_run=false
joblog_file=""
results_dir=""

# Parse command line arguments
while [[ $# -gt 0 ]]; do
    case $1 in
        -h|--help)
            help
            exit 0
            ;;
        -n)
            num_processors="$2"
            shift 2
            ;;
        -i)
            init_plane="$2"
            shift 2
            ;;
        -max)
            max_plane_cli="$2"
            shift 2
            ;;
        -lc)
            planes_list_path="$2"
            shift 2
            ;;
        -ini|-c|--config)
            ini_file="$2"
            shift 2
            ;;
        -m|--mem)
            memory_ceiling_gb="$2"
            shift 2
            ;;
        -j|--joblog)
            joblog_file="$2"
            shift 2
            ;;
        -r|--results)
            results_dir="$2"
            shift 2
            ;;
        -f|--force)
            force_run=true
            shift
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

# 1. Resolve lc.ini path
if [ -n "$FORECAST_LC_INI" ] && [ -f "$FORECAST_LC_INI" ]; then
    ini_file="$FORECAST_LC_INI"
elif [ ! -f "$ini_file" ] && [ -f "lc/lc.ini" ]; then
    ini_file="lc/lc.ini"
fi

if [ ! -f "$ini_file" ]; then
    echo "Error: lc.ini configuration file not found at '$ini_file'."
    exit 1
fi

# 2. Extract output directory directly from lc.ini or YAML
if [[ "$ini_file" == *.yaml || "$ini_file" == *.yml ]]; then
    output_dir=$(python3 -c "import yaml; cfg=yaml.safe_load(open('$ini_file')); print(cfg.get('paths', {}).get('lc_output_dir', ''))" 2>/dev/null)
else
    output_dir=$(awk '/!...PATH_WHERE_TO_OUTPUT_RESULTS/{getline; print $1}' "$ini_file")
fi
if [ -z "$output_dir" ]; then
    echo "Error: Output directory not found in '$ini_file'."
    exit 1
fi
# Ensure trailing slash
[[ "$output_dir" != */ ]] && output_dir="${output_dir}/"

# 3. Resolve planes_list.txt path
if [ -z "$planes_list_path" ]; then
    if [ -n "$FORECAST_PLANES_LIST" ] && [ -f "$FORECAST_PLANES_LIST" ]; then
        planes_list_path="$FORECAST_PLANES_LIST"
    elif [[ "$ini_file" == *.yaml || "$ini_file" == *.yml ]]; then
        planes_list_path=$(python3 -c "import yaml; cfg=yaml.safe_load(open('$ini_file')); print(cfg.get('geometry', {}).get('planes_list_file', ''))" 2>/dev/null)
    elif [ -f "$ini_file" ]; then
        planes_list_path=$(awk '/!...PLANES_LIST_FILE/{getline; print $1}' "$ini_file")
    fi
    if [ -z "$planes_list_path" ] || [ ! -f "$planes_list_path" ]; then
        if [ -f "planes_list.txt" ]; then
            planes_list_path="planes_list.txt"
        elif [ -f "lc/planes_list.txt" ]; then
            planes_list_path="lc/planes_list.txt"
        elif [ -f "../lc/planes_list.txt" ]; then
            planes_list_path="../lc/planes_list.txt"
        fi
    fi
fi

if [ ! -f "$planes_list_path" ]; then
    echo "Error: planes_list.txt could not be found at '$planes_list_path'."
    exit 1
fi

nl=$(cat "$planes_list_path" | wc -l)
declare -a planes
declare -a snaps
for i in $(seq 0 $((nl-1)))
do
    # col 1 is display plane number (1-based), col 5 is replica index (0-based), col 6 is snapshot number
    planes[i]="$(cat "$planes_list_path" | awk -v p="$((i+1))" '{if(NR==p) print $5}')"
    snaps[i]="$(cat "$planes_list_path" | awk -v p="$((i+1))" '{if(NR==p) print $6}')"
done

max_planes=$(printf "%s\n" "${planes[@]}" | sort -nr | head -n 1)
if [ -n "$max_plane_cli" ]; then
    max_planes="$max_plane_cli"
fi

echo "Configuration:"
echo "  Planes list: $planes_list_path"
echo "  Output dir:  $output_dir"
echo "  Ini file:    $ini_file"
echo "  Processors:  $num_processors"
echo "  Plane range: $init_plane to $max_planes"
echo "  Memory limit:$memory_ceiling_gb GB"
[ -n "$joblog_file" ] && echo "  Job log:     $joblog_file"
[ -n "$results_dir" ] && echo "  Results dir: $results_dir"
echo "  Force rerun: $force_run"
echo ""

# Assemble extra GNU parallel arguments
parallel_args=()
if [ -n "$joblog_file" ]; then
    parallel_args+=(--joblog "$joblog_file")
fi
if [ -n "$results_dir" ]; then
    mkdir -p "$results_dir"
    parallel_args+=(--results "$results_dir")
fi

# Function to run executable_lc with existence check
run_lc() {
    local snapshot=$1
    local plane=$2
    local out_dir=$3
    local force=$4
    local ini_path=$5
    local mem_limit=$6

    local expected_output="${out_dir}coords.lc.${snapshot}_${plane}.txt"

    if [ "$force" != "true" ] && [ -s "$expected_output" ]; then
        echo "[SKIP] Output file already exists: $expected_output"
        return 0
    fi

    echo "Processing LC for snapshot: $snapshot with plane number: $plane"
    
    local flag="-ini"
    [[ "$ini_path" == *.yaml || "$ini_path" == *.yml ]] && flag="-c"
    local exe=""
    if command -v executable_lc >/dev/null 2>&1; then
        exe="$(command -v executable_lc)"
    elif [ -x "./executable_lc" ]; then
        exe="./executable_lc"
    elif [ -x "../lc/executable_lc" ]; then
        exe="../lc/executable_lc"
    elif [ -x "lc/executable_lc" ]; then
        exe="lc/executable_lc"
    fi
    "${exe}" "${snapshot}" "${plane}" "${mem_limit}" "${flag}" "${ini_path}"
    
    # Check if the command was successful
    if [ $? -ne 0 ]; then
        echo "Error processing snapshot: $snapshot with plane number: $plane."
        return 1
    fi
    return 0
}

export -f run_lc

# Generate pairs and run in parallel with GNU Parallel
for (( i = 0; i < $nl; i++ ))
do
    # Only process planes within range [init_plane, max_planes]
    if [[ "${planes[$i]}" -ge "$init_plane" && "${planes[$i]}" -le "$max_planes" ]];
    then
        echo "${snaps[$i]} ${planes[$i]} ${output_dir} ${force_run} ${ini_file} ${memory_ceiling_gb}"
    fi        
done | parallel --bar --jobs "$num_processors" "${parallel_args[@]}" --colsep ' ' run_lc {1} {2} {3} {4} {5} {6}


