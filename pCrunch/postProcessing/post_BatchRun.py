'''
A script to post process a batch run and generate stats and load rankings
'''

# Python Modules and instantiation
import numpy as np
# from wisdem.aeroelasticse.CaseLibrary import ROSCO_Test
import os

# from weis.aeroelasticse.FAST_reader import InputReader_Common, InputReader_OpenFAST, InputReader_FAST7
# from weis.aeroelasticse.FAST_writer import InputWriter_Common, InputWriter_OpenFAST, InputWriter_FAST7
# from weis.aeroelasticse.runFAST_pywrapper import runFAST_pywrapper_batch

# from weis.aeroelasticse.CaseGen_General import CaseGen_General
# from weis.aeroelasticse.CaseGen_IEC import CaseGen_IEC
from pCrunch import pdTools
from pCrunch import Processing, Analysis
from weis.aeroelasticse.Util import FileTools
# Instantiate fast_IO
from ROSCO_toolbox import utilities as ROSCO_utilities
fast_io = ROSCO_utilities.FAST_IO()
fast_pl = ROSCO_utilities.FAST_Plots()
import pandas as pd

# Define input files paths
def post_BatchRun(test_dirs):

    # Load case matrix into dataframe
    case_matrix = [None] * len(test_dir)
    cm   = [None] * len(test_dir)
    fastFile  = [None] * len(test_dir)
    fastRead  = [None] * len(test_dir)

    for i, dir in enumerate(test_dir):
        case_matrix[i] = FileTools.load_yaml(os.path.join(test_dir[i],'case_matrix.yaml'), package=1)
        cm[i] = pd.DataFrame(case_matrix[i])

        # Get ALL FAST info
        # fastRead[i] = InputReader_OpenFAST(FAST_ver='OpenFAST', dev_branch=True)
        # fastFile[i] = os.path.join(test_dir[i],cm[i]['Case_Name'][0] + '.fst')
        # fastRead[i].FAST_InputFile = os.path.basename(fastFile[i])   # FAST input file (ext=.fst)
        # fastRead[i].FAST_directory = os.path.dirname(fastFile[i])   # Path to fst directory files
        # fastRead[i].execute()
    
    # Set up pCrunch, run if not already
    reCrunch = True

    name_base = 'dataset1'
    # Do stats yaml exist?
    stat_yaml_there = [os.path.exists(os.path.join(test,'stats',name_base + '_stats.yaml')) for test in test_dir]

    outfiles = [[os.path.join(test, cn + '.outb') for cn in cm[i_test].Case_Name] for i_test, test in enumerate(test_dir)]



    fp = [None]*len(test_dir)
    st = [None]*len(test_dir)
    lr = [None]*len(test_dir)
    stats = [None]*len(test_dir)
    load_rankings = [None]*len(test_dir)
    # Load and save statistics and load rankings
    for i_test, test in enumerate(test_dir):
        if not stat_yaml_there[i_test] or reCrunch:

            # Set some processing parameters
            fp[i_test] = Processing.FAST_Processing()
            fp[i_test].results_dir              = os.path.join(test, 'stats')
            fp[i_test].OpenFAST_outfile_list    = outfiles[i_test]
            # print(outfiles[i_test])

            fp[i_test].t0                       = 200         
            fp[i_test].parallel_analysis        = False
            fp[i_test].parallel_cores           = 36
    #         fp[i_test].DEL_info = [('TwrBsMyt', 4)]#, ('RootMyb2', 10), ('RootMyb3', 10)]


            fp[i_test].verbose                  = True
            fp[i_test].save_LoadRanking         = True
            fp[i_test].save_SummaryStats        = True
            
            fp[i_test].ranking_vars.append(['GenPwr']), fp[i_test].ranking_stats.append('max')
            fp[i_test].ranking_vars.append(['GenSpeed']), fp[i_test].ranking_stats.append('std')
            fp[i_test].ranking_vars.append(['TwrBsMyt']), fp[i_test].ranking_stats.append('max')
            fp[i_test].ranking_vars.append(['TwrBsMyt']), fp[i_test].ranking_stats.append('std')
            fp[i_test].ranking_vars.append(['TwrBsMxt']), fp[i_test].ranking_stats.append('max')
            fp[i_test].ranking_vars.append(['NcIMUTAxs']), fp[i_test].ranking_stats.append('std')
            fp[i_test].ranking_vars.append(['NcIMUTAys']), fp[i_test].ranking_stats.append('std')

            stats[i_test], load_rankings[i_test] = fp[i_test].batch_processing()
            
        # re-load to get rid of dataset
        stats[i_test] = FileTools.load_yaml(os.path.join(os.path.join(test, 'stats'),name_base+'_stats.yaml'), package=1)
        load_rankings[i_test] = FileTools.load_yaml(os.path.join(os.path.join(test, 'stats'),name_base+'_LoadRanking.yaml'), package=1)

        # Turn into dataframe
        st[i_test] = pdTools.dict2df(stats[i_test])
        lr[i_test] = pdTools.dict2df(load_rankings[i_test])
    


# if __name__ == '__main__':


test_dir = [
    # '/scratch/dzalkind/WEIS-3/results/CT-spar/DISCON-UMaineSemi/ntm+pc_mode',
    # '/scratch/dzalkind/WEIS-3/results/CT-barge/DISCON-CT-barge/ntm',
    # '/scratch/dzalkind/WEIS-3/results/CT-semi/DISCON-CT-semi/ntm',
    # '/scratch/dzalkind/WEIS-3/results/CT-spar/DISCON-CT-spar_hiBW/ntm',
    # '/scratch/dzalkind/WEIS-3/results/CT-spar/DISCON-CT-spar/ntm',
    '/Users/dzalkind/Tools/WEIS-3/results/CT-spar/DISCON-CT-spar_90/simp+pc_mode',
    # '/scratch/dzalkind/WEIS-3/results/CT-barge/DISCON-CT-barge_90/simp+pc_mode',
    # '/scratch/dzalkind/WEIS-3/results/CT-semi/DISCON-CT-semi_90/simp+pc_mode',
    # '/scratch/dzalkind/WEIS-3/results/CT-TLP/DISCON-CT-TLP_90/simp+pc_mode',
    # '/scratch/dzalkind/WEIS-3/results/CT-TLP/DISCON-UMaineSemi/ntm+pc_mode',
    # '/scratch/dzalkind/WEIS-3/results/CT-barge/DISCON-UMaineSemi/ntm+pc_mode',
    # '/scratch/dzalkind/WEIS-3/results/CT-barge/DISCON-CT-barge/simp+fl_gain',
    ]


post_BatchRun(test_dir)
