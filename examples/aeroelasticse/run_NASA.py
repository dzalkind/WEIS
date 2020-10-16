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
from weis.aeroelasticse.CaseGen_IEC         import CaseGen_IEC
# from weis.aeroelasticse.FAST_post import return_timeseries
from weis.aeroelasticse.runFAST_pywrapper  import runFAST_pywrapper, runFAST_pywrapper_batch

from shutil import copyfile

import numpy as np


def NASA_runFAST_CaseGenIEC(TMD):

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

        iec.transient_dir_change        = 'both'  # '+','-','both': sign for transient events in EDC, EWS
        iec.transient_shear_orientation = 'both'  # 'v','h','both': vertical or horizontal shear for EWS
        
    elif False:
        iec.dlc_inputs['DLC']   = [1.6,6.1,6.3,6.5]#,6.1,6.3]
        iec.dlc_inputs['U']     = [[20.,24.],[],[],[]] #[8,12,14,24]#,[],[]]  #[[10, 12, 14], [12]]
        iec.dlc_inputs['Seeds'] = [[5],[12],[50],[60]]#,[],[]] #[[5, 6, 7], []]
        iec.dlc_inputs['Yaw']   = [[],[],[],[]]#,[],[]]  #[[], []]
    else:  # reduced set
        iec.dlc_inputs['DLC']   = [6.5]#,6.1,6.3]
        iec.dlc_inputs['U']     = [[]] #[8,12,14,24]#,[],[]]  #[[10, 12, 14], [12]]
        iec.dlc_inputs['Seeds'] = [[69]]#,[],[]] #[[5, 6, 7], []]
        iec.dlc_inputs['Yaw']   = [[]]#,[],[]]  #[[], []]

    iec.uniqueSeeds = True
    iec.uniqueWaveSeeds = True
    # Set up TMD Case
    TMD_Case = TMD


    # Naming, file management, etc
    iec.wind_dir = '/Users/dzalkind/Tools/WEIS/outputs/NASA/dlc_test'
    iec.case_name_base = 'DLC_Test'
    iec.Turbsim_exe = '/Users/dzalkind/Tools/openfast/build/modules/turbsim/turbsim'
    iec.debug_level = 2
    iec.parallel_windfile_gen = True
    iec.cores = 4
    iec.run_dir = '/Users/dzalkind/Tools/WEIS/outputs/NASA/DLC_Play'
    iec.overwrite = True

    # Run case generator / wind file writing
    case_inputs = {}
    case_inputs[('Fst','OutFileFmt')] = {'vals':[1], 'group':0}   
    case_inputs[("Fst","OutFileFmt")]        = {'vals':[3], 'group':0}
    case_inputs[("Fst","TMax")]        = {'vals':[250], 'group':0}


    case_inputs[('ElastoDyn','YawDOF')] = {'vals':[False], 'group':0}

    # if TMD_Case == 'A':
    #     case_inputs[('ElastoDyn','PtfmCMzt')] = {'vals':[-2.8], 'group':0}
    #     case_inputs[('ElastoDyn','PtfmMass')] = {'vals':[1.52989E+07], 'group':0}
    #     case_inputs[('ElastoDyn','PtfmRIner')] = {'vals':[2.09344E+09], 'group':0}
    #     case_inputs[('ElastoDyn','PtfmPIner')] = {'vals':[2.09344E+09], 'group':0}
    #     case_inputs[('ElastoDyn','PtfmYIner')] = {'vals':[4.18455E+09], 'group':0}
    # elif TMD_Case == 'B':
    #     case_inputs[('ElastoDyn','PtfmCMzt')] = {'vals':[-2.8], 'group':0}
    #     case_inputs[('ElastoDyn','PtfmMass')] = {'vals':[1.54117E+07], 'group':0}
    #     case_inputs[('ElastoDyn','PtfmRIner')] = {'vals':[2.17492E+09], 'group':0}
    #     case_inputs[('ElastoDyn','PtfmPIner')] = {'vals':[2.17492E+09], 'group':0}
    #     case_inputs[('ElastoDyn','PtfmYIner')] = {'vals':[4.34751E+09], 'group':0}
    # elif TMD_Case == 'C':
    #     case_inputs[('ElastoDyn','PtfmCMzt')] = {'vals':[-2.8], 'group':0}
    #     case_inputs[('ElastoDyn','PtfmMass')] = {'vals':[1.61682E+07], 'group':0}
    #     case_inputs[('ElastoDyn','PtfmRIner')] = {'vals':[1.80011E+09], 'group':0}
    #     case_inputs[('ElastoDyn','PtfmPIner')] = {'vals':[1.80011E+09], 'group':0}
    #     case_inputs[('ElastoDyn','PtfmYIner')] = {'vals':[3.59751E+09], 'group':0}


    case_list, case_name_list, dlc_all = iec.execute(case_inputs=case_inputs)

    # Run FAST cases
    fastBatch.FAST_exe = '/Users/dzalkind/Tools/openfast-umaine/install/bin/openfast'   # Path to executable
    fastBatch.FAST_InputFile = 'NASA_Float.fst'   # FAST input file (ext=.fst)
    fastBatch.FAST_directory = '/Users/dzalkind/Projects/NASA/OF_Model_2'   # Path to fst directory files
    fastBatch.FAST_runDirectory = iec.run_dir
    fastBatch.Hull_TMD_File = 'Hull_TMD_Input.dat'

    # Add channels
    channels = {}
    for var in ["TipDxc1", "TipDyc1", "TipDzc1", "TipDxb1", "TipDyb1", "TipDxc2", "TipDyc2", "TipDzc2", "TipDxb2", "TipDyb2", "TipDxc3", "TipDyc3", "TipDzc3", "TipDxb3", "TipDyb3", "RootMxc1", "RootMyc1", "RootMzc1", "RootMxb1", "RootMyb1", "RootMxc2", "RootMyc2", "RootMzc2", "RootMxb2", "RootMyb2", "RootMxc3", "RootMyc3", "RootMzc3", "RootMxb3", "RootMyb3", "TwrBsMxt", "TwrBsMyt", "TwrBsMzt", "GenPwr", "GenTq", "RotThrust", "RtAeroCp", "RtAeroCt", "RotSpeed", "BldPitch1", "TTDspSS", "TTDspFA", "NacYaw", "Wind1VelX", "Wind1VelY", "Wind1VelZ", "LSSTipMxa","LSSTipMya","LSSTipMza","LSSTipMxs","LSSTipMys","LSSTipMzs","LSShftFys","LSShftFzs", "TipRDxr", "TipRDyr", "TipRDzr"]:
        channels[var] = True

    fastBatch.case_list = case_list
    fastBatch.case_name_list = case_name_list
    fastBatch.debug_level = 2
    fastBatch.dev_branch = True
    fastBatch.channels = channels

    fastBatch.run_serial()
    # fastBatch.run_multi(4)


if __name__=="__main__":

    # example_runFAST_pywrapper()
    #example_runFAST_pywrapper_batch()
    #example_runFAST_CaseGenIEC()

    TMD_Configs = ['']   #['','A','B','C']

    for TMD in TMD_Configs:
        NASA_runFAST_CaseGenIEC(TMD)
    # runFAST_TestROSCO()