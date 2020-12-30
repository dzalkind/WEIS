'''
----------- Example_04 --------------
Load a turbine model and tune the controller
-------------------------------------

In this example:
  - Read a .yaml file
  - Load a turbine model from OpenFAST
  - Tune a controller
  - Write a controller input file
  - Plot gain schedule
'''
# Python modules
import matplotlib.pyplot as plt 
import yaml 
# ROSCO toolbox modules 
from ROSCO_toolbox import controller as ROSCO_controller
from ROSCO_toolbox import turbine as ROSCO_turbine
from ROSCO_toolbox import sim as ROSCO_sim
from ROSCO_toolbox import utilities as ROSCO_utilities

# Load yaml file 
parameter_filename = '/Users/dzalkind/Tools/WEIS-3/examples/OpenFAST_models/CT15MW-barge/ServoData/CT-barge_90.yaml'
inps = yaml.safe_load(open(parameter_filename))
path_params         = inps['path_params']
turbine_params      = inps['turbine_params']
controller_params   = inps['controller_params']

# Instantiate turbine, controller, and file processing classes
turbine         = ROSCO_turbine.Turbine(turbine_params)
controller      = ROSCO_controller.Controller(controller_params)
file_processing = ROSCO_utilities.FileProcessing()

# Load turbine data from OpenFAST and rotor performance text file
turbine.load_from_fast(path_params['FAST_InputFile'],path_params['FAST_directory'],dev_branch=True,rot_source='txt',txt_filename=path_params['rotor_performance_filename'])

# Tune controller 
controller.tune_controller(turbine)

# Write parameter input file
param_file = '/Users/dzalkind/Tools/WEIS-3/examples/OpenFAST_models/CT15MW-barge/ServoData/DISCON-CT-barge_90.IN'   
file_processing.write_DISCON(turbine,controller,param_file=param_file, txt_filename=path_params['rotor_performance_filename'])

# Plot gain schedule
fig, ax = plt.subplots(1,2,constrained_layout=True)
ax[0].plot(controller.v[len(controller.vs_gain_schedule.Kp):], controller.pc_gain_schedule.Kp)
ax[0].set_xlabel('Wind Speed')
ax[0].set_ylabel('Proportional Gain')

ax[1].plot(controller.v[len(controller.vs_gain_schedule.Ki):], controller.pc_gain_schedule.Ki)
ax[1].set_xlabel('Wind Speed')
ax[1].set_ylabel('Integral Gain')

plt.suptitle('Pitch Controller Gains')

# Plot minimum pitch schedule
plt.figure(2)
plt.plot(controller.v, controller.pitch_op,label='Steady State Operation')
plt.plot(controller.v, controller.ps_min_bld_pitch, label='Minimum Pitch Schedule')
plt.legend()
plt.xlabel('Wind speed (m/s)')
plt.ylabel('Blade pitch (rad)')
plt.show()
