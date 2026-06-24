#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

IMAGE="${WEIS_DOCKER_IMAGE:-ghcr.io/nlrwindsystems/weis:latest}"
HOST_WORKSPACE="${WEIS_DOCKER_MOUNT_DIR:-$(pwd -P)}"
CONTAINER_WORKSPACE="${WEIS_DOCKER_CONTAINER_WORKDIR:-/workspace}"
CONTAINER_RUN_DIR="${CONTAINER_WORKSPACE}"
JUPYTER_PORT="${WEIS_DOCKER_PORT:-8888}"
EXAMPLES_DEST_DEFAULT="${WEIS_DOCKER_EXAMPLES_DIR:-$(pwd -P)/weis-docker-examples}"

usage() {
    cat <<EOF
WEIS Docker host launcher

Usage:
  $(basename "$0") [HOST_OPTIONS] [entrypoint args...]
  $(basename "$0") [HOST_OPTIONS] lab [jupyter args...]
  $(basename "$0") [HOST_OPTIONS] notebook [jupyter args...]
  $(basename "$0") [HOST_OPTIONS] shell
  $(basename "$0") [HOST_OPTIONS] exec COMMAND [ARGS...]
  $(basename "$0") [HOST_OPTIONS] entrypoint-help
  $(basename "$0") [HOST_OPTIONS] copy-examples [host-dir]

Host options:
  --image IMAGE         Docker image to run.
                        Default: \$WEIS_DOCKER_IMAGE or ${IMAGE}
  --mount-dir PATH      Host directory to mount at ${CONTAINER_WORKSPACE}.
                        Default: \$WEIS_DOCKER_MOUNT_DIR or current directory
  --port PORT           Host/container port for lab/notebook.
                        Default: \$WEIS_DOCKER_PORT or ${JUPYTER_PORT}
  -h, --help            Show this help message.

Notes:
  - This launcher only manages Docker flags, mounts, and port publishing.
  - All WEIS, Jupyter, and MPI behavior stays inside docker/entrypoint/weis-container-entrypoint.
  - Host options must appear before the WEIS/Jupyter command and args.
  - You can download this script by itself and use it without checking out WEIS.

Examples:
  curl -O https://raw.githubusercontent.com/NLRWindSystems/WEIS/<ref>/docker/run-weis-docker.sh
  chmod +x run-weis-docker.sh
  export PATH="\$PWD:\$PATH"
  ./run-weis-docker.sh exec python --version
  ./run-weis-docker.sh entrypoint-help
  ./run-weis-docker.sh copy-examples
  cd weis-docker-examples
  run-weis-docker.sh --driver examples/12_controller_testbench/controller_testbench.py
  run-weis-docker.sh lab --notebook-dir /workspace/examples/12_controller_testbench
EOF
}

error() {
    echo "ERROR: $*" >&2
    echo >&2
    usage >&2
    exit 2
}

require_command() {
    command -v "$1" >/dev/null 2>&1 || error "Required command not found: $1"
}

abspath_existing_dir() {
    local dir="$1"
    [ -d "$dir" ] || error "Directory does not exist: $dir"
    (cd "$dir" && pwd -P)
}

abspath_parent_dir() {
    local path="$1"
    local parent
    parent="$(dirname "$path")"
    [ -d "$parent" ] || error "Parent directory does not exist: $parent"
    local base
    base="$(basename "$path")"
    printf '%s/%s\n' "$(cd "$parent" && pwd -P)" "$base"
}

has_option_with_value() {
    local option_name="$1"
    shift

    while [ "$#" -gt 0 ]; do
        case "$1" in
            "${option_name}"|"${option_name}"=*)
                return 0
                ;;
        esac
        shift
    done

    return 1
}

parse_host_options() {
    while [ "$#" -gt 0 ]; do
        case "$1" in
            -h|--help)
                usage
                exit 0
                ;;
            --image)
                [ "$#" -ge 2 ] || error "--image requires a value"
                IMAGE="$2"
                shift 2
                ;;
            --image=*)
                IMAGE="${1#*=}"
                shift
                ;;
            --mount-dir)
                [ "$#" -ge 2 ] || error "--mount-dir requires a value"
                HOST_WORKSPACE="$(abspath_existing_dir "$2")"
                shift 2
                ;;
            --mount-dir=*)
                HOST_WORKSPACE="$(abspath_existing_dir "${1#*=}")"
                shift
                ;;
            --port)
                [ "$#" -ge 2 ] || error "--port requires a value"
                JUPYTER_PORT="$2"
                shift 2
                ;;
            --port=*)
                JUPYTER_PORT="${1#*=}"
                shift
                ;;
            --)
                shift
                break
                ;;
            *)
                break
                ;;
        esac
    done

    REMAINING_ARGS=("$@")
}

docker_run_base() {
    docker run --rm -it \
        -v "${HOST_WORKSPACE}:${CONTAINER_WORKSPACE}" \
        -w "${CONTAINER_WORKSPACE}" \
        "$IMAGE" \
        "$@"
}

run_entrypoint_args() {
    if has_option_with_value "--workdir" "$@"; then
        docker_run_base "$@"
    else
        docker_run_base --workdir "${CONTAINER_RUN_DIR}" "$@"
    fi
}

run_jupyter_app() {
    local app="$1"
    shift

    local jupyter_args=("$@")
    if ! has_option_with_value "--notebook-dir" "${jupyter_args[@]}"; then
        jupyter_args+=(--notebook-dir "${CONTAINER_RUN_DIR}")
    fi

    docker run --rm -it \
        -p "${JUPYTER_PORT}:${JUPYTER_PORT}" \
        -v "${HOST_WORKSPACE}:${CONTAINER_WORKSPACE}" \
        -w "${CONTAINER_RUN_DIR}" \
        "$IMAGE" \
        "$app" \
        "${jupyter_args[@]}"
}

copy_examples() {
    local dest="${1:-$EXAMPLES_DEST_DEFAULT}"
    dest="$(abspath_parent_dir "$dest")"
    mkdir -p "$dest"

    docker run --rm -it \
        --entrypoint /usr/local/bin/_entrypoint.sh \
        -v "${dest}:${CONTAINER_WORKSPACE}" \
        "$IMAGE" \
        bash -lc 'cp -a /opt/WEIS/examples /workspace/'
}

main() {
    parse_host_options "$@"
    require_command docker
    set -- "${REMAINING_ARGS[@]}"

    case "${1:-}" in
        "")
            run_entrypoint_args
            ;;
        copy-examples)
            shift
            [ "$#" -le 1 ] || error "copy-examples accepts at most one destination path"
            copy_examples "${1:-}"
            ;;
        entrypoint-help)
            shift
            [ "$#" -eq 0 ] || error "entrypoint-help does not accept extra arguments"
            docker_run_base --help
            ;;
        shell|bash|exec)
            docker_run_base "$@"
            ;;
        lab|jupyter-lab|notebook)
            local app="$1"
            shift
            run_jupyter_app "${app}" "$@"
            ;;
        *)
            run_entrypoint_args "$@"
            ;;
    esac
}

main "$@"
