"""

Example script to run the DLCs in OpenFAST

"""

from weis.aeroelasticse.runFAST_pywrapper   import runFAST_pywrapper, runFAST_pywrapper_batch
from weis.aeroelasticse.CaseGen_IEC         import CaseGen_IEC
from wisdem.commonse.mpi_tools              import MPI
from weis.aeroelasticse.CaseLibrary import *
import sys, os, platform
import numpy as np
from ROSCO_toolbox import utilities as ROSCO_utilities


def run_DLC_CT(turbine_model,control,save_dir,n_cores=1,tune=[],dlc_type='full'):
    # Turbine inputs
    iec = CaseGen_IEC()
    iec.overwrite           = False
    iec.Turbine_Class       = 'I'   # Wind class I, II, III, IV
    iec.Turbulence_Class    = 'B'   # Turbulence class 'A', 'B', or 'C'
    iec.D                   = 240.  # Rotor diameter to size the wind grid
    iec.z_hub               = 150.  # Hub height to size the wind grid
    cut_in                  = 4.    # Cut in wind speed
    cut_out                 = 25.   # Cut out wind speed
    n_ws                    = 3    # Number of wind speed bins
    TMax                    = 800.    # Length of wind grids and OpenFAST simulations, suggested 720 s
    Vrated                  = 10.59 # Rated wind speed
    Ttrans                  = max([0., TMax - 400.])  # Start of the transient for DLC with a transient, e.g. DLC 1.4
    TStart                  = 0 # Start of the recording of the channels of OpenFAST

    # Initial conditions to start the OpenFAST runs
    u_ref     = np.arange(3.,26.) # Wind speed
    pitch_ref = [0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 1.5058525323662666, 5.253759185225932, 7.50413344606208, 9.310153958810268, 10.8972969450052, 12.412247669440042, 13.883219268525659, 15.252012626933068, 16.53735488246438, 17.76456777500061, 18.953261878035104, 20.11055307762722, 21.238680277668898, 22.30705111326602, 23.455462501156205] # Pitch values in deg
    omega_ref = [2.019140272160114, 2.8047214918577925, 3.594541645994511, 4.359025795823625, 5.1123509774611025, 5.855691196288371, 6.589281196735111, 7.312788026081227, 7.514186181824161, 7.54665511646938, 7.573823812448151, 7.600476033113538, 7.630243938880304, 7.638301051122195, 7.622050377183605, 7.612285710588359, 7.60743945212863, 7.605865650155881, 7.605792924227456, 7.6062185247519825, 7.607153933765292, 7.613179734210654, 7.606737845170748] # Rotor speeds in rpm
    iec.init_cond = {}
    iec.init_cond[("ElastoDyn","RotSpeed")]        = {'U':u_ref}
    iec.init_cond[("ElastoDyn","RotSpeed")]['val'] = omega_ref
    iec.init_cond[("ElastoDyn","BlPitch1")]        = {'U':u_ref}
    iec.init_cond[("ElastoDyn","BlPitch1")]['val'] = pitch_ref
    iec.init_cond[("ElastoDyn","BlPitch2")]        = iec.init_cond[("ElastoDyn","BlPitch1")]
    iec.init_cond[("ElastoDyn","BlPitch3")]        = iec.init_cond[("ElastoDyn","BlPitch1")]
    iec.init_cond[("HydroDyn","WaveHs")]           = {'U':[3, 4, 6, 8, 10, 12, 14, 16, 18, 20, 22, 24, 25, 40, 50]}
    iec.init_cond[("HydroDyn","WaveHs")]['val']    = [1.101917033, 1.101917033, 1.179052649, 1.315715154, 1.536867124, 1.835816514, 2.187994638, 2.598127096, 3.061304068, 3.617035443, 4.027470219, 4.51580671, 4.51580671, 6.98, 10.7]
    iec.init_cond[("HydroDyn","WaveTp")]           = {'U':[3, 4, 6, 8, 10, 12, 14, 16, 18, 20, 22, 24, 25, 40, 50]}
    iec.init_cond[("HydroDyn","WaveTp")]['val']    = [8.515382435, 8.515382435, 8.310063688, 8.006300889, 7.6514231, 7.440581338, 7.460834063, 7.643300307, 8.046899942, 8.521314105, 8.987021024, 9.451641026, 9.451641026, 11.7, 14.2]
    iec.init_cond[("HydroDyn","PtfmSurge")]        = {'U':[3., 15., 25.]}
    iec.init_cond[("HydroDyn","PtfmSurge")]['val'] = [4., 15., 10.]
    iec.init_cond[("HydroDyn","PtfmPitch")]        = {'U':[3., 15., 25.]}
    iec.init_cond[("HydroDyn","PtfmPitch")]['val'] = [-1., 3., 1.3]
    iec.init_cond[("HydroDyn","PtfmHeave")]        = {'U':[3., 25.]}
    iec.init_cond[("HydroDyn","PtfmHeave")]['val'] = [0.5,0.5]

    # DLC inputs
    iec.dlc_inputs = {}
    if dlc_type == 'full':
        wind_speeds = np.arange(int(cut_in), int(cut_out), 2)
        iec.dlc_inputs['Seeds'] = [[1,2,3,4,5,6]]
        
    elif dlc_type == 'lite':
        wind_speeds = [12,14,16]
        iec.dlc_inputs['Seeds'] = [[25]]

    else:
        wind_speeds = [8]
        iec.dlc_inputs['Seeds'] = [[25]]


    # iec.dlc_inputs['Seeds'] = [range(1,7), range(1,7),[],[], range(1,7), range(1,7), range(1,7)]

    iec.dlc_inputs['DLC']   = [1.1]
    iec.dlc_inputs['U']     = [wind_speeds]
    
    iec.dlc_inputs['Yaw']   = [[]]
    iec.PC_MaxRat           = 2.
    iec.uniqueSeeds         = True
    iec.uniqueWaveSeeds     = True

    iec.TStart              = Ttrans
    iec.TMax                = TMax    # wind file length
    iec.transient_dir_change        = 'both'  # '+','-','both': sign for transient events in EDC, EWS
    iec.transient_shear_orientation = 'both'  # 'v','h','both': vertical or horizontal shear for EWS

    # Management of parallelization
    if MPI:
        from wisdem.commonse.mpi_tools import map_comm_heirarchical, subprocessor_loop, subprocessor_stop
        n_OF_runs = 0
        for i in range(len(iec.dlc_inputs['DLC'])):
            # Number of wind speeds
            if iec.dlc_inputs['DLC'][i] == 1.4: # assuming 1.4 is run at [V_rated-2, V_rated, V_rated] and +/- direction change
                if iec.dlc_inputs['U'][i] == []:
                    n_U = 6
                else:
                    n_U = len(iec.dlc_inputs['U'][i]) * 2
            elif iec.dlc_inputs['DLC'][i] == 5.1: # assuming 5.1 is run at [V_rated-2, V_rated, V_rated]
                if iec.dlc_inputs['U'][i] == []:
                    n_U = 3
                else:
                    n_U = len(iec.dlc_inputs['U'][i])
            elif iec.dlc_inputs['DLC'][i] in [6.1, 6.3]: # assuming V_50 for [-8, 8] deg yaw error
                if iec.dlc_inputs['U'][i] == []:
                    n_U = 2
                else:
                    n_U = len(iec.dlc_inputs['U'][i])
            else:
                n_U = len(iec.dlc_inputs['U'][i])
            # Number of seeds
            if iec.dlc_inputs['DLC'][i] == 1.4: # not turbulent
                n_Seeds = 1
            else:
                n_Seeds = len(iec.dlc_inputs['Seeds'][i])
            n_OF_runs += n_U*n_Seeds
            available_cores = MPI.COMM_WORLD.Get_size()
            n_parallel_OFruns = np.min([available_cores - 1, n_OF_runs])
            comm_map_down, comm_map_up, color_map = map_comm_heirarchical(1, n_parallel_OFruns)
            sys.stdout.flush()

    # Naming, file management, etc
    weis_dir            = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
    iec.wind_dir        = os.path.join(weis_dir,'wind/IEA-15MW')
    iec.case_name_base  = 'iea15mw'
    if MPI:
        iec.cores = available_cores
    else:
        iec.cores = n_cores

    iec.debug_level = 2
    if MPI:
        iec.parallel_windfile_gen = True
        iec.mpi_run               = True
        iec.comm_map_down         = comm_map_down
    else:
        if n_cores > 1:
            iec.parallel_windfile_gen = True
        else:
            iec.parallel_windfile_gen = False
        iec.mpi_run               = False
    iec.run_dir = save_dir

    # Run case generator / wind file writing
    case_inputs = {}
    case_inputs[("Fst","TMax")]              = {'vals':[TMax], 'group':0}
    case_inputs[("Fst","TStart")]            = {'vals':[TStart], 'group':0}
    case_inputs[("Fst","OutFileFmt")]        = {'vals':[2], 'group':0}
    # case_inputs[("ElastoDyn","TwFADOF1")]    = {'vals':["True"], 'group':0}
    # case_inputs[("ElastoDyn","TwFADOF2")]    = {'vals':["True"], 'group':0}
    # case_inputs[("ElastoDyn","TwSSDOF1")]    = {'vals':["True"], 'group':0}
    # case_inputs[("ElastoDyn","TwSSDOF2")]    = {'vals':["True"], 'group':0}
    # case_inputs[("ElastoDyn","FlapDOF1")]    = {'vals':["True"], 'group':0}
    # case_inputs[("ElastoDyn","FlapDOF2")]    = {'vals':["True"], 'group':0}
    # case_inputs[("ElastoDyn","EdgeDOF")]     = {'vals':["True"], 'group':0}
    # case_inputs[("ElastoDyn","DrTrDOF")]     = {'vals':["False"], 'group':0}
    # case_inputs[("ElastoDyn","GenDOF")]      = {'vals':["True"], 'group':0}
    # case_inputs[("ElastoDyn","YawDOF")]      = {'vals':["False"], 'group':0}
    # case_inputs[("ElastoDyn","PtfmSgDOF")]   = {'vals':["False"], 'group':0}
    # case_inputs[("ElastoDyn","PtfmSwDOF")]   = {'vals':["False"], 'group':0}
    # case_inputs[("ElastoDyn","PtfmHvDOF")]   = {'vals':["False"], 'group':0}
    # case_inputs[("ElastoDyn","PtfmRDOF")]    = {'vals':["False"], 'group':0}
    # case_inputs[("ElastoDyn","PtfmPDOF")]    = {'vals':["False"], 'group':0}
    # case_inputs[("ElastoDyn","PtfmYDOF")]    = {'vals':["False"], 'group':0}
    case_inputs[("ServoDyn","PCMode")]       = {'vals':[5], 'group':0}
    case_inputs[("ServoDyn","VSContrl")]     = {'vals':[5], 'group':0}

    # Stop Generator from Turning Off
    case_inputs[('ServoDyn', 'GenTiStr')] = {'vals': ['True'], 'group': 0}
    case_inputs[('ServoDyn', 'GenTiStp')] = {'vals': ['True'], 'group': 0}
    case_inputs[('ServoDyn', 'SpdGenOn')] = {'vals': [0.], 'group': 0}
    case_inputs[('ServoDyn', 'TimGenOn')] = {'vals': [0.], 'group': 0}
    case_inputs[('ServoDyn', 'GenModel')] = {'vals': [1], 'group': 0}

    # Specify rosco controller
    rosco_dll = '/Users/dzalkind/Tools/ROSCO_toolbox/ROSCO/build/libdiscon_carbon_trust.dylib'
    rosco_dll = ''

    if rosco_dll:
        case_inputs[("ServoDyn","DLL_FileName")] = {'vals':[rosco_dll], 'group':0}
    else:  #use WEIS controller
        run_dir1            = os.path.dirname( os.path.dirname( os.path.dirname( os.path.realpath(__file__) ) ) ) + os.sep
        if platform.system() == 'Windows':
            path2dll = os.path.join(run_dir1, 'local/lib/libdiscon.dll')
        elif platform.system() == 'Darwin':
            path2dll = os.path.join(run_dir1, 'local/lib/libdiscon.dylib')
        else:
            path2dll = os.path.join(run_dir1, 'local/lib/libdiscon.so')
        case_inputs[("ServoDyn","DLL_FileName")] = {'vals':[path2dll], 'group':0}

    # Control (DISCON) Inputs
    discon_vt = ROSCO_utilities.read_DISCON(control)
    for discon_input in discon_vt:
        case_inputs[('DISCON_in',discon_input)] = {'vals': [discon_vt[discon_input]], 'group': 0}

    # Control Tuning
    # load default params     
    # 
    if tune == 'pc_mode':     
        control_param_yaml  = os.path.join(weis_dir,'examples/OpenFAST_models/CT15MW-spar/ServoData/IEA15MW-CT-spar.yaml')
        omega = np.linspace(.05,.25,12,endpoint=True).tolist()
        zeta  = [2.25]
        control_case_inputs = sweep_pc_mode(control_param_yaml,omega,zeta,group=3)
        case_inputs.update(control_case_inputs)
    elif tune == 'max_tq':
        case_inputs[('DISCON_in','VS_MaxTq')] = {'vals': [19624046.66639, 1.5*19624046.66639], 'group': 3}

    # Aerodyn Params
    # case_inputs[("AeroDyn15","TwrAero")]     = {'vals':["True"], 'group':0}
    # case_inputs[("AeroDyn15","TwrPotent")]   = {'vals':[1], 'group':0}
    # case_inputs[("AeroDyn15","TwrShadow")]   = {'vals':["True"], 'group':0}
    # case_inputs[("Fst","CompHydro")]         = {'vals':[1], 'group':0}
    # case_inputs[("HydroDyn","WaveMod")]      = {'vals':[2], 'group':0}
    # case_inputs[("HydroDyn","WvDiffQTF")]    = {'vals':["False"], 'group':0}
    channels = {}
    for var in ["TipDxc1", "TipDyc1", "TipDzc1", "TipDxb1", "TipDyb1", "TipDxc2", "TipDyc2", \
         "TipDzc2", "TipDxb2", "TipDyb2", "TipDxc3", "TipDyc3", "TipDzc3", "TipDxb3", "TipDyb3", \
             "RootMxc1", "RootMyc1", "RootMzc1", "RootMxb1", "RootMyb1", "RootMxc2", "RootMyc2", \
                 "RootMzc2", "RootMxb2", "RootMyb2", "RootMxc3", "RootMyc3", "RootMzc3", "RootMxb3",\
                      "RootMyb3", "TwrBsMxt", "TwrBsMyt", "TwrBsMzt", "GenPwr", "GenTq", "RotThrust",\
                           "RtAeroCp", "RtAeroCt", "RotSpeed", "BldPitch1", "TTDspSS", "TTDspFA", \
                               "NcIMUTAxs", "NcIMUTAys", "NcIMUTAzs", "NcIMURAxs", "NcIMURAys", "NcIMURAzs", \
                                "NacYaw", "Wind1VelX", "Wind1VelY", "Wind1VelZ", "LSSTipMxa","LSSTipMya",\
                                   "LSSTipMza","LSSTipMxs","LSSTipMys","LSSTipMzs","LSShftFys","LSShftFzs", \
                                       "TipRDxr", "TipRDyr", "TipRDzr"]:
        channels[var] = True


    # Parallel file generation with MPI
    if MPI:
        comm = MPI.COMM_WORLD
        rank = comm.Get_rank()
    else:
        rank = 0
    if rank == 0:
        case_list, case_name_list, dlc_list = iec.execute(case_inputs=case_inputs)

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
                    'CT-TLP',
                    ]
    discon_list = [
                    '/Users/dzalkind/Tools/WEIS-3/examples/01_aeroelasticse/OpenFAST_models/CT15MW-TLP/ServoData/DISCON-CT-TLP.IN',
                    ]

    test_type_dir   = 'ntm'

    tune            = ''
    dlc_type        = ''

    if tune:
        test_type_dir += '+'+tune

    save_dir_list    = [os.path.join(res_dir,tm,os.path.basename(dl).split('.')[0],test_type_dir) \
        for tm, dl in zip(turbine_mods,discon_list)]

    for tm, co, sd in zip(turbine_mods,discon_list,save_dir_list):
        run_DLC_CT(tm,co,sd,n_cores=1,tune=tune,dlc_type=dlc_type)
    
    
