'''
----------- Example_12 --------------
Load a turbine, tune a controller, determine APC pitch lookup table
-------------------------------------

In this example:
  - Load a turbine from OpenFAST
  - Tune a controller
  - Write open loop inputs
  - Run simple simulation with open loop control

'''
# Python Modules
import yaml, os
# ROSCO toolbox modules 
from ROSCO_toolbox import controller as ROSCO_controller
from ROSCO_toolbox import turbine as ROSCO_turbine
from ROSCO_toolbox import sim as ROSCO_sim
from ROSCO_toolbox import utilities as ROSCO_utilities
from ROSCO_toolbox.ofTools.case_gen.CaseLibrary import power_curve_control
from ROSCO_toolbox.ofTools.case_gen.runFAST_pywrapper import runFAST_pywrapper_batch
from ROSCO_toolbox.ofTools.fast_io import output_processing

import numpy as np
import matplotlib.pyplot as plt

this_dir        = os.path.dirname(os.path.abspath(__file__))
rt_dir          = os.path.dirname(this_dir)
example_out_dir = os.path.join(this_dir,'examples_out')

# Load yaml file 
parameter_filename = '/Users/dzalkind/Tools/ROSCO_toolbox/Tune_Cases/IEA15MW_OL.yaml'
inps = yaml.safe_load(open(parameter_filename))
path_params         = inps['path_params']
turbine_params      = inps['turbine_params']
controller_params   = inps['controller_params']

# Instantiate turbine, controller, and file processing classes
turbine         = ROSCO_turbine.Turbine(turbine_params)
controller      = ROSCO_controller.Controller(controller_params)

# Load turbine data from OpenFAST and rotor performance text file
rt_dir = os.path.dirname(os.path.dirname(__file__))
turbine.load_from_fast(path_params['FAST_InputFile'], \
  os.path.join(rt_dir,path_params['FAST_directory']), \
    dev_branch=True,rot_source='txt', \
      txt_filename= os.path.join(rt_dir,path_params['FAST_directory'],path_params['rotor_performance_filename']))

# Tune controller 
controller.tune_controller(turbine)

# Plot open loop timeseries
fig,ax = controller.OpenLoopControl.plot_timeseries()


if False:
  plt.show()
else:
  fig.savefig(os.path.join(example_out_dir,'14_OL_Inputs.png'))


# Write parameter input file
param_file = 'examples_out/14_OL_DISCON.IN'   
ROSCO_utilities.write_DISCON(turbine,controller,param_file=param_file, txt_filename=path_params['rotor_performance_filename'])
# ROSCO_utilities.write_ol_power(controller,'/Users/dzalkind/Tools/ROSCO_toolbox/Examples/soft_start_example.dat')
# ROSCO_utilities.write_soft_cut_out(controller,'/Users/dzalkind/Tools/ROSCO_toolbox/Examples/soft_cut_out_example.dat')
# file_processing.write_ol_power(controller)


# Run OpenFAST Case:
# Constant wind speed (9 m/s)
rosco_dll = os.path.join(rt_dir,'ROSCO/build/libdiscon.dylib')
run_dir   = os.path.join(example_out_dir,'14_OL_Test')
if not os.path.exists(run_dir):
  os.makedirs(run_dir)
basename = 'OL_Test'

case_list, case_name_list, channels =  power_curve_control(param_file,run_dir, basename,rosco_dll=rosco_dll,U = [9])

fastBatch                   = runFAST_pywrapper_batch(FAST_ver='OpenFAST',dev_branch = True)
fastBatch.FAST_directory    = os.path.join(rt_dir,'Test_Cases/IEA-15-240-RWT-UMaineSemi')   # Path to fst directory files
fastBatch.FAST_InputFile    = 'IEA-15-240-RWT-UMaineSemi.fst'   # FAST input file (ext=.fst)       
fastBatch.channels          = channels
fastBatch.FAST_runDirectory = run_dir  # input!
fastBatch.case_list         = case_list
fastBatch.case_name_list    = case_name_list
fastBatch.debug_level       = 2
fastBatch.FAST_exe          = 'openfast'

fastBatch.run_serial()

# Load and plot
out_file = os.path.join(run_dir,basename+'_0.outb')

#  Define Plot cases 
cases = {}
cases['Baseline'] = ['Wind1VelX', 'BldPitch1', 'GenTq', 'RotSpeed','NacYaw']

op = output_processing.output_processing()
fastout = op.load_fast_out(out_file, tmin=0)
fix, ax = op.plot_fast_out(cases=cases,showplot=True)

if False:
  plt.show()
else:
  fig.savefig(os.path.join(example_out_dir,'14_OL_FAST_Out.png'))

if False: # Check yaw rate
  yaw_rate = controller.OpenLoopControl.ol_timeseries['yaw_rate']

  import scipy as sp
  f_yr    = sp.interpolate.interp1d(controller.OpenLoopControl.ol_timeseries['time'], \
                    controller.OpenLoopControl.ol_timeseries['yaw_rate'], \
                    fill_value = "extrapolate")

  yaw_rate = f_yr(fastout[0]['Time'])
  yaw = 0
  dt  = 0.025
  yaw = np.zeros(len(yaw_rate)+1)
  for i,yr in enumerate(yaw_rate):
    yaw[i+1] = yaw[i]+yr*dt 

  # fig, ax = plt.subplots(2,1)
  # ax[0].plot(fastout[0]['Time'],yaw_rate)
  plt.plot(fastout[0]['Time'],yaw[:-1]*57.2958)
  plt.show()

  print('here')



