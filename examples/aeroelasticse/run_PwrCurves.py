"""

Example script to compute the steady-state performance in OpenFAST

"""


from weis.aeroelasticse.runFAST_pywrapper import runFAST_pywrapper_batch
from weis.aeroelasticse.CaseGen_General import CaseGen_General
from weis.aeroelasticse.CaseLibrary import power_curve_control
import numpy as np
import os, platform

def run_PwrCurves(turbine_model,control_input,run_directory,n_cores=1):
    # Run Power Curve Sims, using power_curve_control() in CaseLibrary.py
    # turbine_model: fixed, floating -> correspond to the examples in here
    # control_input: discon filename
    # run_directory: where sims are run, outputs placed

    # Paths calling the standard modules of WEIS
    fastBatch                   = runFAST_pywrapper_batch(FAST_ver='OpenFAST', dev_branch=True)
    model_dir                   = os.path.join(os.path.dirname( os.path.dirname( os.path.realpath(__file__) ) ), 'OpenFAST_models')
    fastBatch.debug_level       = 2


    if turbine_model == 'fixed':
        fastBatch.FAST_directory    = os.path.join(model_dir, 'IEA-15-240-RWT/IEA-15-240-RWT-Monopile')   # Path to fst directory files
        fastBatch.FAST_InputFile    = 'IEA-15-240-RWT-Monopile.fst'   # FAST input file (ext=.fst)

    # run directory
    fastBatch.FAST_runDirectory = run_directory



    # Find the controller, if in WEIS
    # if platform.system() == 'Windows':
    #     path2dll = os.path.join(run_dir1, 'local/lib/libdiscon.dll')
    # elif platform.system() == 'Darwin':
    #     path2dll = os.path.join(run_dir1, 'local/lib/libdiscon.dylib')
    # else:
    #     path2dll = os.path.join(run_dir1, 'local/lib/libdiscon.so')


    path2ll = '/Users/dzalkind/Tools/ROSCO_toolbox/ROSCO/build/libdiscon_const_pwr.dylib'

    # Generate the matrix of cases
    weis_dir = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
    discon = "/Users/dzalkind/Tools/WEIS-3/ROSCO_toolbox/ROSCO_testing/DISCON-UMaineSemi_NoPS.IN"
    run_dir = os.path.join(weis_dir,'results','ct_nops')

    case_list, case_name_list, chan_list = power_curve_control(control_input,run_directory,'test',rosco_dll=path2ll)

    channels = {}
    for var in chan_list:
        channels[var] = True
    fastBatch.case_list         = case_list
    fastBatch.case_name_list    = case_name_list
    fastBatch.channels          = channels

    # Run OpenFAST, either serially or sequentially
    if n_cores == 1:
        fastBatch.run_serial()
    else:
        fastBatch.run_multi(n_cores)


if __name__ == "__main__":

    # directories
    weis_dir = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
    res_dir = os.path.join(weis_dir,'results')

    # set up cases
    turbine_mod = 'fixed'
    discon_list = ['/Users/dzalkind/Projects/CarbonTrust/Control_Inputs/DISCON_fixed_ps100.IN',
    '/Users/dzalkind/Projects/CarbonTrust/Control_Inputs/DISCON_fixed_ps080.IN']

    run_dir_list = ['fixed_ps100','fixed_ps080']

    for discon, run_dir in zip(discon_list,run_dir_list):
        run_PwrCurves(turbine_mod,discon,os.path.join(res_dir,run_dir),n_cores=4)
