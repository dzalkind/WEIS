"""
A basic python script to setup and simulate the NASA FOWT with hull TMDs
"""
# Hacky way of doing relative imports
from __future__ import print_function
import os, sys, time
import multiprocessing as mp
# sys.path.insert(0, os.path.abspath(".."))

from weis.aeroelasticse.FAST_reader import InputReader_Common, InputReader_OpenFAST, InputReader_FAST7
from weis.aeroelasticse.FAST_writer import InputWriter_Common, InputWriter_OpenFAST, InputWriter_FAST7
from weis.aeroelasticse.FAST_wrapper import FastWrapper
from weis.aeroelasticse.NASA_TMD import NASA_TMD
from weis.aeroelasticse.CaseGen_IEC         import CaseGen_IEC
# from weis.aeroelasticse.FAST_post import return_timeseries
from weis.aeroelasticse.runFAST_pywrapper  import runFAST_pywrapper, runFAST_pywrapper_batch
from weis.aeroelasticse.Util.FileTools import load_case_matrix, load_yaml
from weis.aeroelasticse.CaseLibrary import *

from shutil import copyfile

import numpy as np


def NASA_runFAST_CaseGenIEC(test_case='no_mass',n_cores=1):

    iec         = CaseGen_IEC()
    fastBatch   = runFAST_pywrapper_batch(FAST_ver='OpenFAST')

    # Turbine Data
    iec.init_cond = {} # can leave as {} if data not available
    # iec.init_cond[("ElastoDyn","RotSpeed")] = {'U':[3., 4., 5., 6., 7., 8., 9., 10., 11., 12., 13., 14., 15., 16., 17., 18., 19., 20., 21., 22., 23., 24., 25]}
    # iec.init_cond[("ElastoDyn","RotSpeed")]['val'] = [6.972, 7.183, 7.506, 7.942, 8.469, 9.156, 10.296, 11.431, 11.89, 12.1, 12.1, 12.1, 12.1, 12.1, 12.1, 12.1, 12.1, 12.1, 12.1, 12.1, 12.1, 12.1, 12.1]
    # iec.init_cond[("ElastoDyn","BlPitch1")] = {'U':[3., 4., 5., 6., 7., 8., 9., 10., 11., 12., 13., 14., 15., 16., 17., 18., 19., 20., 21., 22., 23., 24., 25]}
    # iec.init_cond[("ElastoDyn","BlPitch1")]['val'] = [0., 0., 0., 0., 0., 0., 0., 0., 0., 3.823, 6.602, 8.668, 10.450, 12.055, 13.536, 14.920, 16.226, 17.473, 18.699, 19.941, 21.177, 22.347, 23.469]
    
    iec.init_cond[("ElastoDyn","RotSpeed")] = {'U':  [3.,   4.,   5.,   6.,   7.,   8.,   9.,  10., 11., 12., 13., 14., 15., 16., 17., 18., 19., 20., 21., 22., 23., 24., 25]}
    iec.init_cond[("ElastoDyn","RotSpeed")]['val'] = [4.99, 4.99, 4.99, 4.99, 4.99, 5.73, 6.44,7.15,7.55,7.55,7.55,7.55,7.55,7.55,7.55,7.55,7.55,7.55,7.55,7.55,7.55,7.55,7.55]
    iec.init_cond[("ElastoDyn","BlPitch1")] = {'U':[3., 4., 5., 6., 7., 8., 9., 10., 11., 12., 13., 14., 15., 16., 17., 18., 19., 20., 21., 22., 23., 24., 25]}
    iec.init_cond[("ElastoDyn","BlPitch1")]['val'] = [4., 3.7, 2.72, 1.19, 0., 0., 0., 3., 3., 3.823, 6.602, 8.668, 10.450, 12.055, 13.536, 14.920, 16.226, 17.473, 18.699, 19.941, 21.177, 22.347, 23.469]
    
    
    iec.init_cond[("ElastoDyn","BlPitch2")] = iec.init_cond[("ElastoDyn","BlPitch1")]
    iec.init_cond[("ElastoDyn","BlPitch3")] = iec.init_cond[("ElastoDyn","BlPitch1")]


    iec.init_cond[('HydroDyn','WaveHs')] = {'U': [4., 6., 8., 10., 12., 14., 16., 18., 20., 22., 24.]}
    iec.init_cond[('HydroDyn','WaveHs')]['val'] = [1.102,1.179,1.316,1.537,1.836,2.188,2.598,3.061,3.617,4.027,4.516]
    iec.init_cond[('HydroDyn','WaveTp')] = {'U': [4., 6., 8., 10., 12., 14., 16., 18., 20., 22., 24.]}
    iec.init_cond[('HydroDyn','WaveTp')]['val'] = [8.515,8.310,8.006,7.651,7.441,7.461,7.643,8.047,8.521,8.987,9.452]

    iec.Turbine_Class = 'II' # I, II, III, IV
    iec.Turbulence_Class = 'A'
    iec.D = 300.            #TODO: pull this info from fast file...do we know fast file?
    iec.z_hub = 150

    # DLC inputs
    iec.dlc_inputs = {}

    # full set
    if False:  
        iec.dlc_inputs['DLC']   = [1.2,1.6,6.1,6.3,6.5]#,6.1,6.3]
        iec.dlc_inputs['U']     = [[4,6,8,10,12,14,16,18,20,22,24],[4,6,8,10,12,14,16,18,20,22,24],[], \
                                        [],[]]#,[],[]]  #[[10, 12, 14], [12]]
        iec.dlc_inputs['Seeds'] = [[1,2,3,4,5,6],[11,12,13,14,15,16],[17,18,19,20,21,22],[23,24,25,26,27,28],\
                                        [29,30,31,32,33]]#,[],[]] #[[5, 6, 7], []]
        iec.dlc_inputs['WaveSeeds'] = [[1,2,3,4,5,6],[11,12,13,14,15,16],[17,18,19,20,21,22],[23,24,25,26,27,28],\
                                        [29,30,31,32,33]]
        iec.dlc_inputs['Yaw']   = [[],[],[],[],[]]#,[],[]]  #[[], []]
        iec.dlc_inputs['WaveDir'] = [[0.],[0.],[-90.,-45,0.,45,90.],[0.],[0.]]

        iec.transient_dir_change        = 'both'  # '+','-','both': sign for transient events in EDC, EWS
        iec.transient_shear_orientation = 'both'  # 'v','h','both': vertical or horizontal shear for EWS
        
    elif False:
        iec.dlc_inputs['DLC']   = [1.2,1.6,6.1,6.3,6.5]#,6.1,6.3]
        iec.dlc_inputs['U']     = [[8,12,24],[12,20.,24.],[],[],[]] #[8,12,14,24]#,[],[]]  #[[10, 12, 14], [12]]
        iec.dlc_inputs['Seeds'] = [[3],[5],[12],[50],[60]]#,[],[]] #[[5, 6, 7], []]
        iec.dlc_inputs['Yaw']   = [[],[],[],[],[]]#,[],[]]  #[[], []]
        iec.TMax    = 800

    elif True:   # c_tuning cases
        iec.dlc_inputs['DLC']   = [1.2,1.6]#,6.1,6.3]
        iec.dlc_inputs['U']     = [[12,14,16,24],[12,14,16,24],[],[],[]] #[8,12,14,24]#,[],[]]  #[[10, 12, 14], [12]]
        iec.dlc_inputs['Seeds'] = [[3],[5]]#,[],[]] #[[5, 6, 7], []]
        iec.dlc_inputs['Yaw']   = [[],[]]#,[],[]]  #[[], []]
        iec.TMax    = 800
    
    else:  # reduced set
        iec.dlc_inputs['DLC']   = [6.5]#,6.1,6.3]
        iec.dlc_inputs['U']     = [[]] #[8,12,14,24]#,[],[]]  #[[10, 12, 14], [12]]
        iec.dlc_inputs['Seeds'] = [[1,2,3,4,5,6]]#,[],[]] #[[5, 6, 7], []]
        iec.dlc_inputs['Yaw']   = [[]]#,[],[]]  #[[], []]

    iec.uniqueSeeds = True
    iec.uniqueWaveSeeds = True
    # Set up TMD Case
    # TMD_Case = TMD


    # Naming, file management, etc
    weis_dir     = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
    print(weis_dir)
    iec.wind_dir = os.path.join(weis_dir,'results','NASA','wind')
    iec.case_name_base = 'DLC'
    iec.Turbsim_exe = '/home/dzalkind/Tools/openfast-umaine/build/modules/turbsim/turbsim'
    iec.debug_level = 2
    if n_cores == 1:
        iec.parallel_windfile_gen = False
        iec.cores = 1
    else:
        iec.parallel_windfile_gen = True
        iec.cores = n_cores

    iec.run_dir = os.path.join(weis_dir,'results','NASA',test_case)
    iec.overwrite = False

    # print(iec.run_dir)

    # Run case generator / wind file writing
    case_inputs = {}
    case_inputs[('Fst','OutFileFmt')] = {'vals':[1], 'group':0}   
    case_inputs[("Fst","OutFileFmt")]        = {'vals':[2], 'group':0}
    # case_inputs[("Fst","TMax")]        = {'vals':[60], 'group':0}


    case_inputs[('ElastoDyn','YawDOF')] = {'vals':[False], 'group':0}

    # TMD Cases
    # no mass
    if test_case == 'no_mass':
        nt      = NASA_TMD()
        nt.mass_per_tank = 0
        nt.update_tmd_props()
        nt.write_tmd_input(os.path.join(iec.run_dir,'TMD_NoMass.dat'))
        case_inputs[('HydroDyn','TMDFile')] = {'vals':[os.path.join(iec.run_dir,'TMD_NoMass.dat')], 'group':0}

    # sweep natural frequency
    elif test_case == 'sweep_wn':
        w_sweep = np.linspace(0.05,1.55,num=24).tolist()

        nt      = NASA_TMD()
        tmd_files = []
        for i, w_tmd in enumerate(w_sweep):
            # write TMD File to directory
            # nt.damper_freq = w_tmd
            # nt.update_tmd_props()
            nt.period_control   = [0]
            nt.omega_control    = [w_tmd]
            tmd_con_filename    = os.path.join(iec.run_dir,'TMD_Con_w{:3.3f}.dat'.format(w_tmd)) 

            # tmd_filename = os.path.join(iec.run_dir,'TMD_Inp_w{:3.3f}.dat'.format(w_tmd)) 
            # tmd_filename = os.path.join(iec.run_dir,'TMD_Inp_{}.dat'.format(i)) 
            nt.write_tmd_control(tmd_con_filename)

            # collect name for case_input
            tmd_files.append(tmd_con_filename)

        case_inputs[('HydroDyn','TMDControlFile')] = {'vals':tmd_files, 'group':3}
        case_inputs[('HydroDyn','omega_TMD')] = {'vals':w_sweep, 'group':3}


    elif test_case == 'const_wn':
        nt      = NASA_TMD()
        
        nt.damper_freq = .44
        nt.update_tmd_props()
        
        nt.period_control   = [0]
        nt.omega_control    = [.44]
        tmd_con_filename    = os.path.join(iec.run_dir,'TMD_Con_w{:3.3f}.dat'.format(nt.damper_freq)) 
        
        nt.write_tmd_input(os.path.join(iec.run_dir,'TMD_Const.dat'))
        nt.write_tmd_control(tmd_con_filename)
        
        case_inputs[('HydroDyn','TMDFile')] = {'vals':[os.path.join(iec.run_dir,'TMD_Const.dat')], 'group':0}
        case_inputs[('HydroDyn','TMDControlFile')] = {'vals':[tmd_con_filename], 'group':0}

    elif test_case == 'as_shipped':
        nt      = NASA_TMD()
        
        nt.damper_freq = .9
        nt.update_tmd_props()
        
        nt.period_control   = [0]
        nt.omega_control    = [nt.damper_freq]
        tmd_con_filename    = os.path.join(iec.run_dir,'TMD_Con_w{:3.3f}.dat'.format(nt.damper_freq)) 
        
        nt.write_tmd_input(os.path.join(iec.run_dir,'TMD_Const.dat'))
        nt.write_tmd_control(tmd_con_filename)
        
        case_inputs[('HydroDyn','TMDFile')] = {'vals':[os.path.join(iec.run_dir,'TMD_Const.dat')], 'group':0}
        
    elif test_case == 'controlled_wn':
        nt                  = NASA_TMD()
        tmd_con_filename    = os.path.join(iec.run_dir,'TMD_BL_Control.dat')

        nt.write_tmd_control(tmd_con_filename)
        case_inputs[('HydroDyn','TMDControlFile')] = {'vals':[tmd_con_filename], 'group':0}


    elif test_case == 'c_pitch':
        TMD_Files = []

        # No Mass Case
        nt                  = NASA_TMD()
        TMD_Files.append(os.path.join(iec.run_dir,'TMD_NoMass.dat'))
        nt.mass_per_tank = 0
        nt.update_tmd_props()
        nt.write_tmd_input(TMD_Files[0])
        
        # Constant mass case
        nt                  = NASA_TMD()
        nt.damper_freq = .44
        nt.update_tmd_props()
        TMD_Files.append(os.path.join(iec.run_dir,'TMD_Const.dat'))
        nt.write_tmd_input(TMD_Files[1])
        
        nt.period_control   = [0]
        nt.omega_control    = [.44]
        tmd_con_filename    = os.path.join(iec.run_dir,'TMD_Con_w{:3.3f}.dat'.format(nt.damper_freq)) 
        
        nt.write_tmd_input(os.path.join(iec.run_dir,'TMD_Const.dat'))
        nt.write_tmd_control(tmd_con_filename)
        
        case_inputs[('HydroDyn','TMDFile')] = {'vals':TMD_Files, 'group':2}
        case_inputs[('HydroDyn','TMDControlFile')] = {'vals':[tmd_con_filename], 'group':0}


    
    # Make IEC cases
    case_list, case_name_list, dlc_all = iec.execute(case_inputs=case_inputs)

    # To set ideal control, loop through cases and extract Tp
    if test_case == 'ideal_wn':
        
        for case in case_list:
            nt = NASA_TMD()
            w_ideal             = nt.ideal_control(case[('HydroDyn','WaveTp')])
            nt.period_control   = [0]  # constant control
            nt.omega_control    = [w_ideal]
            tmd_con_filename    = os.path.join(iec.run_dir,'TMD_Con_w{:3.3f}.dat'.format(w_ideal))
            
            nt.write_tmd_control(tmd_con_filename)
            case[('HydroDyn','TMDControlFile')] = tmd_con_filename          


    # Run FAST cases
    fastBatch.FAST_exe = '/home/dzalkind/Tools/openfast-umaine/install/bin/openfast'   # Path to executable
    fastBatch.FAST_InputFile = 'NASA_Float.fst'   # FAST input file (ext=.fst)
    fastBatch.FAST_directory = os.path.join(os.path.dirname(os.path.dirname(__file__)),'OpenFAST_models/NASA_Float')
    fastBatch.FAST_runDirectory = iec.run_dir

    # Add channels
    channels = {}
    for var in ["TipDxc1", "TipDyc1", "TipDzc1", "TipDxb1", "TipDyb1", "TipDxc2", "TipDyc2", "TipDzc2", "TipDxb2", "TipDyb2", "TipDxc3", "TipDyc3", "TipDzc3", "TipDxb3", "TipDyb3", "RootMxc1", "RootMyc1", "RootMzc1", "RootMxb1", "RootMyb1", "RootMxc2", "RootMyc2", "RootMzc2", "RootMxb2", "RootMyb2", "RootMxc3", "RootMyc3", "RootMzc3", "RootMxb3", "RootMyb3", "TwrBsMxt", "TwrBsMyt", "TwrBsMzt", "GenPwr", "GenTq", "RotThrust", "RtAeroCp", "RtAeroCt", "RotSpeed", "BldPitch1", "TTDspSS", "TTDspFA", "NacYaw", "Wind1VelX", "Wind1VelY", "Wind1VelZ", "LSSTipMxa","LSSTipMya","LSSTipMza","LSSTipMxs","LSSTipMys","LSSTipMzs","LSShftFys","LSShftFzs", "TipRDxr", "TipRDyr", "TipRDzr"]:
        channels[var] = True

    fastBatch.case_list = case_list
    fastBatch.case_name_list = case_name_list
    fastBatch.debug_level = 2
    fastBatch.dev_branch = True
    fastBatch.channels = channels

    if n_cores == 1:
        fastBatch.run_serial()
    else:
        fastBatch.run_multi(n_cores)


if __name__=="__main__":

    # example_runFAST_pywrapper()
    #example_runFAST_pywrapper_batch()
    #example_runFAST_CaseGenIEC()
    
    # Test Cases
    # no_mass: turn off mass of TMDs (implemented, running)
    # as_shipped: what UM originall sent, no control
    # sweep_wn: sweep TMD of worst case
    # const_wn: set constant wn based on worst case
    # ideal_wn: set constant wn based on known sea state
    # controlled_wn: actively control wn
    # c_pitch: tune pitch controller w/ various TMD settings
    # c_peakshave: tune peak shaver w/ various TMD settings
    # c_fl_phase: tune floating feedback w/ various TMD settings
    # c_fl_gain: tune floating feedback w/ various TMD settings
    test_case = 'c_pitch'




    NASA_runFAST_CaseGenIEC(test_case,n_cores=8)
    # runFAST_TestROSCO()
