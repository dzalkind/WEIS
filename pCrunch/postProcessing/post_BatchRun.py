'''
A script to post process a batch run and generate stats and load rankings
'''

# Python Modules and instantiation
import numpy as np
import os

from weis.aeroelasticse.FAST_reader import InputReader_Common, InputReader_OpenFAST, InputReader_FAST7
from weis.aeroelasticse.FAST_writer import InputWriter_Common, InputWriter_OpenFAST, InputWriter_FAST7
from weis.aeroelasticse.runFAST_pywrapper import runFAST_pywrapper_batch
from weis.aeroelasticse.CaseGen_General import CaseGen_General
from weis.aeroelasticse.CaseGen_IEC import CaseGen_IEC
from pCrunch import pdTools
from pCrunch import Processing, Analysis


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
        fastRead[i] = InputReader_OpenFAST(FAST_ver='OpenFAST', dev_branch=True)
        fastFile[i] = os.path.join(test_dir[i],cm[i]['Case_Name'][0] + '.fst')
        fastRead[i].FAST_InputFile = os.path.basename(fastFile[i])   # FAST input file (ext=.fst)
        fastRead[i].FAST_directory = os.path.dirname(fastFile[i])   # Path to fst directory files
        fastRead[i].execute()
    
    # Set up pCrunch, run if not already
    reCrunch = False

    name_base = 'dataset1'
    # Do stats yaml exist?
    stat_yaml_there = [os.path.exists(os.path.join(test,'stats',name_base + '_stats.yaml')) for test in test_dir]

    outfiles = [[os.path.join(test, cn + '.outb') for cn in cm[0].Case_Name] for test in test_dir]



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
            fp[i_test].t0                       = 200         
            fp[i_test].parallel_analysis        = False
            fp[i_test].parallel_cores           = 8
    #         fp[i_test].DEL_info = [('TwrBsMyt', 4)]#, ('RootMyb2', 10), ('RootMyb3', 10)]


            fp[i_test].verbose                  = False
            fp[i_test].save_LoadRanking         = True
            fp[i_test].save_SummaryStats        = True
            
            fp[i_test].ranking_vars.append(['GenPwr']), fp[i_test].ranking_stats.append('max')
            fp[i_test].ranking_vars.append(['GenSpeed']), fp[i_test].ranking_stats.append('std')
            fp[i_test].ranking_vars.append(['TwrBsMyt']), fp[i_test].ranking_stats.append('max')
            fp[i_test].ranking_vars.append(['TwrBsMyt']), fp[i_test].ranking_stats.append('std')
            fp[i_test].ranking_vars.append(['TwrBsMxt']), fp[i_test].ranking_stats.append('max')
            fp[i_test].ranking_vars.append(['NcIMUTAxs']), fp[i_test].ranking_stats.append('std')
            fp[i_test].ranking_vars.append(['NcIMUTAys']), fp[i_test].ranking_stats.append('std')

            fp[i_test].channels_magnitude = {'TwrBsM': ['TwrBsMyt','TwrBsMxt']}

            stats[i_test], load_rankings[i_test] = fp[i_test].batch_processing()
            
        # re-load to get rid of dataset
        stats[i_test] = FileTools.load_yaml(os.path.join(os.path.join(test, 'stats'),name_base+'_stats.yaml'), package=1)
        load_rankings[i_test] = FileTools.load_yaml(os.path.join(os.path.join(test, 'stats'),name_base+'_LoadRanking.yaml'), package=1)

        # Turn into dataframe
        st[i_test] = pdTools.dict2df(stats[i_test])
        lr[i_test] = pdTools.dict2df(load_rankings[i_test])
    




    test_dir = [
        '/Users/dzalkind/Tools/WEIS-1/results/NASA/no_mass'
        ]


    post_BatchRun(test_dir)


# # Get wind speeds for processed runs
# windspeeds, seed, IECtype, cm_wind = Processing.get_windspeeds(cm, return_df=True)
# stats_df = pdTools.dict2df(stats)


# # Get AEP
# pp = Analysis.Power_Production()
# Vavg = 10   # Average wind speed of cite
# Vrange = [2,26] # Range of wind speeds being considered
# # bnums = int(len(set(windspeeds))/len(fp.namebase)) # Number of wind speeds per dataset for binning data
# bnums = len(fp.OpenFAST_outfile_list)
# pp.windspeeds = list(set(windspeeds))
# p = pp.gen_windPDF(Vavg, bnums, Vrange)
# AEP = pp.AEP(stats)
# print('AEP = {}'.format(AEP))

# # ========== Plotting ==========
# an_plts = Analysis.wsPlotting()
# #  --- Time domain analysis --- 
# filenames = [outfiles[0][2], outfiles[1][2]] # select the 2nd run from each dataset
# cases = {'Baseline': ['Wind1VelX', 'GenPwr', 'BldPitch1', 'GenTq', 'RotSpeed']}
# fast_dict = fast_io.load_fast_out(filenames, tmin=30)
# fast_pl.plot_fast_out(cases, fast_dict)

# # Plot some spectral cases
# spec_cases = [('RootMyb1', 0), ('TwrBsFyt', 0)]
# twrfreq = .0716
# fig,ax = fast_pl.plot_spectral(fast_dict, spec_cases, show_RtSpeed=True, 
#                         add_freqs=[twrfreq], add_freq_labels=['Tower'],
#                         averaging='Welch')
# ax.set_title('DLC1.1')

# # Plot a data distribution
# channels = ['RotSpeed']
# caseid = [0, 1]
# an_plts.distribution(fast_dict, channels, caseid, names=['DLC 1.1', 'DLC 1.3'])

# # --- Batch Statistical analysis ---
# # Bar plot
# fig,ax = an_plts.stat_curve(windspeeds, stats, 'RotSpeed', 'bar', names=['DLC1.1', 'DLC1.3'])

# # Turbulent power curve
# fig,ax = an_plts.stat_curve(windspeeds, stats, 'GenPwr', 'line', stat_idx=0, names=['DLC1.1'])

# plt.show()



