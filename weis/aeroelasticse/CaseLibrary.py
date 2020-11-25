import os, yaml
import numpy as np

from weis.aeroelasticse.CaseGen_General import CaseGen_General
from weis.aeroelasticse.CaseGen_IEC import CaseGen_IEC
from weis.aeroelasticse.HH_WindFile import HH_StepFile

# ROSCO 
from ROSCO_toolbox import controller as ROSCO_controller
from ROSCO_toolbox import turbine as ROSCO_turbine
from ROSCO_toolbox import utilities as ROSCO_utilities


# def power_curve_fit(fst_vt, runDir, namebase, TMax, turbine_class, turbulence_class, Vrated, U_init=[], Omega_init=[], pitch_init=[], Turbsim_exe='', ptfm_U_init=[], ptfm_pitch_init=[], ptfm_surge_init=[], ptfm_heave_init=[], metocean_U_init=[], metocean_Hs_init=[], metocean_Tp_init=[]):

#     # Default Runtime
#     T      = 240.
#     TStart = 120.
#     # T      = 120.
#     # TStart = 60.
    
#     # Overwrite for testing
#     if TMax < T:
#         T      = TMax
#         TStart = 0.

#     # Run conditions for points which will be used for a cubic polynomial fit
#     # U = [10.]
#     U = [4.,8.,9.,10.]
#     omega = np.interp(U, U_init, Omega_init)
#     pitch = np.interp(U, U_init, pitch_init)

#     # Check if floating
#     floating_dof = [fst_vt['ElastoDyn']['PtfmSgDOF'], fst_vt['ElastoDyn']['PtfmSwDOF'], fst_vt['ElastoDyn']['PtfmHvDOF'], fst_vt['ElastoDyn']['PtfmRDOF'], fst_vt['ElastoDyn']['PtfmPDOF'], fst_vt['ElastoDyn']['PtfmYDOF']]
#     if any(floating_dof):
#         floating = True
#         if ptfm_U_init == []:
#             ptfm_U_init     = [4., 5., 6., 7., 8., 9., 10., 10.5, 11., 12., 14., 19., 24.]
#             ptfm_surge_init = [3.8758245863838807, 5.57895688031965, 7.619719770801395, 9.974666446553552, 12.675469235464321, 16.173740623041965, 20.069526574594757, 22.141906121375552, 23.835466098954708, 22.976075549477354, 17.742743260748373, 14.464576583154068, 14.430969814391759]
#             ptfm_heave_init = [0.030777174904620515, 0.008329930604820483, -0.022973502300090893, -0.06506947653943342, -0.12101317451310406, -0.20589689839069836, -0.3169518280533253, -0.3831692055885472, -0.4409624802614755, -0.41411738171337675, -0.2375323506471747, -0.1156867221814119, -0.07029955933167854]
#             ptfm_pitch_init = [0.7519976895165884, 1.104483050851386, 1.5180416334025146, 1.9864587671004394, 2.5152769741130134, 3.1937704945765795, 3.951314212429935, 4.357929703098016, 4.693765745171944, 4.568760630312074, 3.495057478277534, 2.779958240049992, 2.69008798174216]
#         if metocean_U_init == []:
#             metocean_U_init  = [4.00, 6.00, 8.00, 10.00, 12.00, 14.00, 16.00, 18.00, 20.00, 22.00, 24.00]
#             metocean_Hs_init = [1.908567568, 1.960162595, 2.062722244, 2.224539415, 2.489931091, 2.802984019, 3.182301485, 3.652236101, 4.182596165, 4.695439504, 5.422289377]
#             metocean_Tp_init = [12.23645701, 12.14497777, 11.90254947, 11.5196666, 11.05403739, 10.65483551, 10.27562225, 10.13693777, 10.27842325, 10.11660396, 10.96177917]

#         ptfm_heave = np.interp(U, ptfm_U_init, ptfm_heave_init)
#         ptfm_surge = np.interp(U, ptfm_U_init, ptfm_surge_init)
#         ptfm_pitch = np.interp(U, ptfm_U_init, ptfm_pitch_init)
#         metocean_Hs = np.interp(U, metocean_U_init, metocean_Hs_init)
#         metocean_Tp = np.interp(U, metocean_U_init, metocean_Tp_init)
#     else:
#         floating = False

#     case_inputs = {}
#     # simulation settings
#     # case_inputs[("ElastoDyn","PtfmSgDOF")]     = {'vals':['False'], 'group':0}
#     # case_inputs[("ElastoDyn","PtfmHvDOF")]     = {'vals':['False'], 'group':0}
#     # case_inputs[("ElastoDyn","PtfmPDOF")]     = {'vals':['False'], 'group':0}
#     case_inputs[("ElastoDyn","PtfmSwDOF")]     = {'vals':['False'], 'group':0}
#     case_inputs[("ElastoDyn","PtfmRDOF")]     = {'vals':['False'], 'group':0}
#     case_inputs[("ElastoDyn","PtfmYDOF")]     = {'vals':['False'], 'group':0}

#     case_inputs[("Fst","TMax")] = {'vals':[T], 'group':0}
#     case_inputs[("Fst","TStart")] = {'vals':[TStart], 'group':0}
#     case_inputs[("ElastoDyn","YawDOF")]      = {'vals':['True'], 'group':0}
#     case_inputs[("ElastoDyn","FlapDOF1")]    = {'vals':['True'], 'group':0}
#     case_inputs[("ElastoDyn","FlapDOF2")]    = {'vals':['True'], 'group':0}
#     case_inputs[("ElastoDyn","EdgeDOF")]     = {'vals':['True'], 'group':0}
#     case_inputs[("ElastoDyn","DrTrDOF")]     = {'vals':['False'], 'group':0}
#     case_inputs[("ElastoDyn","GenDOF")]      = {'vals':['True'], 'group':0} 
#     case_inputs[("ElastoDyn","TwFADOF1")]    = {'vals':['False'], 'group':0}
#     case_inputs[("ElastoDyn","TwFADOF2")]    = {'vals':['False'], 'group':0}
#     case_inputs[("ElastoDyn","TwSSDOF1")]    = {'vals':['False'], 'group':0}
#     case_inputs[("ElastoDyn","TwSSDOF2")]    = {'vals':['False'], 'group':0}
#     case_inputs[("ServoDyn","PCMode")]       = {'vals':[5], 'group':0}
#     case_inputs[("ServoDyn","VSContrl")]     = {'vals':[5], 'group':0}
#     case_inputs[("ServoDyn","YCMode")]       = {'vals':[5], 'group':0}
#     case_inputs[("AeroDyn15","WakeMod")]     = {'vals':[1], 'group':0}
#     case_inputs[("AeroDyn15","AFAeroMod")]   = {'vals':[2], 'group':0}
#     case_inputs[("AeroDyn15","TwrPotent")]   = {'vals':[0], 'group':0}
#     case_inputs[("AeroDyn15","TwrShadow")]   = {'vals':['False'], 'group':0}
#     case_inputs[("AeroDyn15","TwrAero")]     = {'vals':['False'], 'group':0}
#     case_inputs[("AeroDyn15","SkewMod")]     = {'vals':[1], 'group':0}
#     case_inputs[("AeroDyn15","TipLoss")]     = {'vals':['True'], 'group':0}
#     case_inputs[("AeroDyn15","HubLoss")]     = {'vals':['True'], 'group':0}
#     case_inputs[("AeroDyn15","TanInd")]      = {'vals':['True'], 'group':0}
#     case_inputs[("AeroDyn15","AIDrag")]      = {'vals':['True'], 'group':0}
#     case_inputs[("AeroDyn15","TIDrag")]      = {'vals':['True'], 'group':0}
#     case_inputs[("AeroDyn15","IndToler")]    = {'vals':[1.e-5], 'group':0}
#     case_inputs[("AeroDyn15","MaxIter")]     = {'vals':[5000], 'group':0}
#     case_inputs[("AeroDyn15","UseBlCm")]     = {'vals':['True'], 'group':0}
#     # inital conditions
#     case_inputs[("InflowWind","WindType")] = {'vals':[1], 'group':0}
#     case_inputs[("InflowWind","HWindSpeed")] = {'vals':U, 'group':1}
#     case_inputs[("ElastoDyn","RotSpeed")] = {'vals':omega, 'group':1}
#     case_inputs[("ElastoDyn","BlPitch1")] = {'vals':pitch, 'group':1}
#     case_inputs[("ElastoDyn","BlPitch2")] = case_inputs[("ElastoDyn","BlPitch1")]
#     case_inputs[("ElastoDyn","BlPitch3")] = case_inputs[("ElastoDyn","BlPitch1")]
#     if floating == True:
#         case_inputs[("ElastoDyn","PtfmSurge")] = {'vals':ptfm_surge, 'group':1}
#         case_inputs[("ElastoDyn","PtfmHeave")] = {'vals':ptfm_heave, 'group':1}
#         case_inputs[("ElastoDyn","PtfmPitch")] = {'vals':ptfm_pitch, 'group':1}
#         case_inputs[("HydroDyn","WaveHs")] = {'vals':metocean_Hs, 'group':1}
#         case_inputs[("HydroDyn","WaveTp")] = {'vals':metocean_Tp, 'group':1}
#         case_inputs[("HydroDyn","RdtnDT")] = {'vals':[fst_vt["Fst"]["DT"]], 'group':0}
#         case_inputs[("HydroDyn","WaveMod")] = {'vals':[1], 'group':0}

#     from CaseGen_General import CaseGen_General
#     case_list, case_name_list = CaseGen_General(case_inputs, dir_matrix=runDir, namebase=namebase)

#     channels = ['Wind1VelX','GenPwr']

#     return case_list, case_name_list, channels

def power_curve(fst_vt, runDir, namebase, TMax, turbine_class, turbulence_class, Vrated, U_init=[], Omega_init=[], pitch_init=[], Turbsim_exe='', ptfm_U_init=[], ptfm_pitch_init=[], ptfm_surge_init=[], ptfm_heave_init=[], metocean_U_init=[], metocean_Hs_init=[], metocean_Tp_init=[], V_R25=0.):

    # Default Runtime
    T      = 360.
    TStart = 120.
    # T      = 120.
    # TStart = 60.
    
    # Overwrite for testing
    if TMax < T:
        T      = TMax
        TStart = 0.

    # Run conditions
    U_all = list(sorted([4., 6., 8., 9., 10., 10.5, 11., 11.5, 11.75, 12., 12.5, 13., 14., 19., 25., Vrated]))
    if V_R25 != 0.:
        U_all.append(V_R25)
        U_all = list(sorted(U_all))
    U = [Vi for Vi in U_all if Vi <= Vrated]
    # print(U)

    # dt = [0.01, 0.01, 0.01, 0.01, 0.01, 0.01, 0.01, 0.001, 0.001, 0.001, 0.001, 0.001, 0.001]
    # dt = [0.01]*len(U)

    # U = [4.,8.,9.,10.]
    omega = np.interp(U, U_init, Omega_init)
    pitch = np.interp(U, U_init, pitch_init)
    for i, (omegai, pitchi) in enumerate(zip(omega, pitch)):
        if pitchi > 0. and omegai < Omega_init[-1]:
            pitch[i] = 0.

    # Check if floating
    floating_dof = [fst_vt['ElastoDyn']['PtfmSgDOF'], fst_vt['ElastoDyn']['PtfmSwDOF'], fst_vt['ElastoDyn']['PtfmHvDOF'], fst_vt['ElastoDyn']['PtfmRDOF'], fst_vt['ElastoDyn']['PtfmPDOF'], fst_vt['ElastoDyn']['PtfmYDOF']]
    if any(floating_dof):
        floating = True
        if ptfm_U_init == []:
            ptfm_U_init     = [3., 5., 6., 7., 8., 9., 10., 10.5, 11., 12., 14., 19., 25.]
            ptfm_surge_init = [3.8758245863838807, 5.57895688031965, 7.619719770801395, 9.974666446553552, 12.675469235464321, 16.173740623041965, 20.069526574594757, 22.141906121375552, 23.835466098954708, 22.976075549477354, 17.742743260748373, 14.464576583154068, 14.430969814391759]
            ptfm_heave_init = [0.030777174904620515, 0.008329930604820483, -0.022973502300090893, -0.06506947653943342, -0.12101317451310406, -0.20589689839069836, -0.3169518280533253, -0.3831692055885472, -0.4409624802614755, -0.41411738171337675, -0.2375323506471747, -0.1156867221814119, -0.07029955933167854]
            ptfm_pitch_init = [0.7519976895165884, 1.104483050851386, 1.5180416334025146, 1.9864587671004394, 2.5152769741130134, 3.1937704945765795, 3.951314212429935, 4.357929703098016, 4.693765745171944, 4.568760630312074, 3.495057478277534, 2.779958240049992, 2.69008798174216]
        if metocean_U_init == []:
            metocean_U_init  = [3.00, 6.00, 8.00, 10.00, 12.00, 14.00, 16.00, 18.00, 20.00, 22.00, 25.00]
            metocean_Hs_init = [1.908567568, 1.960162595, 2.062722244, 2.224539415, 2.489931091, 2.802984019, 3.182301485, 3.652236101, 4.182596165, 4.695439504, 5.422289377]
            metocean_Tp_init = [12.23645701, 12.14497777, 11.90254947, 11.5196666, 11.05403739, 10.65483551, 10.27562225, 10.13693777, 10.27842325, 10.11660396, 10.96177917]

        ptfm_heave = np.interp(U, ptfm_U_init, ptfm_heave_init)
        ptfm_surge = np.interp(U, ptfm_U_init, ptfm_surge_init)
        ptfm_pitch = np.interp(U, ptfm_U_init, ptfm_pitch_init)
        metocean_Hs = np.interp(U, metocean_U_init, metocean_Hs_init)
        metocean_Tp = np.interp(U, metocean_U_init, metocean_Tp_init)
    else:
        floating = False

    case_inputs = {}
    # simulation settings
    # case_inputs[("ElastoDyn","PtfmSgDOF")]     = {'vals':['False'], 'group':0}
    # case_inputs[("ElastoDyn","PtfmHvDOF")]     = {'vals':['False'], 'group':0}
    # case_inputs[("ElastoDyn","PtfmPDOF")]     = {'vals':['False'], 'group':0}
    # case_inputs[("ElastoDyn","PtfmSwDOF")]     = {'vals':['False'], 'group':0}
    # case_inputs[("ElastoDyn","PtfmRDOF")]     = {'vals':['False'], 'group':0}
    # case_inputs[("ElastoDyn","PtfmYDOF")]     = {'vals':['False'], 'group':0}

    case_inputs[("Fst","TMax")] = {'vals':[T], 'group':0}
    case_inputs[("Fst","TStart")] = {'vals':[TStart], 'group':0}
    case_inputs[("Fst","OutFileFmt")] = {'vals':[2], 'group':0}
    
    # case_inputs[("Fst","DT")] = {'vals':dt, 'group':1}
    # case_inputs[("ElastoDyn","YawDOF")]      = {'vals':['True'], 'group':0}
    # case_inputs[("ElastoDyn","FlapDOF1")]    = {'vals':['False'], 'group':0}
    # case_inputs[("ElastoDyn","FlapDOF2")]    = {'vals':['False'], 'group':0}
    # case_inputs[("ElastoDyn","EdgeDOF")]     = {'vals':['False'], 'group':0}
    # case_inputs[("ElastoDyn","DrTrDOF")]     = {'vals':['False'], 'group':0}
    # case_inputs[("ElastoDyn","GenDOF")]      = {'vals':['True'], 'group':0} 
    # case_inputs[("ElastoDyn","TwFADOF1")]    = {'vals':['False'], 'group':0}
    # case_inputs[("ElastoDyn","TwFADOF2")]    = {'vals':['False'], 'group':0}
    # case_inputs[("ElastoDyn","TwSSDOF1")]    = {'vals':['False'], 'group':0}
    # case_inputs[("ElastoDyn","TwSSDOF2")]    = {'vals':['False'], 'group':0}
    # case_inputs[("ServoDyn","PCMode")]       = {'vals':[5], 'group':0}
    # case_inputs[("ServoDyn","VSContrl")]     = {'vals':[5], 'group':0}
    # case_inputs[("ServoDyn","YCMode")]       = {'vals':[5], 'group':0}
    case_inputs[("AeroDyn15","WakeMod")]     = {'vals':[1], 'group':0}
    case_inputs[("AeroDyn15","AFAeroMod")]   = {'vals':[2], 'group':0}
    case_inputs[("AeroDyn15","TwrPotent")]   = {'vals':[0], 'group':0}
    case_inputs[("AeroDyn15","TwrShadow")]   = {'vals':['False'], 'group':0}
    case_inputs[("AeroDyn15","TwrAero")]     = {'vals':['False'], 'group':0}
    case_inputs[("AeroDyn15","SkewMod")]     = {'vals':[1], 'group':0}
    case_inputs[("AeroDyn15","TipLoss")]     = {'vals':['True'], 'group':0}
    case_inputs[("AeroDyn15","HubLoss")]     = {'vals':['True'], 'group':0}
    case_inputs[("AeroDyn15","TanInd")]      = {'vals':['True'], 'group':0}
    case_inputs[("AeroDyn15","AIDrag")]      = {'vals':['True'], 'group':0}
    case_inputs[("AeroDyn15","TIDrag")]      = {'vals':['True'], 'group':0}
    case_inputs[("AeroDyn15","IndToler")]    = {'vals':[1.e-5], 'group':0}
    case_inputs[("AeroDyn15","MaxIter")]     = {'vals':[5000], 'group':0}
    case_inputs[("AeroDyn15","UseBlCm")]     = {'vals':['True'], 'group':0}
    # inital conditions
    case_inputs[("InflowWind","WindType")] = {'vals':[1], 'group':0}
    case_inputs[("InflowWind","HWindSpeed")] = {'vals':U, 'group':1}
    case_inputs[("ElastoDyn","RotSpeed")] = {'vals':omega, 'group':1}
    case_inputs[("ElastoDyn","BlPitch1")] = {'vals':pitch, 'group':1}
    case_inputs[("ElastoDyn","BlPitch2")] = case_inputs[("ElastoDyn","BlPitch1")]
    case_inputs[("ElastoDyn","BlPitch3")] = case_inputs[("ElastoDyn","BlPitch1")]
    if floating == True:
        case_inputs[("ElastoDyn","PtfmSurge")] = {'vals':ptfm_surge, 'group':1}
        case_inputs[("ElastoDyn","PtfmHeave")] = {'vals':ptfm_heave, 'group':1}
        case_inputs[("ElastoDyn","PtfmPitch")] = {'vals':ptfm_pitch, 'group':1}
        case_inputs[("HydroDyn","WaveHs")] = {'vals':metocean_Hs, 'group':1}
        case_inputs[("HydroDyn","WaveTp")] = {'vals':metocean_Tp, 'group':1}
        case_inputs[("HydroDyn","RdtnDT")] = {'vals':dt, 'group':1}
        case_inputs[("HydroDyn","WaveMod")] = {'vals':[1], 'group':0}

    from weis.aeroelasticse.CaseGen_General import CaseGen_General
    case_list, case_name_list = CaseGen_General(case_inputs, dir_matrix=runDir, namebase=namebase)

    channels = ['Wind1VelX','GenPwr',"RtAeroCp", "RotTorq", "RotThrust", "RotSpeed", "BldPitch1"]

    return case_list, case_name_list, channels

def power_curve_control(discon_file,runDir, namebase,rosco_dll=''):
    # Set up cases for FIW-JIP project
    # 2.x in controller tuning register

    # Default Runtime
    T_max   = 800.


    # Run conditions
    U = np.arange(4,24.5,.5).tolist()

    case_inputs = {}
    # simulation settings
    case_inputs[("Fst","TMax")] = {'vals':[T_max], 'group':0}
    case_inputs[("Fst","OutFileFmt")] = {'vals':[2], 'group':0}

    # DOFs
    # case_inputs[("ElastoDyn","YawDOF")]      = {'vals':['True'], 'group':0}
    # case_inputs[("ElastoDyn","FlapDOF1")]    = {'vals':['False'], 'group':0}
    # case_inputs[("ElastoDyn","FlapDOF2")]    = {'vals':['False'], 'group':0}
    # case_inputs[("ElastoDyn","EdgeDOF")]     = {'vals':['False'], 'group':0}
    # case_inputs[("ElastoDyn","DrTrDOF")]     = {'vals':['False'], 'group':0}
    # case_inputs[("ElastoDyn","GenDOF")]      = {'vals':['True'], 'group':0} 
    # case_inputs[("ElastoDyn","TwFADOF1")]    = {'vals':['False'], 'group':0}
    # case_inputs[("ElastoDyn","TwFADOF2")]    = {'vals':['False'], 'group':0}
    # case_inputs[("ElastoDyn","TwSSDOF1")]    = {'vals':['False'], 'group':0}
    # case_inputs[("ElastoDyn","TwSSDOF2")]    = {'vals':['False'], 'group':0}
    # case_inputs[("ElastoDyn","PtfmSgDOF")]     = {'vals':['False'], 'group':0}
    # case_inputs[("ElastoDyn","PtfmHvDOF")]     = {'vals':['False'], 'group':0}
    # case_inputs[("ElastoDyn","PtfmPDOF")]     = {'vals':['False'], 'group':0}
    # case_inputs[("ElastoDyn","PtfmSwDOF")]     = {'vals':['False'], 'group':0}
    # case_inputs[("ElastoDyn","PtfmRDOF")]     = {'vals':['False'], 'group':0}
    # case_inputs[("ElastoDyn","PtfmYDOF")]     = {'vals':['False'], 'group':0}
    
    # wind inflow
    case_inputs[("InflowWind","WindType")] = {'vals':[1], 'group':0}
    case_inputs[("InflowWind","HWindSpeed")] = {'vals':U, 'group':1}

    # Stop Generator from Turning Off
    case_inputs[('ServoDyn', 'GenTiStr')] = {'vals': ['True'], 'group': 0}
    case_inputs[('ServoDyn', 'GenTiStp')] = {'vals': ['True'], 'group': 0}
    case_inputs[('ServoDyn', 'SpdGenOn')] = {'vals': [0.], 'group': 0}
    case_inputs[('ServoDyn', 'TimGenOn')] = {'vals': [0.], 'group': 0}
    case_inputs[('ServoDyn', 'GenModel')] = {'vals': [1], 'group': 0}
    

    # AeroDyn
    case_inputs[("AeroDyn15", "WakeMod")] = {'vals': [1], 'group': 0}
    case_inputs[("AeroDyn15", "AFAeroMod")] = {'vals': [2], 'group': 0}
    case_inputs[("AeroDyn15", "TwrPotent")] = {'vals': [0], 'group': 0}
    case_inputs[("AeroDyn15", "TwrShadow")] = {'vals': ['False'], 'group': 0}
    case_inputs[("AeroDyn15", "TwrAero")] = {'vals': ['False'], 'group': 0}
    case_inputs[("AeroDyn15", "SkewMod")] = {'vals': [1], 'group': 0}
    case_inputs[("AeroDyn15", "TipLoss")] = {'vals': ['True'], 'group': 0}
    case_inputs[("AeroDyn15", "HubLoss")] = {'vals': ['True'], 'group': 0}
    case_inputs[("AeroDyn15", "TanInd")] = {'vals': ['True'], 'group': 0}
    case_inputs[("AeroDyn15", "AIDrag")] = {'vals': ['True'], 'group': 0}
    case_inputs[("AeroDyn15", "TIDrag")] = {'vals': ['True'], 'group': 0}
    case_inputs[("AeroDyn15", "IndToler")] = {'vals': [1.e-5], 'group': 0}
    case_inputs[("AeroDyn15", "MaxIter")] = {'vals': [5000], 'group': 0}
    case_inputs[("AeroDyn15", "UseBlCm")] = {'vals': ['True'], 'group': 0}

    # Controller
    if rosco_dll:
        # Need to update this to ROSCO with power control!!!
        case_inputs[("ServoDyn","DLL_FileName")] = {'vals':[rosco_dll], 'group':0}

    # Control (DISCON) Inputs
    file_processing = ROSCO_utilities.FileProcessing()
    discon_vt = file_processing.read_DISCON(discon_file)
    for discon_input in discon_vt:
        case_inputs[('DISCON_in',discon_input)] = {'vals': [discon_vt[discon_input]], 'group': 0}

    from weis.aeroelasticse.CaseGen_General import CaseGen_General
    case_list, case_name_list = CaseGen_General(case_inputs, dir_matrix=runDir, namebase=namebase)

    channels = set_channels()

    return case_list, case_name_list, channels

def simp_step(discon_file,runDir, namebase,rosco_dll='',tune=''):
    # Set up cases for FIW-JIP project
    # 3.x in controller tuning register

    # Default Runtime
    T_max   = 800.

    # Step Wind Setup

    # Make Default step wind object
    hh_step = HH_StepFile()
    hh_step.t_max = T_max
    hh_step.t_step = 400
    hh_step.wind_directory = runDir

    # Run conditions
    U_start     = [10,11,12,16] #, 16]
    U_end       = [11,12,13,17] #, 17]
    step_wind_files = []

    for u_s,u_e in zip(U_start,U_end):
        # Make Step
        hh_step.u_start = u_s
        hh_step.u_end   = u_e
        hh_step.update()
        hh_step.write()

        step_wind_files.append(hh_step.filename)

    case_inputs = {}
    # simulation settings
    case_inputs[("Fst","TMax")] = {'vals':[T_max], 'group':0}
    case_inputs[("Fst","OutFileFmt")]        = {'vals':[2], 'group':0}

    # DOFs
    # case_inputs[("ElastoDyn","YawDOF")]      = {'vals':['True'], 'group':0}
    # case_inputs[("ElastoDyn","FlapDOF1")]    = {'vals':['False'], 'group':0}
    # case_inputs[("ElastoDyn","FlapDOF2")]    = {'vals':['False'], 'group':0}
    # case_inputs[("ElastoDyn","EdgeDOF")]     = {'vals':['False'], 'group':0}
    # case_inputs[("ElastoDyn","DrTrDOF")]     = {'vals':['False'], 'group':0}
    # case_inputs[("ElastoDyn","GenDOF")]      = {'vals':['True'], 'group':0} 
    # case_inputs[("ElastoDyn","TwFADOF1")]    = {'vals':['False'], 'group':0}
    # case_inputs[("ElastoDyn","TwFADOF2")]    = {'vals':['False'], 'group':0}
    # case_inputs[("ElastoDyn","TwSSDOF1")]    = {'vals':['False'], 'group':0}
    # case_inputs[("ElastoDyn","TwSSDOF2")]    = {'vals':['False'], 'group':0}
    # case_inputs[("ElastoDyn","PtfmSgDOF")]     = {'vals':['False'], 'group':0}
    # case_inputs[("ElastoDyn","PtfmHvDOF")]     = {'vals':['False'], 'group':0}
    # case_inputs[("ElastoDyn","PtfmPDOF")]     = {'vals':['False'], 'group':0}
    # case_inputs[("ElastoDyn","PtfmSwDOF")]     = {'vals':['False'], 'group':0}
    # case_inputs[("ElastoDyn","PtfmRDOF")]     = {'vals':['False'], 'group':0}
    # case_inputs[("ElastoDyn","PtfmYDOF")]     = {'vals':['False'], 'group':0}
    
    # wind inflow
    case_inputs[("InflowWind","WindType")] = {'vals':[2], 'group':0}
    case_inputs[("InflowWind","Filename")] = {'vals':step_wind_files, 'group':1}


    # Stop Generator from Turning Off
    case_inputs[('ServoDyn', 'GenTiStr')] = {'vals': ['True'], 'group': 0}
    case_inputs[('ServoDyn', 'GenTiStp')] = {'vals': ['True'], 'group': 0}
    case_inputs[('ServoDyn', 'SpdGenOn')] = {'vals': [0.], 'group': 0}
    case_inputs[('ServoDyn', 'TimGenOn')] = {'vals': [0.], 'group': 0}
    case_inputs[('ServoDyn', 'GenModel')] = {'vals': [1], 'group': 0}
    

    # AeroDyn
    case_inputs[("AeroDyn15", "WakeMod")] = {'vals': [1], 'group': 0}
    case_inputs[("AeroDyn15", "AFAeroMod")] = {'vals': [2], 'group': 0}
    case_inputs[("AeroDyn15", "TwrPotent")] = {'vals': [0], 'group': 0}
    case_inputs[("AeroDyn15", "TwrShadow")] = {'vals': ['False'], 'group': 0}
    case_inputs[("AeroDyn15", "TwrAero")] = {'vals': ['False'], 'group': 0}
    case_inputs[("AeroDyn15", "SkewMod")] = {'vals': [1], 'group': 0}
    case_inputs[("AeroDyn15", "TipLoss")] = {'vals': ['True'], 'group': 0}
    case_inputs[("AeroDyn15", "HubLoss")] = {'vals': ['True'], 'group': 0}
    case_inputs[("AeroDyn15", "TanInd")] = {'vals': ['True'], 'group': 0}
    case_inputs[("AeroDyn15", "AIDrag")] = {'vals': ['True'], 'group': 0}
    case_inputs[("AeroDyn15", "TIDrag")] = {'vals': ['True'], 'group': 0}
    case_inputs[("AeroDyn15", "IndToler")] = {'vals': [1.e-5], 'group': 0}
    case_inputs[("AeroDyn15", "MaxIter")] = {'vals': [5000], 'group': 0}
    case_inputs[("AeroDyn15", "UseBlCm")] = {'vals': ['True'], 'group': 0}

    # Controller
    if rosco_dll:
        # Need to update this to ROSCO with power control!!!
        case_inputs[("ServoDyn","DLL_FileName")] = {'vals':[rosco_dll], 'group':0}

    # Control (DISCON) Inputs
    file_processing = ROSCO_utilities.FileProcessing()
    discon_vt = file_processing.read_DISCON(discon_file)
    for discon_input in discon_vt:
        case_inputs[('DISCON_in',discon_input)] = {'vals': [discon_vt[discon_input]], 'group': 0}


    # Tune Floating Feedback Gain
    if tune == 'fl_gain':
        case_inputs[('DISCON_in','Fl_Kp')] = {'vals': np.linspace(0,-25,10,endpoint=True).tolist(), 'group': 2}

    elif tune == 'fl_phase':
        case_inputs[('DISCON_in','Fl_Kp')] = {'vals': 8*[-25], 'group': 2}
        case_inputs[('DISCON_in','F_FlCornerFreq')] = {'vals': 8*[0.300], 'group': 2}
        case_inputs[('DISCON_in','F_FlHighPassFreq')] = {'vals':[0.001,0.005,0.010,0.020,0.030,0.042,0.060,0.100], 'group': 2}
        case_inputs[('meta','Fl_Phase')] = {'vals':8*[-50],'group':2}

    elif tune == 'pc_mode':
        # define omega, zeta
        omega = np.linspace(.05,.25,8,endpoint=True).tolist()
        zeta  = np.linspace(1,3,3,endpoint=True).tolist()
        
        control_case_inputs = sweep_pc_mode(omega,zeta)
        case_inputs.update(control_case_inputs)


    elif tune == 'ps_perc':
        # Set sweep limits here
        ps_perc = np.linspace(.75,1,num=8,endpoint=True).tolist()
        
        # load default params          
        weis_dir            = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
        control_param_yaml  = os.path.join(weis_dir,'examples/OpenFAST_models/CT15MW-spar/ServoData/IEA15MW-CT-spar.yaml')
        inps                = yaml.safe_load(open(control_param_yaml))
        path_params         = inps['path_params']
        turbine_params      = inps['turbine_params']
        controller_params   = inps['controller_params']

        # make default controller, turbine objects for ROSCO_toolbox
        turbine             = ROSCO_turbine.Turbine(turbine_params)
        turbine.load_from_fast( path_params['FAST_InputFile'],path_params['FAST_directory'], dev_branch=True)

        controller          = ROSCO_controller.Controller(controller_params)

        # tune default controller
        controller.tune_controller(turbine)

        # Loop through and make min pitch tables
        ps_ws = []
        ps_mp = []
        m_ps  = []  # flattened (omega,zeta) pairs
        for p in ps_perc:
            controller.ps_percent = p
            controller.tune_controller(turbine)
            m_ps.append(controller.ps_min_bld_pitch)

        # add control gains to case_list
        case_inputs[('meta','ps_perc')]          = {'vals': ps_perc, 'group': 2}
        case_inputs[('DISCON_in', 'PS_BldPitchMin')] = {'vals': m_ps, 'group': 2}

        # file.write('{}              ! PS_WindSpeeds     - Wind speeds corresponding to minimum blade pitch angles [m/s]\n'.format(''.join('{:<4.2f} '.format(controller.v[i]) for i in range(len(controller.v)))))
        # file.write('{}              ! PS_BldPitchMin    - Minimum blade pitch angles [rad]\n'.format(''.join('{:<10.8f} '.format(controller.ps_min_bld_pitch[i]) for i in range(len(controller.ps_min_bld_pitch)))))


    from weis.aeroelasticse.CaseGen_General import CaseGen_General
    case_list, case_name_list = CaseGen_General(case_inputs, dir_matrix=runDir, namebase=namebase)

    channels = set_channels()

    return case_list, case_name_list, channels


def steps(discon_file,runDir, namebase,rosco_dll=''):
    # Set up cases for FIW-JIP project
    # 3.x in controller tuning register

    # Default Runtime
    T_max   = 800.

    # Step Wind Setup

    # Make Default step wind object
    hh_step = HH_StepFile()
    hh_step.t_max = T_max
    hh_step.t_step = 400
    hh_step.wind_directory = runDir

    # Run conditions
    U = np.arange(4,24,1).tolist()
    step_wind_files = []

    for u in U:
        # Step up
        hh_step.u_start = u
        hh_step.u_end   = u+1
        hh_step.update()
        hh_step.write()

        step_wind_files.append(hh_step.filename)

        # Step down
        hh_step.u_start = u+1
        hh_step.u_end   = u
        hh_step.update()
        hh_step.write()

        step_wind_files.append(hh_step.filename)

    case_inputs = {}
    # simulation settings
    case_inputs[("Fst","TMax")] = {'vals':[T_max], 'group':0}
    case_inputs[("Fst","OutFileFmt")]        = {'vals':[2], 'group':0}

    # DOFs
    # case_inputs[("ElastoDyn","YawDOF")]      = {'vals':['True'], 'group':0}
    # case_inputs[("ElastoDyn","FlapDOF1")]    = {'vals':['False'], 'group':0}
    # case_inputs[("ElastoDyn","FlapDOF2")]    = {'vals':['False'], 'group':0}
    # case_inputs[("ElastoDyn","EdgeDOF")]     = {'vals':['False'], 'group':0}
    # case_inputs[("ElastoDyn","DrTrDOF")]     = {'vals':['False'], 'group':0}
    # case_inputs[("ElastoDyn","GenDOF")]      = {'vals':['True'], 'group':0} 
    # case_inputs[("ElastoDyn","TwFADOF1")]    = {'vals':['False'], 'group':0}
    # case_inputs[("ElastoDyn","TwFADOF2")]    = {'vals':['False'], 'group':0}
    # case_inputs[("ElastoDyn","TwSSDOF1")]    = {'vals':['False'], 'group':0}
    # case_inputs[("ElastoDyn","TwSSDOF2")]    = {'vals':['False'], 'group':0}
    # case_inputs[("ElastoDyn","PtfmSgDOF")]     = {'vals':['False'], 'group':0}
    # case_inputs[("ElastoDyn","PtfmHvDOF")]     = {'vals':['False'], 'group':0}
    # case_inputs[("ElastoDyn","PtfmPDOF")]     = {'vals':['False'], 'group':0}
    # case_inputs[("ElastoDyn","PtfmSwDOF")]     = {'vals':['False'], 'group':0}
    # case_inputs[("ElastoDyn","PtfmRDOF")]     = {'vals':['False'], 'group':0}
    # case_inputs[("ElastoDyn","PtfmYDOF")]     = {'vals':['False'], 'group':0}
    
    # wind inflow
    case_inputs[("InflowWind","WindType")] = {'vals':[2], 'group':0}
    case_inputs[("InflowWind","Filename")] = {'vals':step_wind_files, 'group':1}


    # Stop Generator from Turning Off
    case_inputs[('ServoDyn', 'GenTiStr')] = {'vals': ['True'], 'group': 0}
    case_inputs[('ServoDyn', 'GenTiStp')] = {'vals': ['True'], 'group': 0}
    case_inputs[('ServoDyn', 'SpdGenOn')] = {'vals': [0.], 'group': 0}
    case_inputs[('ServoDyn', 'TimGenOn')] = {'vals': [0.], 'group': 0}
    case_inputs[('ServoDyn', 'GenModel')] = {'vals': [1], 'group': 0}
    

    # AeroDyn
    case_inputs[("AeroDyn15", "WakeMod")] = {'vals': [1], 'group': 0}
    case_inputs[("AeroDyn15", "AFAeroMod")] = {'vals': [2], 'group': 0}
    case_inputs[("AeroDyn15", "TwrPotent")] = {'vals': [0], 'group': 0}
    case_inputs[("AeroDyn15", "TwrShadow")] = {'vals': ['False'], 'group': 0}
    case_inputs[("AeroDyn15", "TwrAero")] = {'vals': ['False'], 'group': 0}
    case_inputs[("AeroDyn15", "SkewMod")] = {'vals': [1], 'group': 0}
    case_inputs[("AeroDyn15", "TipLoss")] = {'vals': ['True'], 'group': 0}
    case_inputs[("AeroDyn15", "HubLoss")] = {'vals': ['True'], 'group': 0}
    case_inputs[("AeroDyn15", "TanInd")] = {'vals': ['True'], 'group': 0}
    case_inputs[("AeroDyn15", "AIDrag")] = {'vals': ['True'], 'group': 0}
    case_inputs[("AeroDyn15", "TIDrag")] = {'vals': ['True'], 'group': 0}
    case_inputs[("AeroDyn15", "IndToler")] = {'vals': [1.e-5], 'group': 0}
    case_inputs[("AeroDyn15", "MaxIter")] = {'vals': [5000], 'group': 0}
    case_inputs[("AeroDyn15", "UseBlCm")] = {'vals': ['True'], 'group': 0}

    # Controller
    if rosco_dll:
        # Need to update this to ROSCO with power control!!!
        case_inputs[("ServoDyn","DLL_FileName")] = {'vals':[rosco_dll], 'group':0}

    # Control (DISCON) Inputs
    file_processing = ROSCO_utilities.FileProcessing()
    discon_vt = file_processing.read_DISCON(discon_file)
    for discon_input in discon_vt:
        case_inputs[('DISCON_in',discon_input)] = {'vals': [discon_vt[discon_input]], 'group': 0}

    from weis.aeroelasticse.CaseGen_General import CaseGen_General
    case_list, case_name_list = CaseGen_General(case_inputs, dir_matrix=runDir, namebase=namebase)

    channels = set_channels()

    return case_list, case_name_list, channels


def sweep_pc_mode(cont_yaml,omega=np.linspace(.05,.35,8,endpoint=True).tolist(),zeta=[1.5],group=2):
    
    
    inps                = yaml.safe_load(open(cont_yaml))
    path_params         = inps['path_params']
    turbine_params      = inps['turbine_params']
    controller_params   = inps['controller_params']

    # make default controller, turbine objects for ROSCO_toolbox
    turbine             = ROSCO_turbine.Turbine(turbine_params)
    turbine.load_from_fast( path_params['FAST_InputFile'],path_params['FAST_directory'], dev_branch=True)

    controller          = ROSCO_controller.Controller(controller_params)

    # tune default controller
    controller.tune_controller(turbine)

    # check if inputs are lists
    if not isinstance(omega,list):
        omega = [omega]
    if not isinstance(zeta,list):
        zeta = [zeta]

    # Loop through and make PI gains
    pc_kp = []
    pc_ki = []
    m_omega = []  # flattened (omega,zeta) pairs
    m_zeta = []  # flattened (omega,zeta) pairs
    for o in omega:
        for z in zeta:
            controller.omega_pc = o
            controller.zeta_pc  = z
            controller.tune_controller(turbine)
            pc_kp.append(controller.pc_gain_schedule.Kp.tolist())
            pc_ki.append(controller.pc_gain_schedule.Ki.tolist())
            m_omega.append(o)
            m_zeta.append(z)

    # add control gains to case_list
    case_inputs = {}
    case_inputs[('meta','omega')]          = {'vals': m_omega, 'group': group}
    case_inputs[('meta','zeta')]          = {'vals': m_zeta, 'group': group}
    case_inputs[('DISCON_in', 'PC_GS_KP')] = {'vals': pc_kp, 'group': group}
    case_inputs[('DISCON_in', 'PC_GS_KI')] = {'vals': pc_ki, 'group': group}

    return case_inputs


def RotorSE_rated(fst_vt, runDir, namebase, TMax, turbine_class, turbulence_class, Vrated, U_init=[], Omega_init=[], pitch_init=[], Turbsim_exe='', ptfm_U_init=[], ptfm_pitch_init=[], ptfm_surge_init=[], ptfm_heave_init=[], metocean_U_init=[], metocean_Hs_init=[], metocean_Tp_init=[]):

    # Default Runtime
    T      = 240.
    TStart = 120.

    # dt = 0.001
    dt = 0.01
    
    # Overwrite for testing
    if TMax < T:
        T      = TMax
        TStart = 0.

    omega = np.interp(Vrated, U_init, Omega_init)
    pitch = np.interp(Vrated, U_init, pitch_init)

    # Check if floating
    floating_dof = [fst_vt['ElastoDyn']['PtfmSgDOF'], fst_vt['ElastoDyn']['PtfmSwDOF'], fst_vt['ElastoDyn']['PtfmHvDOF'], fst_vt['ElastoDyn']['PtfmRDOF'], fst_vt['ElastoDyn']['PtfmPDOF'], fst_vt['ElastoDyn']['PtfmYDOF']]
    if any(floating_dof):
        floating = True
        if ptfm_U_init == []:
            ptfm_U_init     = [4., 5., 6., 7., 8., 9., 10., 10.5, 11., 12., 14., 19., 24.]
            ptfm_surge_init = [3.8758245863838807, 5.57895688031965, 7.619719770801395, 9.974666446553552, 12.675469235464321, 16.173740623041965, 20.069526574594757, 22.141906121375552, 23.835466098954708, 22.976075549477354, 17.742743260748373, 14.464576583154068, 14.430969814391759]
            ptfm_heave_init = [0.030777174904620515, 0.008329930604820483, -0.022973502300090893, -0.06506947653943342, -0.12101317451310406, -0.20589689839069836, -0.3169518280533253, -0.3831692055885472, -0.4409624802614755, -0.41411738171337675, -0.2375323506471747, -0.1156867221814119, -0.07029955933167854]
            ptfm_pitch_init = [0.7519976895165884, 1.104483050851386, 1.5180416334025146, 1.9864587671004394, 2.5152769741130134, 3.1937704945765795, 3.951314212429935, 4.357929703098016, 4.693765745171944, 4.568760630312074, 3.495057478277534, 2.779958240049992, 2.69008798174216]
        if metocean_U_init == []:
            metocean_U_init  = [4.00, 6.00, 8.00, 10.00, 12.00, 14.00, 16.00, 18.00, 20.00, 22.00, 24.00]
            metocean_Hs_init = [1.908567568, 1.960162595, 2.062722244, 2.224539415, 2.489931091, 2.802984019, 3.182301485, 3.652236101, 4.182596165, 4.695439504, 5.422289377]
            metocean_Tp_init = [12.23645701, 12.14497777, 11.90254947, 11.5196666, 11.05403739, 10.65483551, 10.27562225, 10.13693777, 10.27842325, 10.11660396, 10.96177917]

        ptfm_heave = [np.interp(Vrated, ptfm_U_init, ptfm_heave_init)]
        ptfm_surge = [np.interp(Vrated, ptfm_U_init, ptfm_surge_init)]
        ptfm_pitch = [np.interp(Vrated, ptfm_U_init, ptfm_pitch_init)]
        metocean_Hs = [np.interp(Vrated, metocean_U_init, metocean_Hs_init)]
        metocean_Tp = [np.interp(Vrated, metocean_U_init, metocean_Tp_init)]
    else:
        floating = False

    case_inputs = {}
    case_inputs[("Fst","TMax")]              = {'vals':[T], 'group':0}
    case_inputs[("Fst","TStart")]            = {'vals':[TStart], 'group':0}
    case_inputs[("Fst","DT")]                = {'vals':[dt], 'group':0}
    case_inputs[("Fst","OutFileFmt")]        = {'vals':[2], 'group':0}
    
    case_inputs[("InflowWind","WindType")]   = {'vals':[1], 'group':0}
    case_inputs[("InflowWind","HWindSpeed")] = {'vals':[Vrated], 'group':0}

    case_inputs[("ElastoDyn","RotSpeed")]    = {'vals':[omega], 'group':0}
    case_inputs[("ElastoDyn","BlPitch1")]    = {'vals':[pitch], 'group':0}
    case_inputs[("ElastoDyn","BlPitch2")]    = {'vals':[pitch], 'group':0}
    case_inputs[("ElastoDyn","BlPitch3")]    = {'vals':[pitch], 'group':0}
    case_inputs[("ElastoDyn","YawDOF")]      = {'vals':['False'], 'group':0}
    case_inputs[("ElastoDyn","FlapDOF1")]    = {'vals':['False'], 'group':0}
    case_inputs[("ElastoDyn","FlapDOF2")]    = {'vals':['False'], 'group':0}
    case_inputs[("ElastoDyn","EdgeDOF")]     = {'vals':['False'], 'group':0}
    case_inputs[("ElastoDyn","DrTrDOF")]     = {'vals':['False'], 'group':0}
    case_inputs[("ElastoDyn","GenDOF")]      = {'vals':['True'], 'group':0} 
    case_inputs[("ElastoDyn","TwFADOF1")]    = {'vals':['False'], 'group':0}
    case_inputs[("ElastoDyn","TwFADOF2")]    = {'vals':['False'], 'group':0}
    case_inputs[("ElastoDyn","TwSSDOF1")]    = {'vals':['False'], 'group':0}
    case_inputs[("ElastoDyn","TwSSDOF2")]    = {'vals':['False'], 'group':0}

    case_inputs[("ServoDyn","PCMode")]       = {'vals':[5], 'group':0}
    case_inputs[("ServoDyn","VSContrl")]     = {'vals':[5], 'group':0}

    case_inputs[("AeroDyn15","WakeMod")]     = {'vals':[1], 'group':0}
    case_inputs[("AeroDyn15","AFAeroMod")]   = {'vals':[2], 'group':0}
    case_inputs[("AeroDyn15","TwrPotent")]   = {'vals':[0], 'group':0}
    case_inputs[("AeroDyn15","TwrShadow")]   = {'vals':['False'], 'group':0}
    case_inputs[("AeroDyn15","TwrAero")]     = {'vals':['False'], 'group':0}
    case_inputs[("AeroDyn15","SkewMod")]     = {'vals':[1], 'group':0}
    case_inputs[("AeroDyn15","TipLoss")]     = {'vals':['True'], 'group':0}
    case_inputs[("AeroDyn15","HubLoss")]     = {'vals':['True'], 'group':0}
    case_inputs[("AeroDyn15","TanInd")]      = {'vals':['True'], 'group':0}
    case_inputs[("AeroDyn15","AIDrag")]      = {'vals':['True'], 'group':0}
    case_inputs[("AeroDyn15","TIDrag")]      = {'vals':['True'], 'group':0}
    case_inputs[("AeroDyn15","IndToler")]    = {'vals':[1.e-5], 'group':0}
    case_inputs[("AeroDyn15","MaxIter")]     = {'vals':[5000], 'group':0}
    case_inputs[("AeroDyn15","UseBlCm")]     = {'vals':['True'], 'group':0}
    
    if floating == True:
        case_inputs[("ElastoDyn","PtfmSurge")] = {'vals':ptfm_surge, 'group':1}
        case_inputs[("ElastoDyn","PtfmHeave")] = {'vals':ptfm_heave, 'group':1}
        case_inputs[("ElastoDyn","PtfmPitch")] = {'vals':ptfm_pitch, 'group':1}
        case_inputs[("HydroDyn","WaveHs")] = {'vals':metocean_Hs, 'group':1}
        case_inputs[("HydroDyn","WaveTp")] = {'vals':metocean_Tp, 'group':1}
        case_inputs[("HydroDyn","RdtnDT")] = {'vals':[dt], 'group':0}
        case_inputs[("HydroDyn","WaveMod")] = {'vals':[1], 'group':0}

    namebase += '_rated'
    case_list, case_name_list = CaseGen_General(case_inputs, dir_matrix=runDir, namebase=namebase)

    channels  = ["TipDxc1", "TipDyc1"]
    channels += ["RootMxc1", "RootMyc1", "RootMzc1", "RootMxc2", "RootMyc2", "RootMzc2", "RootMxc3", "RootMyc3", "RootMzc3"]
    channels += ["RootFxc1", "RootFyc1", "RootFzc1", "RootFxc2", "RootFyc2", "RootFzc2", "RootFxc3", "RootFyc3", "RootFzc3"]
    channels += ["RtAeroCp", "RotTorq", "RotThrust", "RotSpeed"]

    return case_list, case_name_list, channels

def RotorSE_DLC_1_4_Rated(fst_vt, runDir, namebase, TMax, turbine_class, turbulence_class, Vrated, U_init=[], Omega_init=[], pitch_init=[], Turbsim_exe=''):

    # Default Runtime
    T      = 60.
    TStart = 30.
    # TStart = 0.
    
    # Overwrite for testing
    if TMax < T:
        T      = TMax
        TStart = 0.


    iec = CaseGen_IEC()
    iec.init_cond[("ElastoDyn","RotSpeed")] = {'U':  U_init}
    iec.init_cond[("ElastoDyn","RotSpeed")]['val'] = Omega_init
    iec.init_cond[("ElastoDyn","BlPitch1")] = {'U':  U_init}
    iec.init_cond[("ElastoDyn","BlPitch1")]['val'] = pitch_init
    iec.init_cond[("ElastoDyn","BlPitch2")] = iec.init_cond[("ElastoDyn","BlPitch1")]
    iec.init_cond[("ElastoDyn","BlPitch3")] = iec.init_cond[("ElastoDyn","BlPitch1")]
    iec.Turbine_Class = turbine_class
    iec.Turbulence_Class = turbulence_class
    iec.D = fst_vt['ElastoDyn']['TipRad']*2.
    iec.z_hub = fst_vt['InflowWind']['RefHt']

    iec.dlc_inputs = {}
    iec.dlc_inputs['DLC']   = [1.4]
    iec.dlc_inputs['U']     = [[Vrated]]
    iec.dlc_inputs['Seeds'] = [[]]
    iec.dlc_inputs['Yaw']   = [[]]
    iec.transient_dir_change        = '-'  # '+','-','both': sign for transient events in EDC, EWS
    iec.transient_shear_orientation = 'v'  # 'v','h','both': vertical or horizontal shear for EWS

    iec.wind_dir        = runDir
    iec.case_name_base  = namebase + '_gust'
    iec.Turbsim_exe     = ''
    iec.debug_level     = 0
    iec.parallel_windfile_gen = False
    iec.run_dir         = runDir

    case_inputs = {}
    case_inputs[("Fst","TMax")]              = {'vals':[T], 'group':0}
    case_inputs[("Fst","TStart")]            = {'vals':[TStart], 'group':0}
    case_inputs[("Fst","OutFileFmt")]        = {'vals':[2], 'group':0}

    case_inputs[("ElastoDyn","YawDOF")]      = {'vals':['True'], 'group':0}
    case_inputs[("ElastoDyn","FlapDOF1")]    = {'vals':['True'], 'group':0}
    case_inputs[("ElastoDyn","FlapDOF2")]    = {'vals':['True'], 'group':0}
    case_inputs[("ElastoDyn","EdgeDOF")]     = {'vals':['True'], 'group':0}
    case_inputs[("ElastoDyn","DrTrDOF")]     = {'vals':['False'], 'group':0}
    case_inputs[("ElastoDyn","GenDOF")]      = {'vals':['True'], 'group':0} 
    case_inputs[("ElastoDyn","TwFADOF1")]    = {'vals':['False'], 'group':0}
    case_inputs[("ElastoDyn","TwFADOF2")]    = {'vals':['False'], 'group':0}
    case_inputs[("ElastoDyn","TwSSDOF1")]    = {'vals':['False'], 'group':0}
    case_inputs[("ElastoDyn","TwSSDOF2")]    = {'vals':['False'], 'group':0}

    case_inputs[("ServoDyn","PCMode")]       = {'vals':[5], 'group':0}
    case_inputs[("ServoDyn","VSContrl")]     = {'vals':[5], 'group':0}
    case_inputs[("ServoDyn","YCMode")]       = {'vals':[5], 'group':0}

    case_inputs[("AeroDyn15","WakeMod")]     = {'vals':[1], 'group':0}
    case_inputs[("AeroDyn15","AFAeroMod")]   = {'vals':[2], 'group':0}
    case_inputs[("AeroDyn15","TwrPotent")]   = {'vals':[0], 'group':0}
    case_inputs[("AeroDyn15","TwrShadow")]   = {'vals':['False'], 'group':0}
    case_inputs[("AeroDyn15","TwrAero")]     = {'vals':['False'], 'group':0}

    case_inputs[("AeroDyn15","SkewMod")]     = {'vals':[1], 'group':0}
    case_inputs[("AeroDyn15","TipLoss")]     = {'vals':['True'], 'group':0}
    case_inputs[("AeroDyn15","HubLoss")]     = {'vals':['True'], 'group':0}
    case_inputs[("AeroDyn15","TanInd")]      = {'vals':['True'], 'group':0}
    case_inputs[("AeroDyn15","AIDrag")]      = {'vals':['True'], 'group':0}
    case_inputs[("AeroDyn15","TIDrag")]      = {'vals':['True'], 'group':0}
    case_inputs[("AeroDyn15","IndToler")]    = {'vals':[1.e-5], 'group':0}
    case_inputs[("AeroDyn15","MaxIter")]     = {'vals':[5000], 'group':0}
    case_inputs[("AeroDyn15","UseBlCm")]     = {'vals':['True'], 'group':0}
    
    case_list, case_name_list = iec.execute(case_inputs=case_inputs)

    channels  = ["TipDxc1", "TipDyc1", "TipDzc1", "TipDxc2", "TipDyc2", "TipDzc2", "TipDxc3", "TipDyc3", "TipDzc3"]
    channels += ["RootMxc1", "RootMyc1", "RootMzc1", "RootMxc2", "RootMyc2", "RootMzc2", "RootMxc3", "RootMyc3", "RootMzc3"]
    channels += ["RootFxc1", "RootFyc1", "RootFzc1", "RootFxc2", "RootFyc2", "RootFzc2", "RootFxc3", "RootFyc3", "RootFzc3"]
    channels += ["RtAeroCp", "RotTorq", "RotThrust", "RotSpeed", "NacYaw"]

    channels += ["B1N1Fx", "B1N2Fx", "B1N3Fx", "B1N4Fx", "B1N5Fx", "B1N6Fx", "B1N7Fx", "B1N8Fx", "B1N9Fx"]
    channels += ["B1N1Fy", "B1N2Fy", "B1N3Fy", "B1N4Fy", "B1N5Fy", "B1N6Fy", "B1N7Fy", "B1N8Fy", "B1N9Fy"]

    return case_list, case_name_list, channels

def RotorSE_DLC_7_1_Steady(fst_vt, runDir, namebase, TMax, turbine_class, turbulence_class, U, U_init=[], Omega_init=[], pitch_init=[], Turbsim_exe=''):
    # Extreme 1yr return period wind speed with a power fault resulting in the blade not feathering

    # Default Runtime
    T      = 60.
    TStart = 30.
    
    # Overwrite for testing
    if TMax < T:
        T      = TMax
        TStart = 0.

    Pitch = 0.
    Omega = 0.

    case_inputs = {}
    case_inputs[("Fst","TMax")]              = {'vals':[T], 'group':0}
    case_inputs[("Fst","TStart")]            = {'vals':[TStart], 'group':0}
    case_inputs[("Fst","OutFileFmt")]        = {'vals':[2], 'group':0}
    
    case_inputs[("InflowWind","WindType")]   = {'vals':[1], 'group':0}
    case_inputs[("InflowWind","HWindSpeed")] = {'vals':[U], 'group':0}
    case_inputs[("InflowWind","PLexp")] = {'vals':[0.11], 'group':0}

    case_inputs[("ElastoDyn","RotSpeed")]    = {'vals':[Omega], 'group':0}
    case_inputs[("ElastoDyn","BlPitch1")]    = {'vals':[Pitch], 'group':0}
    case_inputs[("ElastoDyn","BlPitch2")]    = {'vals':[Pitch], 'group':0}
    case_inputs[("ElastoDyn","BlPitch3")]    = {'vals':[Pitch], 'group':0}
    case_inputs[("ElastoDyn","YawDOF")]      = {'vals':['True'], 'group':0}
    case_inputs[("ElastoDyn","FlapDOF1")]    = {'vals':['True'], 'group':0}
    case_inputs[("ElastoDyn","FlapDOF2")]    = {'vals':['True'], 'group':0}
    case_inputs[("ElastoDyn","EdgeDOF")]     = {'vals':['True'], 'group':0}
    case_inputs[("ElastoDyn","DrTrDOF")]     = {'vals':['False'], 'group':0}
    case_inputs[("ElastoDyn","GenDOF")]      = {'vals':['False'], 'group':0} 
    case_inputs[("ElastoDyn","TwFADOF1")]    = {'vals':['False'], 'group':0}
    case_inputs[("ElastoDyn","TwFADOF2")]    = {'vals':['False'], 'group':0}
    case_inputs[("ElastoDyn","TwSSDOF1")]    = {'vals':['False'], 'group':0}
    case_inputs[("ElastoDyn","TwSSDOF2")]    = {'vals':['False'], 'group':0}

    case_inputs[("ServoDyn","PCMode")]       = {'vals':[0], 'group':0}
    case_inputs[("ServoDyn","VSContrl")]     = {'vals':[5], 'group':0}
    case_inputs[("ServoDyn","YCMode")]       = {'vals':[5], 'group':0}

    case_inputs[("AeroDyn15","WakeMod")]     = {'vals':[1], 'group':0}
    case_inputs[("AeroDyn15","AFAeroMod")]   = {'vals':[1], 'group':0}
    case_inputs[("AeroDyn15","TwrPotent")]   = {'vals':[0], 'group':0}
    case_inputs[("AeroDyn15","TwrShadow")]   = {'vals':['False'], 'group':0}
    case_inputs[("AeroDyn15","TwrAero")]     = {'vals':['False'], 'group':0}

    case_inputs[("AeroDyn15","SkewMod")]     = {'vals':[1], 'group':0}
    case_inputs[("AeroDyn15","TipLoss")]     = {'vals':['True'], 'group':0}
    case_inputs[("AeroDyn15","HubLoss")]     = {'vals':['True'], 'group':0}
    case_inputs[("AeroDyn15","TanInd")]      = {'vals':['True'], 'group':0}
    case_inputs[("AeroDyn15","AIDrag")]      = {'vals':['True'], 'group':0}
    case_inputs[("AeroDyn15","TIDrag")]      = {'vals':['True'], 'group':0}
    case_inputs[("AeroDyn15","IndToler")]    = {'vals':[1.e-5], 'group':0}
    case_inputs[("AeroDyn15","MaxIter")]     = {'vals':[5000], 'group':0}
    case_inputs[("AeroDyn15","UseBlCm")]     = {'vals':['True'], 'group':0}
    

    namebase += '_idle50yr'
    case_list, case_name_list = CaseGen_General(case_inputs, namebase=namebase, save_matrix=False)

    channels  = ["TipDxc1", "TipDyc1", "TipDzc1", "TipDxc2", "TipDyc2", "TipDzc2", "TipDxc3", "TipDyc3", "TipDzc3"]
    channels += ["RootMxc1", "RootMyc1", "RootMzc1", "RootMxc2", "RootMyc2", "RootMzc2", "RootMxc3", "RootMyc3", "RootMzc3"]
    channels += ["RootFxc1", "RootFyc1", "RootFzc1", "RootFxc2", "RootFyc2", "RootFzc2", "RootFxc3", "RootFyc3", "RootFzc3"]
    channels += ["RtAeroCp", "RotTorq", "RotThrust", "RotSpeed", "NacYaw"]

    channels += ["B1N1Fx", "B1N2Fx", "B1N3Fx", "B1N4Fx", "B1N5Fx", "B1N6Fx", "B1N7Fx", "B1N8Fx", "B1N9Fx"]
    channels += ["B1N1Fy", "B1N2Fy", "B1N3Fy", "B1N4Fy", "B1N5Fy", "B1N6Fy", "B1N7Fy", "B1N8Fy", "B1N9Fy"]

    return case_list, case_name_list, channels

def RotorSE_DLC_1_1_Turb(fst_vt, runDir, namebase, TMax, turbine_class, turbulence_class, U, U_init=[], Omega_init=[], pitch_init=[], Turbsim_exe='', debug_level=0, cores=0, mpi_run=False, mpi_comm_map_down=[]):
    
    # Default Runtime
    T      = 60.
    TStart = 30.
    
    # Overwrite for testing
    if TMax < T:
        T      = TMax
        TStart = 0.


    iec = CaseGen_IEC()
    iec.init_cond[("ElastoDyn","RotSpeed")] = {'U':  U_init}
    iec.init_cond[("ElastoDyn","RotSpeed")]['val'] = [0.95*omega_i for omega_i in Omega_init]
    iec.init_cond[("ElastoDyn","BlPitch1")] = {'U':  U_init}
    iec.init_cond[("ElastoDyn","BlPitch1")]['val'] = pitch_init
    iec.init_cond[("ElastoDyn","BlPitch2")] = iec.init_cond[("ElastoDyn","BlPitch1")]
    iec.init_cond[("ElastoDyn","BlPitch3")] = iec.init_cond[("ElastoDyn","BlPitch1")]
    iec.Turbine_Class = turbine_class
    iec.Turbulence_Class = turbulence_class
    iec.D = fst_vt['ElastoDyn']['TipRad']*2.
    iec.z_hub = fst_vt['InflowWind']['RefHt']

    iec.dlc_inputs = {}
    iec.dlc_inputs['DLC']   = [1.1]
    iec.dlc_inputs['U']     = [[U]]
    # iec.dlc_inputs['Seeds'] = [[1]]
    iec.dlc_inputs['Seeds'] = [[1]] # nothing special about these seeds, randomly generated
    iec.dlc_inputs['Yaw']   = [[]]
    iec.transient_dir_change        = '-'  # '+','-','both': sign for transient events in EDC, EWS
    iec.transient_shear_orientation = 'v'  # 'v','h','both': vertical or horizontal shear for EWS

    iec.wind_dir        = runDir
    iec.case_name_base  = namebase + '_turb'
    iec.Turbsim_exe     = Turbsim_exe
    iec.debug_level     = debug_level
    iec.cores           = cores
    iec.run_dir         = runDir
    iec.overwrite       = True
    # iec.overwrite       = False
    if cores > 1:
        iec.parallel_windfile_gen = True
    else:
        iec.parallel_windfile_gen = False

    # mpi_run = False
    if mpi_run:
        iec.mpi_run           = mpi_run
        iec.comm_map_down = mpi_comm_map_down

    case_inputs = {}
    case_inputs[("Fst","TMax")]              = {'vals':[T], 'group':0}
    case_inputs[("Fst","TStart")]            = {'vals':[TStart], 'group':0}
    case_inputs[("Fst","OutFileFmt")]        = {'vals':[2], 'group':0}

    case_inputs[("ElastoDyn","YawDOF")]      = {'vals':['True'], 'group':0}
    case_inputs[("ElastoDyn","FlapDOF1")]    = {'vals':['True'], 'group':0}
    case_inputs[("ElastoDyn","FlapDOF2")]    = {'vals':['True'], 'group':0}
    case_inputs[("ElastoDyn","EdgeDOF")]     = {'vals':['True'], 'group':0}
    case_inputs[("ElastoDyn","DrTrDOF")]     = {'vals':['False'], 'group':0}
    case_inputs[("ElastoDyn","GenDOF")]      = {'vals':['True'], 'group':0} 
    case_inputs[("ElastoDyn","TwFADOF1")]    = {'vals':['False'], 'group':0}
    case_inputs[("ElastoDyn","TwFADOF2")]    = {'vals':['False'], 'group':0}
    case_inputs[("ElastoDyn","TwSSDOF1")]    = {'vals':['False'], 'group':0}
    case_inputs[("ElastoDyn","TwSSDOF2")]    = {'vals':['False'], 'group':0}

    case_inputs[("ServoDyn","PCMode")]       = {'vals':[5], 'group':0}
    case_inputs[("ServoDyn","VSContrl")]     = {'vals':[5], 'group':0}
    case_inputs[("ServoDyn","YCMode")]       = {'vals':[5], 'group':0}

    case_inputs[("AeroDyn15","WakeMod")]     = {'vals':[1], 'group':0}
    case_inputs[("AeroDyn15","AFAeroMod")]   = {'vals':[2], 'group':0}
    case_inputs[("AeroDyn15","TwrPotent")]   = {'vals':[0], 'group':0}
    case_inputs[("AeroDyn15","TwrShadow")]   = {'vals':['False'], 'group':0}
    case_inputs[("AeroDyn15","TwrAero")]     = {'vals':['False'], 'group':0}

    case_inputs[("AeroDyn15","SkewMod")]     = {'vals':[1], 'group':0}
    case_inputs[("AeroDyn15","TipLoss")]     = {'vals':['True'], 'group':0}
    case_inputs[("AeroDyn15","HubLoss")]     = {'vals':['True'], 'group':0}
    # case_inputs[("AeroDyn15","TanInd")]      = {'vals':['True'], 'group':0}
    # case_inputs[("AeroDyn15","AIDrag")]      = {'vals':['True'], 'group':0}
    # case_inputs[("AeroDyn15","TIDrag")]      = {'vals':['True'], 'group':0}
    # case_inputs[("AeroDyn15","IndToler")]    = {'vals':[1.e-5], 'group':0}
    # case_inputs[("AeroDyn15","MaxIter")]     = {'vals':[5000], 'group':0}
    case_inputs[("AeroDyn15","UseBlCm")]     = {'vals':['True'], 'group':0}
    
    case_list, case_name_list = iec.execute(case_inputs=case_inputs)

    channels  = ["TipDxc1", "TipDyc1", "TipDzc1", "TipDxc2", "TipDyc2", "TipDzc2", "TipDxc3", "TipDyc3", "TipDzc3"]
    channels += ["RootMxc1", "RootMyc1", "RootMzc1", "RootMxc2", "RootMyc2", "RootMzc2", "RootMxc3", "RootMyc3", "RootMzc3"]
    channels += ["RootFxc1", "RootFyc1", "RootFzc1", "RootFxc2", "RootFyc2", "RootFzc2", "RootFxc3", "RootFyc3", "RootFzc3"]
    channels += ["RtAeroCp", "RotTorq", "RotThrust", "RotSpeed", "NacYaw"]

    channels += ["B1N1Fx", "B1N2Fx", "B1N3Fx", "B1N4Fx", "B1N5Fx", "B1N6Fx", "B1N7Fx", "B1N8Fx", "B1N9Fx"]
    channels += ["B1N1Fy", "B1N2Fy", "B1N3Fy", "B1N4Fy", "B1N5Fy", "B1N6Fy", "B1N7Fy", "B1N8Fy", "B1N9Fy"]

    return case_list, case_name_list, channels


def RotorSE_DAC_rated(fst_vt, runDir, namebase, TMax, turbine_class, turbulence_class, Vrated, U_init=[], Omega_init=[], pitch_init=[], Turbsim_exe='', debug_level=0, cores=0, mpi_run=False, mpi_comm_map_down=[]):
    # Default Runtime
    T = 630. # 600.
    TStart = 0. #0.  # 30.

    # Overwrite for testing
    if TMax < T:
        T = TMax
        TStart = 0.

    iec = CaseGen_IEC()
    iec.TMax = T
    iec.init_cond[("ElastoDyn", "RotSpeed")] = {'U': U_init}
    iec.init_cond[("ElastoDyn", "RotSpeed")]['val'] = [0.95 * omega_i for omega_i in Omega_init]
    iec.init_cond[("ElastoDyn", "BlPitch1")] = {'U': U_init}
    iec.init_cond[("ElastoDyn", "BlPitch1")]['val'] = pitch_init
    iec.init_cond[("ElastoDyn", "BlPitch2")] = iec.init_cond[("ElastoDyn", "BlPitch1")]
    iec.init_cond[("ElastoDyn", "BlPitch3")] = iec.init_cond[("ElastoDyn", "BlPitch1")]


    iec.Turbine_Class = turbine_class
    iec.Turbulence_Class = turbulence_class
    iec.D = fst_vt['ElastoDyn']['TipRad'] * 2.
    iec.z_hub = fst_vt['InflowWind']['RefHt']

    iec.dlc_inputs = {}
    iec.dlc_inputs['DLC'] = [1.1]  # [1.1]
    # iec.dlc_inputs['U'] = [[U]]
    iec.dlc_inputs['U'] = [list(Vrated + np.arange(0, 10, 2))]
    # iec.dlc_inputs['Seeds'] = [[1]]
    iec.dlc_inputs['Seeds'] = [[13428, 1524]]  # nothing special about these seeds, randomly generated
    iec.dlc_inputs['Yaw'] = [[]]
    iec.transient_dir_change = '-'  # '+','-','both': sign for transient events in EDC, EWS
    iec.transient_shear_orientation = 'v'  # 'v','h','both': vertical or horizontal shear for EWS
    iec.TMax = 5.

    iec.wind_dir = runDir
    iec.case_name_base = namebase 
    iec.Turbsim_exe = Turbsim_exe
    iec.debug_level = debug_level
    iec.cores = cores
    iec.run_dir = runDir
    # iec.overwrite = True
    iec.overwrite       = False
    if cores > 1:
        iec.parallel_windfile_gen = True
    else:
        iec.parallel_windfile_gen = False

    # mpi_run = False
    if mpi_run:
        iec.mpi_run = mpi_run
        iec.comm_map_down = mpi_comm_map_down

    case_inputs = {}
    case_inputs[("Fst", "TMax")] = {'vals': [T], 'group': 0}
    case_inputs[("Fst", "TStart")] = {'vals': [TStart], 'group': 0}
    case_inputs[("Fst", "OutFileFmt")] = {'vals': [3], 'group': 0}

    case_inputs[("ElastoDyn", "YawDOF")] = {'vals': ['False'], 'group': 0}
    case_inputs[("ElastoDyn", "FlapDOF1")] = {'vals': ['True'], 'group': 0}
    case_inputs[("ElastoDyn", "FlapDOF2")] = {'vals': ['True'], 'group': 0}
    case_inputs[("ElastoDyn", "EdgeDOF")] = {'vals': ['False'], 'group': 0}  # <<< set to FALSE for now
    case_inputs[("ElastoDyn", "DrTrDOF")] = {'vals': ['False'], 'group': 0}
    case_inputs[("ElastoDyn", "GenDOF")] = {'vals': ['True'], 'group': 0}
    case_inputs[("ElastoDyn", "TwFADOF1")] = {'vals': ['False'], 'group': 0}
    case_inputs[("ElastoDyn", "TwFADOF2")] = {'vals': ['False'], 'group': 0}
    case_inputs[("ElastoDyn", "TwSSDOF1")] = {'vals': ['False'], 'group': 0}
    case_inputs[("ElastoDyn", "TwSSDOF2")] = {'vals': ['False'], 'group': 0}

    case_inputs[("ServoDyn", "PCMode")] = {'vals': [5], 'group': 0}
    case_inputs[("ServoDyn", "VSContrl")] = {'vals': [5], 'group': 0}
    case_inputs[("ServoDyn", "YCMode")] = {'vals': [0], 'group': 0}

    case_inputs[("AeroDyn15", "WakeMod")] = {'vals': [1], 'group': 0}
    case_inputs[("AeroDyn15", "AFAeroMod")] = {'vals': [2], 'group': 0}
    case_inputs[("AeroDyn15", "TwrPotent")] = {'vals': [0], 'group': 0}
    case_inputs[("AeroDyn15", "TwrShadow")] = {'vals': ['False'], 'group': 0}
    case_inputs[("AeroDyn15", "TwrAero")] = {'vals': ['False'], 'group': 0}

    case_inputs[("AeroDyn15", "SkewMod")] = {'vals': [2], 'group': 0}
    case_inputs[("AeroDyn15", "TipLoss")] = {'vals': ['True'], 'group': 0}
    case_inputs[("AeroDyn15", "HubLoss")] = {'vals': ['True'], 'group': 0}
    # case_inputs[("AeroDyn15","TanInd")]      = {'vals':['True'], 'group':0}
    # case_inputs[("AeroDyn15","AIDrag")]      = {'vals':['True'], 'group':0}
    # case_inputs[("AeroDyn15","TIDrag")]      = {'vals':['True'], 'group':0}
    # case_inputs[("AeroDyn15","IndToler")]    = {'vals':[1.e-5], 'group':0}
    # case_inputs[("AeroDyn15","MaxIter")]     = {'vals':[5000], 'group':0}
    case_inputs[("AeroDyn15", "UseBlCm")] = {'vals': ['True'], 'group': 0}

    case_list, case_name_list = iec.execute(case_inputs=case_inputs)

    channels = ["TipDxc1", "TipDyc1", "TipDzc1", "TipDxc2", "TipDyc2", "TipDzc2", "TipDxc3", "TipDyc3", "TipDzc3", "Azimuth"]
    channels += ["RootMxc1", "RootMyc1", "RootMzc1", "RootMxc2", "RootMyc2", "RootMzc2", "RootMxc3", "RootMyc3", "RootMzc3"]
    channels += ["RootFxc1", "RootFyc1", "RootFzc1", "RootFxc2", "RootFyc2", "RootFzc2", "RootFxc3", "RootFyc3", "RootFzc3"]
    channels += ["RtAeroCp", "RotTorq", "RotThrust", "RotSpeed", "NacYaw"]

    channels += ["B1N1Fx", "B1N2Fx", "B1N3Fx", "B1N4Fx", "B1N5Fx", "B1N6Fx", "B1N7Fx", "B1N8Fx", "B1N9Fx"]
    channels += ["B1N1Fy", "B1N2Fy", "B1N3Fy", "B1N4Fy", "B1N5Fy", "B1N6Fy", "B1N7Fy", "B1N8Fy", "B1N9Fy"]

    channels += ["Wind1VelX", "Wind1VelY", "Wind1VelZ"]
    channels += ["BLFLAP1", "BLFLAP2", "BLFLAP3"]


    return case_list, case_name_list, channels


def RotorSE_steady_wind(fst_vt, runDir, namebase, TMax, turbine_class, turbulence_class, Vrated, U_init=[], Omega_init=[], pitch_init=[], Turbsim_exe='', debug_level=0, cores=0, mpi_run=False, mpi_comm_map_down=[]):
    # Default Runtime
    T = 30. # 600.
    TStart = 0. #0.  # 30.

    # Overwrite for testing
    if TMax < T:
        T = TMax
        TStart = 0.

    # iec = CaseGen_IEC()
    # iec.TMax = T
    # iec.init_cond[("ElastoDyn", "RotSpeed")] = {'U': U_init}
    # iec.init_cond[("ElastoDyn", "RotSpeed")]['val'] = [0.95 * omega_i for omega_i in Omega_init]
    # iec.init_cond[("ElastoDyn", "BlPitch1")] = {'U': U_init}
    # iec.init_cond[("ElastoDyn", "BlPitch1")]['val'] = pitch_init
    # iec.init_cond[("ElastoDyn", "BlPitch2")] = iec.init_cond[("ElastoDyn", "BlPitch1")]
    # iec.init_cond[("ElastoDyn", "BlPitch3")] = iec.init_cond[("ElastoDyn", "BlPitch1")]


    # iec.Turbine_Class = turbine_class
    # iec.Turbulence_Class = turbulence_class
    # iec.D = fst_vt['ElastoDyn']['TipRad'] * 2.
    # iec.z_hub = fst_vt['InflowWind']['RefHt']

    # iec.dlc_inputs = {}
    # iec.dlc_inputs['DLC'] = [1.1]  # [1.1]
    # # iec.dlc_inputs['U'] = [[U]]
    # iec.dlc_inputs['U'] = [list(Vrated + np.arange(0, 10, 2))]
    # # iec.dlc_inputs['Seeds'] = [[1]]
    # iec.dlc_inputs['Seeds'] = [[13428, 1524]]  # nothing special about these seeds, randomly generated
    # iec.dlc_inputs['Yaw'] = [[]]
    # iec.transient_dir_change = '-'  # '+','-','both': sign for transient events in EDC, EWS
    # iec.transient_shear_orientation = 'v'  # 'v','h','both': vertical or horizontal shear for EWS
    # iec.TMax = 5.

    # iec.wind_dir = runDir
    # iec.case_name_base = namebase 
    # iec.Turbsim_exe = Turbsim_exe
    # iec.debug_level = debug_level
    # iec.cores = cores
    # iec.run_dir = runDir
    # # iec.overwrite = True
    # iec.overwrite       = False
    # if cores > 1:
    #     iec.parallel_windfile_gen = True
    # else:
    #     iec.parallel_windfile_gen = False

    # mpi_run = False
    if mpi_run:
        iec.mpi_run = mpi_run
        iec.comm_map_down = mpi_comm_map_down

    case_inputs = {}
    case_inputs[("Fst", "TMax")] = {'vals': [T], 'group': 0}
    case_inputs[("Fst", "TStart")] = {'vals': [TStart], 'group': 0}
    case_inputs[("Fst", "OutFileFmt")] = {'vals': [3], 'group': 0}

    case_inputs[("InflowWind","WindType")]   = {'vals':[1], 'group':0}
    case_inputs[("InflowWind","HWindSpeed")] = {'vals':[Vrated], 'group':0}

    case_inputs[("ElastoDyn", "YawDOF")]   = {'vals': ['False'], 'group': 0}
    case_inputs[("ElastoDyn", "FlapDOF1")] = {'vals': ['False'], 'group': 0}
    case_inputs[("ElastoDyn", "FlapDOF2")] = {'vals': ['False'], 'group': 0}
    case_inputs[("ElastoDyn", "EdgeDOF")]  = {'vals': ['False'], 'group': 0}  # <<< set to FALSE for now
    case_inputs[("ElastoDyn", "DrTrDOF")]  = {'vals': ['False'], 'group': 0}
    case_inputs[("ElastoDyn", "GenDOF")]   = {'vals': ['False'], 'group': 0}
    case_inputs[("ElastoDyn", "TwFADOF1")] = {'vals': ['False'], 'group': 0}
    case_inputs[("ElastoDyn", "TwFADOF2")] = {'vals': ['False'], 'group': 0}
    case_inputs[("ElastoDyn", "TwSSDOF1")] = {'vals': ['False'], 'group': 0}
    case_inputs[("ElastoDyn", "TwSSDOF2")] = {'vals': ['False'], 'group': 0}

    case_inputs[("ServoDyn", "PCMode")] = {'vals': [0], 'group': 0}
    case_inputs[("ServoDyn", "VSContrl")] = {'vals': [0], 'group': 0}
    case_inputs[("ServoDyn", "YCMode")] = {'vals': [0], 'group': 0}

    case_inputs[("AeroDyn15", "WakeMod")] = {'vals': [1], 'group': 0}
    case_inputs[("AeroDyn15", "AFAeroMod")] = {'vals': [2], 'group': 0}
    case_inputs[("AeroDyn15", "TwrPotent")] = {'vals': [0], 'group': 0}
    case_inputs[("AeroDyn15", "TwrShadow")] = {'vals': ['False'], 'group': 0}
    case_inputs[("AeroDyn15", "TwrAero")] = {'vals': ['False'], 'group': 0}

    case_inputs[("AeroDyn15", "SkewMod")] = {'vals': [2], 'group': 0}
    case_inputs[("AeroDyn15", "TipLoss")] = {'vals': ['True'], 'group': 0}
    case_inputs[("AeroDyn15", "HubLoss")] = {'vals': ['True'], 'group': 0}
    # case_inputs[("AeroDyn15","TanInd")]      = {'vals':['True'], 'group':0}
    # case_inputs[("AeroDyn15","AIDrag")]      = {'vals':['True'], 'group':0}
    # case_inputs[("AeroDyn15","TIDrag")]      = {'vals':['True'], 'group':0}
    # case_inputs[("AeroDyn15","IndToler")]    = {'vals':[1.e-5], 'group':0}
    # case_inputs[("AeroDyn15","MaxIter")]     = {'vals':[5000], 'group':0}
    case_inputs[("AeroDyn15", "UseBlCm")] = {'vals': ['True'], 'group': 0}

    # case_list, case_name_list = iec.execute(case_inputs=case_inputs)
    case_list, case_name_list = CaseGen_General(case_inputs, dir_matrix=runDir, namebase=namebase)

    channels = ["TipDxc1", "TipDyc1", "TipDzc1", "TipDxc2", "TipDyc2", "TipDzc2", "TipDxc3", "TipDyc3", "TipDzc3", "Azimuth"]
    channels += ["RootMxc1", "RootMyc1", "RootMzc1", "RootMxc2", "RootMyc2", "RootMzc2", "RootMxc3", "RootMyc3", "RootMzc3"]
    channels += ["RootFxc1", "RootFyc1", "RootFzc1", "RootFxc2", "RootFyc2", "RootFzc2", "RootFxc3", "RootFyc3", "RootFzc3"]
    channels += ["RtAeroCp", "RotTorq", "RotThrust", "RotSpeed", "NacYaw"]

    channels += ["B1N1Fx", "B1N2Fx", "B1N3Fx", "B1N4Fx", "B1N5Fx", "B1N6Fx", "B1N7Fx", "B1N8Fx", "B1N9Fx"]
    channels += ["B1N1Fy", "B1N2Fy", "B1N3Fy", "B1N4Fy", "B1N5Fy", "B1N6Fy", "B1N7Fy", "B1N8Fy", "B1N9Fy"]

    channels += ["Wind1VelX", "Wind1VelY", "Wind1VelZ"]
    channels += ["BLFLAP1", "BLFLAP2", "BLFLAP3"]


    return case_list, case_name_list, channels


def set_channels():
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
                                       "TipRDxr", "TipRDyr", "TipRDzr","RtVAvgxh"]:
        channels[var] = True
    return channels

if __name__ == "__main__":

    # power_curve()
    weis_dir = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
    discon = "/Users/dzalkind/Tools/WEIS-3/ROSCO_toolbox/ROSCO_testing/DISCON-UMaineSemi_NoPS.IN"
    run_dir = os.path.join(weis_dir,'results','step_test')

    case_list, case_name_list, channels = steps(discon,run_dir,'test0')

    print('here')


