"""Controller Testbench — run OpenFAST DLC simulations and post-process results.

Usage
-----
1. Set ``input_file`` in :func:`main` to point at your testbench YAML.
2. Run::

       python controller_testbench.py          # serial
       mpirun -np 4 python controller_testbench.py  # parallel

Results are written to the ``output_directory`` specified in the YAML and can
be visualised with the companion ``WTCBench_Reporting.ipynb`` notebook.
"""

import os, sys
from weis.aeroelasticse.openmdao_openfast import FASTLoadCases
import weis.inputs as sch
from rosco import discon_lib_path
from openmdao.utils.mpi  import MPI
from weis.dlc_driver.dlc_generator    import DLCGenerator
import numpy as np
import logging
import shutil

if MPI:
    from weis.glue_code.mpi_tools import map_comm_heirarchical, subprocessor_loop, subprocessor_stop


this_dir = os.path.dirname( os.path.realpath(__file__) )
logger = logging.getLogger("wisdem/weis")


# =============================================================================
# USER CONFIGURATION — change the line below to point at your testbench YAML
# =============================================================================
INPUT_FILE = 'testbench_options_lite.yaml'
# =============================================================================


def _build_modeling_options(input_file):
    """Load and validate the testbench YAML, then reshape it into the
    ``modeling_options`` dict expected by :class:`FASTLoadCases`.

    Developer notes
    ---------------
    * The testbench schema (``testbench_schema.yaml``) uses ``$ref`` to share
      definitions with the full WEIS ``modeling_schema.yaml``.  Validation is
      two-pass: first against the testbench schema (populating testbench-only
      defaults), then against the merged WEIS schema (populating General,
      ROSCO, OpenFAST defaults, etc.).
    * Several keys that normally come from the WEIS GUI or driver are hard-
      coded here (``fst_vt``, ``materials``, ``flags``, ``from_openfast``).
    * ``OFmgmt`` is a convenience alias for
      ``testbench_options['General']['openfast_configuration']``; mutations to
      it are visible through the parent dict.
    """
    modopt_file = os.path.join(this_dir, input_file)
    testbench_options = sch.load_testbench_yaml(modopt_file)

    # -- internal bookkeeping for FASTLoadCases --
    testbench_options['General']['openfast_configuration']['fst_vt'] = {}
    testbench_options['fname_input_modeling'] = modopt_file
    testbench_options['materials'] = {}

    # -- turbine parameters (from YAML → OpenMDAO inputs) --
    inputs = {
        'V_cutin':          testbench_options['Turbine_Info']['wind_speed_cut_in'],
        'V_cutout':         testbench_options['Turbine_Info']['wind_speed_cut_out'],
        'Vrated':           testbench_options['Turbine_Info']['wind_speed_rated'],
        'hub_height':       testbench_options['Turbine_Info']['hub_height'],
        'Rtip':             testbench_options['Turbine_Info']['rotor_radius'],
        'rho':    1.225,
        'shearExp': 0.14,
        'lifetime': 25.,
    }
    inputs = {key: np.array([value]) for key, value in inputs.items()}

    discrete_inputs = {
        'turbine_class': testbench_options['Turbine_Info']['turbine_class'],
        'turbulence_class': testbench_options['Turbine_Info']['turbulence_class'],
    }

    testbench_options['flags'] = testbench_options['Turbine_Info']['flags']

    # -- ROSCO: skip tuning, use the DISCON already in the OpenFAST model --
    testbench_options['ROSCO']['flag'] = False

    # -- OpenFAST: always read from a pre-existing input set --
    testbench_options['OpenFAST']['flag'] = True
    testbench_options['OpenFAST']['from_openfast'] = True

    # -- OpenFAST management / execution settings --
    OFmgmt = testbench_options['General']['openfast_configuration']
    OFmgmt['cores']     = testbench_options['Testbench_Options'].get('n_cores', 1)
    OFmgmt['use_exe']   = True
    OFmgmt['allow_fails'] = True

    OFmgmt['FAST_exe']    = testbench_options['Testbench_Options'].get('FAST_exe', shutil.which('openfast'))
    OFmgmt['turbsim_exe'] = testbench_options['Testbench_Options'].get('turbsim_exe', shutil.which('turbsim'))
    OFmgmt['write_stdout'] = testbench_options['OpenFAST'].get('write_stdout', False)

    # -- controller library / DISCON --
    if testbench_options['Controller'] is not None and 'path2dll' in testbench_options['Controller']:
        OFmgmt['path2dll'] = testbench_options['Controller']['path2dll']
    else:
        logger.warning('No path2dll specified in testbench_options.yaml. Using default rosco path to dll.')
        OFmgmt['path2dll'] = discon_lib_path

    if testbench_options['Controller'] is not None and 'DISCON_in' in testbench_options['Controller']:
        OFmgmt['DISCON_in'] = testbench_options['Controller']['DISCON_in']
        OFmgmt['DISCON_in'] = os.path.join(os.path.dirname(modopt_file), OFmgmt['DISCON_in'])
        if not os.path.isfile(OFmgmt['DISCON_in']):
            raise FileNotFoundError(f"DISCON_in file not found: {OFmgmt['DISCON_in']}")
    else:
        logger.warning('No DISCON_in specified in testbench_options.yaml. Using DISCON input defined in OpenFAST input set.')

    # -- directories --
    OFmgmt['OF_run_fst'] = 'testbench'
    OFmgmt['OF_run_dir'] = os.path.join(os.path.dirname(modopt_file), testbench_options['Testbench_Options']['output_directory'])
    testbench_options['OpenFAST']['openfast_dir'] = os.path.join(os.path.dirname(modopt_file), testbench_options['OpenFAST']['openfast_dir'])

    # -- post-processing --
    OFmgmt['PostProcessing'] = testbench_options['PostProcessing']

    return testbench_options, inputs, discrete_inputs


def _run_testbench(input_file):
    """Execute the full testbench pipeline: load config → generate DLCs →
    run OpenFAST (optionally in parallel via MPI) → post-process → verify
    output files.

    Developer notes
    ---------------
    * MPI parallelism follows the WEIS hierarchical communicator pattern.
      Rank 0 drives the simulations; other ranks act as sub-processors.
    * After post-processing, expected output files are checked.  Missing files
      raise ``FileNotFoundError`` when running under pytest (detected via the
      ``PYTEST_CURRENT_TEST`` env var) and log a warning otherwise.
    """
    testbench_options, inputs, discrete_inputs = _build_modeling_options(input_file)

    logging.basicConfig(
        level=logging.DEBUG,
        format='%(asctime)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S',
    )

    OFmgmt = testbench_options['General']['openfast_configuration']

    # -- build DLC matrix --
    dlc_generator = DLCGenerator(
        metocean=testbench_options['DLC_driver']['metocean_conditions'],
        dlc_driver_options=testbench_options['DLC_driver'],
    )
    for DLCopt in testbench_options['DLC_driver']['DLCs']:
        dlc_generator.generate(DLCopt['DLC'], DLCopt)
    n_OF_runs = dlc_generator.n_cases

    # -- MPI setup --
    if MPI:
        opt_options = {
            'driver': {'design_of_experiments': {'flag': False}},
        }

        available_cores = MPI.COMM_WORLD.Get_size()
        n_parallel_OFruns = min([available_cores - 1, n_OF_runs])
        comm_map_down, comm_map_up, _ = map_comm_heirarchical(1, n_parallel_OFruns)

        OFmgmt['mpi_run'] = True
        OFmgmt['mpi_comm_map_down'] = comm_map_down

        rank = MPI.COMM_WORLD.Get_rank()

        if rank in comm_map_up.keys():
            subprocessor_loop(comm_map_up)
    else:
        opt_options = {}
        rank = 0

    # -- run simulations (rank 0 only) --
    if rank == 0:
        logging.info('Running controller testbench with input file: %s', input_file)
        if 'DISCON_in' in OFmgmt:
            logger.info('Using DISCON_in: %s', OFmgmt['DISCON_in'])
        sys.stdout.flush()

        flc = FASTLoadCases()
        flc.options['modeling_options'] = testbench_options
        flc.options['opt_options'] = opt_options
        flc.n_blades = 3
        flc.of_inumber = -1

        flc.setup_directories()
        flc.modopt_dir = os.path.dirname(flc.options['modeling_options']['fname_input_modeling'])

        fst_vt = flc.create_fst_vt(inputs, discrete_inputs)
        dlc_generator = flc.run_FAST(inputs, discrete_inputs, fst_vt)

        outputs = {}
        discrete_outputs = {}
        flc.post_process(dlc_generator, inputs, discrete_inputs, outputs, discrete_outputs)

        # -- verify expected output files --
        iteration_dir = os.path.join(OFmgmt['OF_run_dir'], 'iteration_0')
        expected_files = [
            'summary_stats.p',
            'DELs.p',
            'del_summary.yaml',
            'characteristic_loads.yaml',
            'aep_info.yaml',
        ]
        missing = [f for f in expected_files if not os.path.isfile(os.path.join(iteration_dir, f))]
        if missing:
            msg = f"Missing expected output files in {iteration_dir}: {missing}"
            if os.environ.get('PYTEST_CURRENT_TEST'):
                raise FileNotFoundError(msg)
            else:
                logger.warning(msg)
        else:
            logger.info('All expected output files present in %s', iteration_dir)

    if rank == 0 and MPI:
        subprocessor_stop(comm_map_down)
    sys.stdout.flush()


def main():
    _run_testbench(INPUT_FILE)


if __name__ == '__main__':
    main()
