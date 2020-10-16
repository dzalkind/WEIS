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
from weis.aeroelasticse.CaseGen_General         import CaseGen_General
# from weis.aeroelasticse.FAST_post import return_timeseries
from weis.aeroelasticse.runFAST_pywrapper  import runFAST_pywrapper, runFAST_pywrapper_batch

from shutil import copyfile

import numpy as np


def runFAST_RAO_NASA(TMD):

    # iec         = CaseGen_General()

    # Set up FAST batch run
    fastBatch   = runFAST_pywrapper_batch(FAST_ver='OpenFAST')

    fastBatch.FAST_exe = '/Users/dzalkind/Tools/openfast-umaine/install/bin/openfast'   # Path to executable
    fastBatch.FAST_InputFile = 'NASA_Float.fst'   # FAST input file (ext=.fst)
    fastBatch.FAST_directory = '/Users/dzalkind/Projects/NASA/OF_Model_2'   # Path to fst directory files
    fastBatch.FAST_runDirectory = '/Users/dzalkind/Tools/WEIS/outputs/NASA/RAO_Play'
    fastBatch.Hull_TMD_File = 'Hull_TMD_Input.dat'

    # # Turbine Data
    # iec.init_cond = {} # can leave as {} if data not available
    # # iec.init_cond[("ElastoDyn","RotSpeed")] = {'U':[3., 4., 5., 6., 7., 8., 9., 10., 11., 12., 13., 14., 15., 16., 17., 18., 19., 20., 21., 22., 23., 24., 25]}
    # # iec.init_cond[("ElastoDyn","RotSpeed")]['val'] = [6.972, 7.183, 7.506, 7.942, 8.469, 9.156, 10.296, 11.431, 11.89, 12.1, 12.1, 12.1, 12.1, 12.1, 12.1, 12.1, 12.1, 12.1, 12.1, 12.1, 12.1, 12.1, 12.1]
    # # iec.init_cond[("ElastoDyn","BlPitch1")] = {'U':[3., 4., 5., 6., 7., 8., 9., 10., 11., 12., 13., 14., 15., 16., 17., 18., 19., 20., 21., 22., 23., 24., 25]}
    # # iec.init_cond[("ElastoDyn","BlPitch1")]['val'] = [0., 0., 0., 0., 0., 0., 0., 0., 0., 3.823, 6.602, 8.668, 10.450, 12.055, 13.536, 14.920, 16.226, 17.473, 18.699, 19.941, 21.177, 22.347, 23.469]
    
    # iec.init_cond[("ElastoDyn","RotSpeed")] = {'U':  [3.,   4.,   5.,   6.,   7.,   8.,   9.,  10., 11., 12., 13., 14., 15., 16., 17., 18., 19., 20., 21., 22., 23., 24., 25]}
    # iec.init_cond[("ElastoDyn","RotSpeed")]['val'] = [4.99, 4.99, 4.99, 4.99, 4.99, 5.73, 6.44,7.15,7.55,7.55,7.55,7.55,7.55,7.55,7.55,7.55,7.55,7.55,7.55,7.55,7.55,7.55,7.55]
    # iec.init_cond[("ElastoDyn","BlPitch1")] = {'U':[3., 4., 5., 6., 7., 8., 9., 10., 11., 12., 13., 14., 15., 16., 17., 18., 19., 20., 21., 22., 23., 24., 25]}
    # iec.init_cond[("ElastoDyn","BlPitch1")]['val'] = [4., 3.7, 2.72, 1.19, 0., 0., 0., 3., 3., 3.823, 6.602, 8.668, 10.450, 12.055, 13.536, 14.920, 16.226, 17.473, 18.699, 19.941, 21.177, 22.347, 23.469]
    
    
    # iec.init_cond[("ElastoDyn","BlPitch2")] = iec.init_cond[("ElastoDyn","BlPitch1")]
    # iec.init_cond[("ElastoDyn","BlPitch3")] = iec.init_cond[("ElastoDyn","BlPitch1")]


    # iec.init_cond[('HydroDyn','WaveHs')] = {'U': [4., 6., 8., 10., 12., 14., 16., 18., 20., 22., 24.]}
    # iec.init_cond[('HydroDyn','WaveHs')]['val'] = [1.102,1.179,1.316,1.537,1.836,2.188,2.598,3.061,3.617,4.027,4.516]

    # # These are swept in an RAO
    # # iec.init_cond[('HydroDyn','WaveTp')] = {'U': [4., 6., 8., 10., 12., 14., 16., 18., 20., 22., 24.]}
    # # iec.init_cond[('HydroDyn','WaveTp')]['val'] = [8.515,8.310,8.006,7.651,7.441,7.461,7.643,8.047,8.521,8.987,9.452]

    # iec.Turbine_Class = 'I' # I, II, III, IV
    # iec.Turbulence_Class = 'A'
    # iec.D = 240.            #TODO: pull this info from fast file...do we know fast file?
    # iec.z_hub = 150

    # # DLC inputs
    # iec.dlc_inputs = {}

    # Set up TMD Case
    TMD_Case = TMD


    # Naming, file management, etc
    # iec.wind_dir = '/Users/dzalkind/Tools/WEIS/outputs/NASA/wind'
    # iec.case_name_base = 'TMD_' + TMD_Case
    # iec.Turbsim_exe = '/Users/dzalkind/Tools/openfast/build/modules/turbsim/turbsim'
    # iec.debug_level = 2
    # iec.parallel_windfile_gen = True
    # iec.cores = 4
    # iec.run_dir = '/Users/dzalkind/Tools/WEIS/outputs/NASA/Testing/TMD_' + TMD_Case

    # Run case generator / wind file writing
    case_inputs = {}
    case_inputs[('Fst','OutFileFmt')] = {'vals':[1], 'group':0}   

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


    case_inputs[('Fst','TMax')] = {'vals':[2000.], 'group':0}
    case_inputs[('InflowWind','WindType')] = {'vals':[1], 'group':0}
    case_inputs[('InflowWind','HWindSpeed')] = {'vals':[24.], 'group':0}
    case_inputs[('HydroDyn','WaveMod')] = {'vals':[1], 'group':0}
    case_inputs[('HydroDyn','WaveHs')] = {'vals':[4.], 'group':0}


    wave_periods = np.linspace(3,30,20,endpoint=True).tolist()
    case_inputs[('HydroDyn','WaveTp')] = {'vals':wave_periods, 'group':1}
    
    #     case_inputs[('ElastoDyn','PtfmPIner')] = {'vals':[1.80011E+09], 'group':0}
    #     case_inputs[('ElastoDyn','PtfmYIner')] = {'vals':[3.59751E+09], 'group':0}

    case_list, case_name_list = CaseGen_General(case_inputs, dir_matrix=fastBatch.FAST_runDirectory, namebase='testing')


    fastBatch.case_list = case_list
    fastBatch.case_name_list = case_name_list
    fastBatch.debug_level = 2
    fastBatch.dev_branch = True

    # fastBatch.run_serial()
    fastBatch.run_multi(4)


if __name__=="__main__":

    # example_runFAST_pywrapper()
    #example_runFAST_pywrapper_batch()
    #example_runFAST_CaseGenIEC()

    TMD_Configs = ['']   #['','A','B','C']

    for TMD in TMD_Configs:
        runFAST_RAO_NASA(TMD)
    # runFAST_TestROSCO()