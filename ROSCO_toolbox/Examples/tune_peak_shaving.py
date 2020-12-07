'''
----------- Example_07 --------------
Load saved turbine, tune controller, plot minimum pitch schedule
-------------------------------------

In this example:
  - Load a yaml file
  - Load a turbine from openfast
  - Tune a controller
  - Plot minimum pitch schedule
'''

# Python modules
import matplotlib.pyplot as plt 
import yaml, os
import numpy as np
# ROSCO toolbox modules 
from ROSCO_toolbox import controller as ROSCO_controller
from ROSCO_toolbox import turbine as ROSCO_turbine
from ROSCO_toolbox import sim as ROSCO_sim
from ROSCO_toolbox import utilities as ROSCO_utilities


def tune_peak_shaving(turbine_str,ps_level,Plot=False):
    # Load yaml file 
    if turbine_str == "fixed":
        parameter_filename = '/Users/dzalkind/Tools/WEIS-3/ROSCO_toolbox/Tune_Cases/IEA15MW_fixed.yaml'

        
    inps = yaml.safe_load(open(parameter_filename))
    path_params         = inps['path_params']
    turbine_params      = inps['turbine_params']
    controller_params   = inps['controller_params']

    # Ensure minimum generator speed at 50 rpm (for example's sake), turn on peak shaving and cp-maximizing min pitch
    # controller_params['PS_Mode']    = 1
    controller_params['ps_percent'] = ps_level

    # Instantiate turbine, controller, and file processing classes
    turbine         = ROSCO_turbine.Turbine(turbine_params)
    controller      = ROSCO_controller.Controller(controller_params)
    file_processing = ROSCO_utilities.FileProcessing()

    # Load turbine data from OpenFAST and rotor performance text file
    turbine.load_from_fast(path_params['FAST_InputFile'],path_params['FAST_directory'],dev_branch=True,rot_source='txt',txt_filename=path_params['rotor_performance_filename'])

    # Tune controller 
    controller.tune_controller(turbine)

    # Set max torque = rated torque
    turbine.max_torque = turbine.rated_torque
    print('here')

    # Plot minimum pitch schedule
    if Plot:
        plt.plot(controller.v, controller.pitch_op,label='Steady State Operation')
        plt.plot(controller.v, controller.ps_min_bld_pitch, label='Minimum Pitch Schedule')
        plt.legend()
        plt.xlabel('Wind speed (m/s)')
        plt.ylabel('Blade pitch (rad)')
        plt.show()

    # Write parameter input file
    param_dir  = '/Users/dzalkind/Projects/CarbonTrust/Control_Inputs'
    param_file = 'DISCON_{}_ps{:03d}.IN'.format(turbine_str,int(ps_level*100))   # This must be named DISCON.IN to be seen by the compiled controller binary. 
    file_processing.write_DISCON(turbine,controller,param_file=os.path.join(param_dir,param_file), txt_filename=path_params['rotor_performance_filename'])


if __name__ == "__main__":
    turbine = 'fixed'
    ps_list = np.arange(0.8,1.05,.05).tolist()

    for ps in ps_list:
        tune_peak_shaving(turbine,ps,Plot=False)


