"""

Example script to run the DLCs in OpenFAST

"""

from weis.aeroelasticse.runFAST_pywrapper   import runFAST_pywrapper, runFAST_pywrapper_batch
from weis.aeroelasticse.CaseGen_IEC         import CaseGen_IEC
from weis.aeroelasticse.CaseLibrary         import *
from wisdem.commonse.mpi_tools              import MPI
import sys, os, platform
import numpy as np
from ROSCO_toolbox import utilities as ROSCO_utilities


def run_Simp(turbine_model,control,save_dir,n_cores=1):
    
    # Specify rosco controller
    rosco_dll = '' #'/Users/dzalkind/Tools/ROSCO_toolbox/ROSCO/build/libdiscon.dylib'

    if not rosco_dll: # use WEIS ROSCO
        run_dir1            = os.path.dirname( os.path.dirname( os.path.dirname( os.path.realpath(__file__) ) ) ) + os.sep
        if platform.system() == 'Windows':
            rosco_dll = os.path.join(run_dir1, 'local/lib/libdiscon.dll')
        elif platform.system() == 'Darwin':
            rosco_dll = os.path.join(run_dir1, 'local/lib/libdiscon.dylib')
        else:
            rosco_dll = os.path.join(run_dir1, 'local/lib/libdiscon.so')

    # Select case function
    if os.path.basename(save_dir) == 'simp':
        case_function = simp_step
        name_base = 'step'
    elif os.path.basename(save_dir) == 'pwr_curve':
        case_function = power_curve_control
        name_base = 'const'
    else:
        raise Exception('Test type not specified properly')

    # Set up cases from CaseLibrary
    case_list, case_name_list, channels = case_function(control,save_dir,name_base,rosco_dll=rosco_dll)

    # Management of parallelization, leave in for now
    if MPI:
        from wisdem.commonse.mpi_tools import map_comm_heirarchical, subprocessor_loop, subprocessor_stop
        n_OF_runs = len(case_list)

        available_cores = MPI.COMM_WORLD.Get_size()
        n_parallel_OFruns = np.min([available_cores - 1, n_OF_runs])
        comm_map_down, comm_map_up, color_map = map_comm_heirarchical(1, n_parallel_OFruns)
        sys.stdout.flush()

    # Naming, file management, etc
    weis_dir            = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))



    # Parallel file generation with MPI
    if MPI:
        comm = MPI.COMM_WORLD
        rank = comm.Get_rank()
    else:
        rank = 0
    if rank == 0:

        # Run FAST cases
        fastBatch                   = runFAST_pywrapper_batch(FAST_ver='OpenFAST',dev_branch = True)
        
        # Select Turbine Model
        model_dir                   = os.path.join(os.path.dirname( os.path.dirname( os.path.realpath(__file__) ) ), 'OpenFAST_models')


        fastBatch.select_CT_model(turbine_model,model_dir)
        
        fastBatch.channels          = channels
        fastBatch.FAST_runDirectory = save_dir  # input!
        fastBatch.case_list         = case_list
        fastBatch.case_name_list    = case_name_list
        fastBatch.debug_level       = 2
        fastBatch.FAST_exe          = '/Users/dzalkind/Tools/openfast-main/install/bin/openfast'

        if MPI:
            fastBatch.run_mpi(comm_map_down)
        else:
            if n_cores == 1:
                fastBatch.run_serial()
            else:
                fastBatch.run_multi(cores=n_cores)

    if MPI:
        sys.stdout.flush()
        if rank in comm_map_up.keys():
            subprocessor_loop(comm_map_up)
        sys.stdout.flush()

    # Close signal to subprocessors
    if rank == 0 and MPI:
        subprocessor_stop(comm_map_down)
    sys.stdout.flush()
    

if __name__ == "__main__":

    # directories
    weis_dir = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
    res_dir = os.path.join(weis_dir,'results')

    # set up cases
    turbine_mods = [
                    # 'UMaine-Fixed',
                    # 'CT-spar',
                    'NREL-5MW',
                    # 'UMaine-Fixed',
                    # 'CT-semi',
                    # 'UMaine-Semi'
                    ]
    discon_list = [
                    # '/Users/dzalkind/Tools/WEIS-3/examples/OpenFAST_models/CT15MW-spar/ServoData/DISCON_CT-spar_ps100.IN',
                    '/Users/dzalkind/Tools/WEIS-3/examples/OpenFAST_models/NREL-5MW/DISCON_5MW.IN',
                    # '/Users/dzalkind/Tools/WEIS-3/examples/OpenFAST_models/CT15MW-spar/ServoData/DISCON_CT-spar_ps080.IN',
                    # '/Users/dzalkind/Tools/WEIS-3/examples/OpenFAST_models/IEA-15-240-RWT/IEA-15-240-RWT-UMaineSemi/DISCON_fixed_ps100.IN',
                    # '/Users/dzalkind/Tools/WEIS-3/examples/OpenFAST_models/IEA-15-240-RWT/IEA-15-240-RWT-UMaineSemi/DISCON_fixed_ps100_const_pwr.IN',
                    # '/Users/dzalkind/Tools/WEIS-3/examples/OpenFAST_models/IEA-15-240-RWT/IEA-15-240-RWT-UMaineSemi/DISCON_fixed_ps100.IN',
                    ]

    # Options: simp, pwr_crv
    test_type   = 'simp'

    save_dir_list    = [os.path.join(res_dir,tm,os.path.basename(dl).split('.')[0],test_type) \
        for tm, dl in zip(turbine_mods,discon_list)]

    for tm, co, sd in zip(turbine_mods,discon_list,save_dir_list):
        run_Simp(tm,co,sd,n_cores=1)
    
    
    
    
