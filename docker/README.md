# WEIS Docker Usage

This directory contains a host-side launcher for running a prebuilt WEIS image and an in-repo Dockerfile for developers who need to rebuild that image.

## Run A Prebuilt Image Without Cloning WEIS

If you only want to run WEIS, you do not need this repo locally. Download `run-weis-docker.sh` onto any machine that already has Docker and make it executable:

```bash
curl -O https://raw.githubusercontent.com/NLRWindSystems/WEIS/<ref>/docker/run-weis-docker.sh
chmod +x run-weis-docker.sh
export PATH="$PWD:$PATH"
```

By default the script uses `ghcr.io/nlrwindsystems/weis:latest`. Override that with `WEIS_DOCKER_IMAGE` or `--image` if you want a different tag.

See the built-in help for the full command surface:

```bash
./run-weis-docker.sh --help
./run-weis-docker.sh entrypoint-help
```

## Common Launcher Workflows

Smoke-test the image:

```bash
./run-weis-docker.sh exec python --version
./run-weis-docker.sh exec python -c "import weis, wisdem, raft, gmsh, pygmsh; print('imports ok')"
```

Copy WEIS examples out of the image:

```bash
./run-weis-docker.sh copy-examples
```

This creates `./weis-docker-examples` by default. To choose a different destination:

```bash
./run-weis-docker.sh copy-examples /tmp/weis-examples
```

The normal launcher workflow is to put the launcher on `PATH`, `cd` into the root of the workspace you want mounted as `/workspace`, and then run the script. That keeps the command line short because you do not need `--mount-dir` for the common case.

Run the controller testbench from copied examples:

```bash
cd weis-docker-examples
run-weis-docker.sh --driver examples/12_controller_testbench/controller_testbench.py
```

Start JupyterLab in the controller testbench directory:

```bash
cd weis-docker-examples
run-weis-docker.sh lab --notebook-dir /workspace/examples/12_controller_testbench
```

Open `http://localhost:8888/lab` after the container starts.

Use `--mount-dir` only when you want to run from one directory while mounting a different host directory into the container.

## Developer: Build The Image From This Repo

Build from the repo root so the Dockerfile can copy the checked-out WEIS tree into the image:

```bash
docker build -f docker/dockerfile -t weis:local .
```

This image installs WEIS from the local checkout, pins Python to `3.12`, installs the current Jupyter tooling, and keeps `docker/entrypoint/weis-container-entrypoint` as the in-container entrypoint.
