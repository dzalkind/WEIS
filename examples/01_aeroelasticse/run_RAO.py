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

def resp_amp_op(discon_file,runDir, namebase,rosco_dll='', U = 14, TMax = 2000):

    case_inputs = {}

    # Wave Stuff for RAO
    case_inputs[('Fst','TMax')] = {'vals':[TMax], 'group':0}
    if U:
        case_inputs[('InflowWind','WindType')] = {'vals':[1], 'group':0}
        case_inputs[('InflowWind','HWindSpeed')] = {'vals':[U], 'group':0}
    else:
        case_inputs[('Fst','CompInflow')] = {'vals':[0], 'group':0}
    case_inputs[('HydroDyn','WaveMod')] = {'vals':[1], 'group':0}
    case_inputs[('HydroDyn','WaveHs')] = {'vals':[1.], 'group':0}


    wave_periods = np.linspace(3,30,32,endpoint=True).tolist()
    case_inputs[('HydroDyn','WaveTp')] = {'vals':wave_periods, 'group':1}

        # Stop Generator from Turning Off
    case_inputs[('ServoDyn', 'GenTiStr')] = {'vals': ['True'], 'group': 0}
    case_inputs[('ServoDyn', 'GenTiStp')] = {'vals': ['True'], 'group': 0}
    case_inputs[('ServoDyn', 'SpdGenOn')] = {'vals': [0.], 'group': 0}
    case_inputs[('ServoDyn', 'TimGenOn')] = {'vals': [0.], 'group': 0}
    case_inputs[('ServoDyn', 'GenModel')] = {'vals': [1], 'group': 0}

    if not U:   # parked
        case_inputs[("ElastoDyn","GenDOF")]   = {'vals':["False"], 'group':0}
        case_inputs[("ElastoDyn","YawDOF")]   = {'vals':["False"], 'group':0}
        case_inputs[("ElastoDyn","RotSpeed")] = {'vals':[0.], 'group':0}
        case_inputs[("ElastoDyn","BlPitch1")] = {'vals':[90.], 'group':0}
        case_inputs[("ElastoDyn","BlPitch2")] = {'vals':[90.], 'group':0}
        case_inputs[("ElastoDyn","BlPitch3")] = {'vals':[90.], 'group':0}
        case_inputs[("ServoDyn","PCMode")]    = {'vals':[0], 'group':0}
        case_inputs[("AeroDyn15","AFAeroMod")]= {'vals':[1], 'group':0}
    

    # AeroDyn
    case_inputs[("AeroDyn15", "WakeMod")] = {'vals': [1], 'group': 0}
    case_inputs[("AeroDyn15", "AFAeroMod")] = {'vals': [2], 'group': 0}
    case_inputs[("AeroDyn15", "TwrPotent")] = {'vals': [0], 'group': 0}
    case_inputs[("AeroDyn15", "TwrShadow")] = {'vals': ['False'], 'group': 0}
    case_inputs[("AeroDyn15", "TwrAero")] = {'vals': ['False'], 'group': 0}
    case_inputs[("AeroDyn15", "SkewMod")] = {'vals': [1], 'group': 0}
    case_inputs[("AeroDyn15", "TipLoss")] = {'vals': ['True'], 'group': 0}
    case_inputs[("AeroDyn15", "HubLoss")] = {'vals': ['True'], 'group': 0}
    case_inputs[("AeroDyn15", "TanInd")] = {'vals': ['True'], 'group': 0}
    case_inputs[("AeroDyn15", "AIDrag")] = {'vals': ['True'], 'group': 0}
    case_inputs[("AeroDyn15", "TIDrag")] = {'vals': ['True'], 'group': 0}
    case_inputs[("AeroDyn15", "IndToler")] = {'vals': [1.e-5], 'group': 0}
    case_inputs[("AeroDyn15", "MaxIter")] = {'vals': [5000], 'group': 0}
    case_inputs[("AeroDyn15", "UseBlCm")] = {'vals': ['True'], 'group': 0}


    # Controller
    if rosco_dll:
        # Need to update this to ROSCO with power control!!!
        case_inputs[("ServoDyn","DLL_FileName")] = {'vals':[rosco_dll], 'group':0}

    # Control (DISCON) Inputs
    discon_vt = ROSCO_utilities.read_DISCON(discon_file)
    for discon_input in discon_vt:
        case_inputs[('DISCON_in',discon_input)] = {'vals': [discon_vt[discon_input]], 'group': 0}

    from weis.aeroelasticse.CaseGen_General import CaseGen_General
    case_list, case_name_list = CaseGen_General(case_inputs, dir_matrix=runDir, namebase=namebase)

    channels = set_channels()

    return case_list, case_name_list, channels


def run_RAO(turbine_model,control,save_dir,n_cores=1,U=14):
    
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
    name_base = 'const'

    # Set up cases from CaseLibrary
    case_list, case_name_list, channels = resp_amp_op(control,save_dir,name_base,rosco_dll=rosco_dll,U=U)

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
        model_dir                   = os.path.join(os.path.dirname( ( os.path.realpath(__file__) ) ), 'OpenFAST_models')


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
                    'CT-spar',
                    # 'NREL-5MW',
                    # 'UMaine-Fixed',
                    # 'CT-semi',
                    # 'UMaine-Semi'
                    ]
    discon_list = [
                    '/Users/dzalkind/Tools/WEIS-3/examples/01_aeroelasticse/OpenFAST_models/CT15MW-spar/ServoData/DISCON-CT-spar.IN',
                    # '/Users/dzalkind/Tools/WEIS-3/examples/OpenFAST_models/NREL-5MW/DISCON_5MW.IN',
                    # '/Users/dzalkind/Tools/WEIS-3/examples/OpenFAST_models/CT15MW-spar/ServoData/DISCON_CT-spar_ps080.IN',
                    # '/Users/dzalkind/Tools/WEIS-3/examples/01_aeroelasticse/OpenFAST_models/IEA-15-240-RWT/IEA-15-240-RWT-Monopile/DISCON-Monopile.IN',
                    # '/Users/dzalkind/Tools/WEIS-3/examples/OpenFAST_models/IEA-15-240-RWT/IEA-15-240-RWT-UMaineSemi/DISCON_fixed_ps100_const_pwr.IN',
                    # '/Users/dzalkind/Tools/WEIS-3/examples/OpenFAST_models/IEA-15-240-RWT/IEA-15-240-RWT-UMaineSemi/DISCON_fixed_ps100.IN',
                    ]

    # Options: simp, pwr_curve
    test_type   = 'RAO'

    wind_speeds = [0] #,8,14]

    save_dir_list    = [os.path.join(res_dir,tm,os.path.basename(dl).split('.')[0],test_type) \
        for tm, dl in zip(turbine_mods,discon_list)]

    for tm, co, sd in zip(turbine_mods,discon_list,save_dir_list):
        for ws in wind_speeds:
            sd = os.path.join(sd,'U{}'.format(ws))
            run_RAO(tm,co,sd,n_cores=1,U=ws)
    
    
    
    
