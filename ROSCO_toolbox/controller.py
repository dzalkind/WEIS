# Copyright 2019 NREL

# Licensed under the Apache License, Version 2.0 (the "License"); you may not use
# this file except in compliance with the License. You may obtain a copy of the
# License at http://www.apache.org/licenses/LICENSE-2.0

# Unless required by applicable law or agreed to in writing, software distributed
# under the License is distributed on an "AS IS" BASIS, WITHOUT WARRANTIES OR
# CONDITIONS OF ANY KIND, either express or implied. See the License for the
# specific language governing permissions and limitations under the License.

import numpy as np
import sys
import datetime
from scipy import interpolate, gradient, integrate

# Some useful constants
now = datetime.datetime.now()
pi = np.pi
rad2deg = np.rad2deg(1)
deg2rad = np.deg2rad(1)
rpm2RadSec = 2.0*(np.pi)/60.0
RadSec2rpm = 60/(2.0 * np.pi)

class Controller():
    """
    Class Controller used to calculate controller tunings parameters


    Methods:
    -------
    tune_controller

    Parameters:
    -----------
    controller_params: dict
                       Dictionary containing controller paramaters that need to be defined
    """

    def __init__(self, controller_params):
        ''' 
        Load controller tuning parameters from input dictionary
        '''

        print('-----------------------------------------------------------------------------')
        print('   Tuning a reference wind turbine controller using NREL\'s ROSCO toolbox    ')
        # print('      Developed by Nikhar J. Abbas for collaborative research purposes.      ')
        print('-----------------------------------------------------------------------------')

        # Controller Flags
        self.LoggingLevel = controller_params['LoggingLevel']
        self.F_LPFType = controller_params['F_LPFType']
        self.F_NotchType = controller_params['F_NotchType']
        self.IPC_ControlMode = controller_params['IPC_ControlMode']
        self.VS_ControlMode = controller_params['VS_ControlMode']
        self.PC_ControlMode = controller_params['PC_ControlMode']
        self.Y_ControlMode = controller_params['Y_ControlMode']
        self.SS_Mode = controller_params['SS_Mode']
        self.WE_Mode = controller_params['WE_Mode']
        self.PS_Mode = controller_params['PS_Mode']
        self.SD_Mode = controller_params['SD_Mode']
        self.Fl_Mode = controller_params['Fl_Mode']
        self.Flp_Mode = controller_params['Flp_Mode']

        # Necessary parameters
        self.zeta_pc = controller_params['zeta_pc']
        self.omega_pc = controller_params['omega_pc']
        self.zeta_vs = controller_params['zeta_vs']
        self.omega_vs = controller_params['omega_vs']
        if self.Flp_Mode > 0:
            self.zeta_flp = controller_params['zeta_flp']
            self.omega_flp = controller_params['omega_flp']

        # Optional parameters, default to standard if not defined
        if isinstance(controller_params['min_pitch'], float):
            self.min_pitch = controller_params['min_pitch']
        else:
            self.min_pitch = None
        
        if controller_params['max_pitch']:
            self.max_pitch = controller_params['max_pitch']
        else:
            self.max_pitch = 90*deg2rad      # Default to 90 degrees max pitch
        
        if controller_params['vs_minspd']:
            self.vs_minspd = controller_params['vs_minspd']
        else:
            self.vs_minspd = None 

        if controller_params['ss_vsgain']:
            self.ss_vsgain = controller_params['ss_vsgain']
        else:
            self.ss_vsgain = 1.      # Default to 100% setpoint shift
        
        if controller_params['ss_pcgain']:
            self.ss_pcgain = controller_params['ss_pcgain']
        else:
            self.ss_pcgain = 0.001      # Default to 0.1% setpoint shift
        
        if controller_params['ps_percent']:
            self.ps_percent = controller_params['ps_percent']
        else:
            self.ps_percent = 0.75      # Default to 75% peak shaving

        # critical damping if LPFType = 2
        if controller_params['F_LPFType']:
            if controller_params['F_LPFType'] == 2:
                self.F_LPFDamping = 0.7
            else:
                self.F_LPFDamping = 0.0
        else:
            self.F_LPFDamping = 0.0

        # Shutdown filter default cornering freq at 15s time constant
        if controller_params['sd_cornerfreq']:
            self.sd_cornerfreq = controller_params['sd_cornerfreq']
        else:
            self.sd_cornerfreq = 0.41888
        
        if controller_params['sd_maxpit']:
            self.sd_maxpit = controller_params['sd_maxpit']
        else:
            self.sd_maxpit = None

        if controller_params['flp_maxpit']:
            self.flp_maxpit = controller_params['flp_maxpit']
        else:
            if controller_params['Flp_Mode'] > 0:
                self.flp_maxpit = 10.0 * deg2rad
            else:
                self.flp_maxpit = 0.0

        # Filters
        if 'filter_params' in controller_params:
            if controller_params['filter_params']['f_we_cornerfreq']:
                self.f_we_cornerfreq    = controller_params['filter_params']['f_we_cornerfreq']
            else:
                self.f_we_cornerfreq    = 0.20944
            if controller_params['filter_params']['f_fl_highpassfreq']:
                self.f_fl_highpassfreq    = controller_params['filter_params']['f_fl_highpassfreq']
            else:
                self.f_fl_highpassfreq    = 0.01042
            if controller_params['filter_params']['f_ss_cornerfreq']:
                self.f_ss_cornerfreq = controller_params['f_ss_cornerfreq']
            else:
                self.f_ss_cornerfreq = .62831850001     # Default to 10 second time constant 
        else:
            self.f_we_cornerfreq    = 0.20944
            self.f_fl_highpassfreq    = 0.01042
            self.f_ss_cornerfreq = .62831850001
        
        # power controller params
        if 'PwC_Mode' in controller_params:
            self.PwC_Mode = controller_params['PwC_Mode']
            if 'PwC_ConstPwr' in controller_params:
                self.PwC_ConstPwr    = controller_params['PwC_ConstPwr']
            else:
                self.PwC_ConstPwr    = 1.0

            if 'PwC_OpenLoop_Inp' in controller_params:
                self.PwC_OpenLoop_Inp = controller_params['PwC_OpenLoop_Inp']
            else:
                self.PwC_OpenLoop_Inp = ""
                
        else:
            self.PwC_Mode       = 0
            self.PwC_ConstPwr        = 1.0
            self.PwC_OpenLoop_Inp  = ""

        # soft start (open loop power control)
        if 'soft_start' in controller_params:
            self.SoftStart = SoftStart(self,controller_params['soft_start'])
            self.PwC_OpenLoop_Inp  = self.SoftStart.filename

        # soft cut-out (open loop power vs. wind speed)
        if 'soft_cut_out' in controller_params:
            self.SoftCutOut = SoftCutOut(self,controller_params['soft_cut_out'])
            self.PwC_OpenLoop_Inp  = self.SoftCutOut.filename
            
        if 'open_loop' in controller_params:
            # Set open loop control mode
            ol_params = controller_params['open_loop']
            ol_index_counter = 2

            self.OL_Mode = 1
            self.OL_Ind_Breakpoint = 1

            if 'blade_pitch' in ol_params:
                self.OL_Ind_BldPitch = ol_index_counter
                ol_index_counter += 1
            else:
                self.OL_Ind_BldPitch = 0

            if 'generator_torque' in ol_params:
                self.OL_Ind_GenTq = ol_index_counter
                ol_index_counter += 1
            else:
                self.OL_Ind_GenTq = 0

            if 'yaw_rate' in ol_params:
                self.OL_Ind_YawRate = ol_index_counter
                ol_index_counter += 1
            else:
                self.OL_Ind_YawRate = 0

            if 'yaw_angle' in ol_params:
                if 'yaw_rate' in ol_params:
                    print('ROSCO Toolbox Warning: both yaw_rate and yaw_angle set as open loop input, using yaw_rate only')
                else:
                    self.OL_Ind_YawRate = ol_index_counter
                    ol_index_counter += 1

            else:
                self.OL_Ind_YawRate = 0

            # Input file
            if 'filename' in controller_params['open_loop']:
                self.OL_Filename = controller_params['open_loop']['filename']
            else:
                self.OL_Filename = 'open_loop_input.dat'

            # Set up open loop control inputs here
            self.OpenLoopControl    = OpenLoopControl(self,ol_params)
        else:
            self.OL_Mode = 0
            self.OL_Filename        = "unused"
            self.OL_Ind_Breakpoint  = 0
            self.OL_Ind_BldPitch    = 0
            self.OL_Ind_GenTq       = 0
            self.OL_Ind_YawRate     = 0


    def tune_controller(self, turbine):
        """
        Given a turbine model, tune a controller based on the NREL generic controller tuning process

        Parameters:
        -----------
        turbine : class
                  Turbine class containing necessary turbine information to accurately tune the controller. 
        """
        # -------------Load Parameters ------------- #
        # Re-define Turbine Parameters for shorthand
        J = turbine.J                           # Total rotor inertial (kg-m^2) 
        rho = turbine.rho                       # Air density (kg/m^3)
        R = turbine.rotor_radius                    # Rotor radius (m)
        Ar = np.pi*R**2                         # Rotor area (m^2)
        Ng = turbine.Ng                         # Gearbox ratio (-)
        rated_rotor_speed = turbine.rated_rotor_speed               # Rated rotor speed (rad/s)


        # -------------Define Operation Points ------------- #
        TSR_rated = rated_rotor_speed*R/turbine.v_rated  # TSR at rated

        # separate wind speeds by operation regions
        v_below_rated = np.linspace(turbine.v_min,turbine.v_rated, num=30)             # below rated
        v_above_rated = np.linspace(turbine.v_rated,turbine.v_max, num=30)             # above rated
        v = np.concatenate((v_below_rated, v_above_rated))

        # separate TSRs by operations regions
        TSR_below_rated = np.ones(len(v_below_rated))*turbine.TSR_operational # below rated     
        TSR_above_rated = rated_rotor_speed*R/v_above_rated                   # above rated
        # TSR_below_rated = np.minimum(np.max(TSR_above_rated), TSR_below_rated)
        TSR_op = np.concatenate((TSR_below_rated, TSR_above_rated))   # operational TSRs

        # Find expected operational Cp values
        Cp_above_rated = turbine.Cp.interp_surface(0,TSR_above_rated[0])             # Cp during rated operation (not optimal). Assumes cut-in bld pitch to be 0
        Cp_op_br = np.ones(len(v_below_rated)) * turbine.Cp.max              # below rated
        Cp_op_ar = Cp_above_rated * (TSR_above_rated/TSR_rated)**3           # above rated
        Cp_op = np.concatenate((Cp_op_br, Cp_op_ar))                # operational CPs to linearize around
        pitch_initial_rad = turbine.pitch_initial_rad
        TSR_initial = turbine.TSR_initial

        # initialize variables
        pitch_op    = np.empty(len(TSR_op))
        dCp_beta    = np.empty(len(TSR_op))
        dCp_TSR     = np.empty(len(TSR_op))
        dCt_beta    = np.empty(len(TSR_op))
        dCt_TSR     = np.empty(len(TSR_op))
        Ct_op       = np.empty(len(TSR_op))

        # ------------- Find Linearized State "Matrices" ------------- #
        for i in range(len(TSR_op)):
            # Find pitch angle as a function of expected operating CP for each TSR
            Cp_TSR = np.ndarray.flatten(turbine.Cp.interp_surface(turbine.pitch_initial_rad, TSR_op[i]))     # all Cp values for a given tsr
            Cp_op[i] = np.clip(Cp_op[i], np.min(Cp_TSR), np.max(Cp_TSR))        # saturate Cp values to be on Cp surface
            f_cp_pitch = interpolate.interp1d(Cp_TSR,pitch_initial_rad)         # interpolate function for Cp(tsr) values
            # expected operation blade pitch values
            if v[i] <= turbine.v_rated and isinstance(self.min_pitch, float): # Below rated & defined min_pitch
                pitch_op[i] = min(self.min_pitch, f_cp_pitch(Cp_op[i]))
            elif isinstance(self.min_pitch, float):
                pitch_op[i] = max(self.min_pitch, f_cp_pitch(Cp_op[i]))             
            else:
                pitch_op[i] = f_cp_pitch(Cp_op[i])     

            dCp_beta[i], dCp_TSR[i] = turbine.Cp.interp_gradient(pitch_op[i],TSR_op[i])       # gradients of Cp surface in Beta and TSR directions
            dCt_beta[i], dCt_TSR[i] = turbine.Ct.interp_gradient(pitch_op[i],TSR_op[i])       # gradients of Cp surface in Beta and TSR directions
        
            # Thrust
            Ct_TSR      = np.ndarray.flatten(turbine.Ct.interp_surface(turbine.pitch_initial_rad, TSR_op[i]))     # all Cp values for a given tsr
            f_ct        = interpolate.interp1d(pitch_initial_rad,Ct_TSR)
            Ct_op[i]    = f_ct(pitch_op[i])
            Ct_op[i]    = np.clip(Ct_op[i], np.min(Ct_TSR), np.max(Ct_TSR))        # saturate Ct values to be on Ct surface


        # Define minimum pitch saturation to be at Cp-maximizing pitch angle if not specifically defined
        if not isinstance(self.min_pitch, float):
            self.min_pitch = pitch_op[0]

        # Full Cx surface gradients
        dCp_dbeta   = dCp_beta/np.diff(pitch_initial_rad)[0]
        dCp_dTSR    = dCp_TSR/np.diff(TSR_initial)[0]
        dCt_dbeta   = dCt_beta/np.diff(pitch_initial_rad)[0]
        dCt_dTSR    = dCt_TSR/np.diff(TSR_initial)[0]
        
        # Linearized system derivatives
        dtau_dbeta      = Ng/2*rho*Ar*R*(1/TSR_op)*dCp_dbeta*v**2
        dtau_dlambda    = Ng/2*rho*Ar*R*v**2*(1/(TSR_op**2))*(dCp_dTSR*TSR_op - Cp_op)
        dlambda_domega  = R/v/Ng
        dtau_domega     = dtau_dlambda*dlambda_domega

        dlambda_dv      = -(TSR_op/v)

        Pi_beta         = 1/2 * rho * Ar * v**2 * dCt_dbeta
        Pi_omega        = 1/2 * rho * Ar * R * v * dCt_dTSR
        Pi_wind         = 1/2 * rho * Ar * v**2 * dCt_dTSR * dlambda_dv + rho * Ar * v * Ct_op

        # Second order system coefficients
        A = dtau_domega/J             # Plant pole
        B_tau = -Ng**2/J              # Torque input  
        B_beta = dtau_dbeta/J         # Blade pitch input 

        # Wind Disturbance Input
        dtau_dv = (0.5 * rho * Ar * 1/rated_rotor_speed) * (dCp_dTSR*dlambda_dv*v**3 + Cp_op*3*v**2) 
        B_wind = dtau_dv/J # wind speed input - currently unused 


        # separate and define below and above rated parameters
        A_vs = A[0:len(v_below_rated)]          # below rated
        A_pc = A[-len(v_above_rated)+1:]     # above rated
        B_tau = B_tau * np.ones(len(v))

        # -- Find gain schedule --
        self.pc_gain_schedule = ControllerTypes()
        self.pc_gain_schedule.second_order_PI(self.zeta_pc, self.omega_pc,A_pc,B_beta[-len(v_above_rated)+1:],linearize=True,v=v_above_rated[1:])
        self.vs_gain_schedule = ControllerTypes()
        self.vs_gain_schedule.second_order_PI(self.zeta_vs, self.omega_vs,A_vs,B_tau[0:len(v_below_rated)],linearize=False,v=v_below_rated)

        # -- Find K for Komega_g^2 --
        self.vs_rgn2K = (pi*rho*R**5.0 * turbine.Cp.max) / (2.0 * turbine.Cp.TSR_opt**3 * Ng**3)/ (turbine.GenEff/100 * turbine.GBoxEff/100)
        self.vs_refspd = min(turbine.TSR_operational * turbine.v_rated/R, turbine.rated_rotor_speed) * Ng

        # -- Define some setpoints --
        # minimum rotor speed saturation limits
        if self.vs_minspd:
            self.vs_minspd = np.maximum(self.vs_minspd, (turbine.TSR_operational * turbine.v_min / turbine.rotor_radius) * Ng)
        else: 
            self.vs_minspd = (turbine.TSR_operational * turbine.v_min / turbine.rotor_radius) * Ng
        self.pc_minspd = self.vs_minspd

        # max pitch angle for shutdown
        if self.sd_maxpit:
            self.sd_maxpit = self.sd_maxpit
        else:
            self.sd_maxpit = pitch_op[-1]

        # Store some variables
        self.v              = v                                  # Wind speed (m/s)
        self.v_below_rated  = v_below_rated
        self.pitch_op       = pitch_op
        self.pitch_op_pc    = pitch_op[-len(v_above_rated)+1:]
        self.TSR_op         = TSR_op
        self.A              = A 
        self.B_beta         = B_beta
        self.B_tau          = B_tau
        self.B_wind         = B_wind
        self.TSR_op         = TSR_op
        self.omega_op       = np.minimum(turbine.rated_rotor_speed, TSR_op*v/R)
        self.Pi_omega       = Pi_omega
        self.Pi_beta        = Pi_beta
        self.Pi_wind        = Pi_wind

        # - Might want these to debug -
        # self.Cp_op = Cp_op

        # --- Minimum pitch saturation ---
        self.ps_min_bld_pitch = np.ones(len(self.pitch_op)) * self.min_pitch
        self.ps = ControllerBlocks()

        if self.PS_Mode == 1:  # Peak Shaving
            self.ps.peak_shaving(self, turbine)
        elif self.PS_Mode == 2: # Cp-maximizing minimum pitch saturation
            self.ps.min_pitch_saturation(self,turbine)
        elif self.PS_Mode == 3: # Peak shaving and Cp-maximizing minimum pitch saturation
            self.ps.peak_shaving(self, turbine)
            self.ps.min_pitch_saturation(self,turbine)

        # --- Floating feedback term ---
        if self.Fl_Mode == 1: # Floating feedback
            Kp_float = (dtau_dv/dtau_dbeta) * turbine.TowerHt * Ng 
            f_kp     = interpolate.interp1d(v,Kp_float)
            self.Kp_float = f_kp(turbine.v_rated * (1.05))   # get Kp at v_rated + 0.5 m/s
            # Turn on the notch filter if floating
            self.F_NotchType = 2
            
            # And check for .yaml input inconsistencies
            if turbine.twr_freq == 0.0 or turbine.ptfm_freq == 0.0:
                print('WARNING: twr_freq and ptfm_freq should be defined for floating turbine control!!')
        else:
            self.Kp_float = 0.0

        # --- Individual pitch control ---
        self.Ki_ipc1p = 0.0
        
        # Flap actuation 
        if self.Flp_Mode >= 1:
            self.flp_angle = 0.0
            try:
                self.tune_flap_controller(turbine)
            except AttributeError:
                print('ERROR: If Flp_Mode > 0, you need to have blade information loaded in the turbine object.')
                raise
            except UnboundLocalError:
                print('ERROR: You are attempting to tune a flap controller for a blade without flaps!')
                raise
        else:
            self.flp_angle = 0.0
            self.Ki_flap = np.array([0.0])
            self.Kp_flap = np.array([0.0])

        # Active power control
        self.PwC_R, self.PwC_BldPitchMin = self.power_control(turbine.Cp)

    def tune_flap_controller(self,turbine):
        '''
        Tune controller for distributed aerodynamic control

        Parameters:
        -----------
        turbine : class
                  Turbine class containing necessary turbine information to accurately tune the controller. 
        '''
        # Find blade aerodynamic coefficients
        v_rel = []
        phi_vec = []
        alpha=[]
        for i, _ in enumerate(self.v):
            turbine.cc_rotor.induction_inflow=True
            # Axial and tangential inductions
            try: 
                a, ap, alpha0, cl, cd = turbine.cc_rotor.distributedAeroLoads(
                                                self.v[i], self.omega_op[i], self.pitch_op[i], 0.0)
            except ValueError:
                loads, derivs = turbine.cc_rotor.distributedAeroLoads(
                                                self.v[i], self.omega_op[i], self.pitch_op[i], 0.0)
                a = loads['a']
                ap = loads['ap']
                alpha0 = loads['alpha']
                cl = loads['Cl']
                cd = loads['Cd']
                 
            # Relative windspeed
            v_rel.append([np.sqrt(self.v[i]**2*(1-a)**2 + self.omega_op[i]**2*turbine.span**2*(1-ap)**2)])
            # Inflow wind direction
            phi_vec.append(self.pitch_op[i] + turbine.twist*deg2rad)

        # Lift and drag coefficients
        num_af = len(turbine.af_data) # number of airfoils
        Cl0 = np.zeros(num_af)
        Cd0 = np.zeros(num_af)
        Clp = np.zeros(num_af)
        Cdp = np.zeros(num_af)
        Clm = np.zeros(num_af)
        Cdm = np.zeros(num_af)
        
        for i,section in enumerate(turbine.af_data):
            # assume airfoil section as AOA of zero for slope calculations - for now
            a0_ind = section[0]['Alpha'].index(np.min(np.abs(section[0]['Alpha'])))
            # Coefficients 
            if section[0]['NumTabs'] == 3:  # sections with 3 flaps
                Clm[i,] = section[0]['Cl'][a0_ind]
                Cdm[i,] = section[0]['Cd'][a0_ind]
                Cl0[i,] = section[1]['Cl'][a0_ind]
                Cd0[i,] = section[1]['Cd'][a0_ind]
                Clp[i,] = section[2]['Cl'][a0_ind]
                Cdp[i,] = section[2]['Cd'][a0_ind]
                Ctrl_flp = float(section[2]['Ctrl'])
            else:                           # sections without 3 flaps
                Cl0[i,] = Clp[i,] = Clm[i,] = section[0]['Cl'][a0_ind]
                Cd0[i,] = Cdp[i,] = Cdm[i,] = section[0]['Cd'][a0_ind]
                Ctrl = float(section[0]['Ctrl'])

        # Find slopes
        Kcl = (Clp - Cl0)/( (Ctrl_flp-Ctrl)*deg2rad )
        Kcd = (Cdp - Cd0)/( (Ctrl_flp-Ctrl)*deg2rad )

        # Find integrated constants
        self.kappa = np.zeros(len(v_rel))
        C1 = np.zeros(len(v_rel))
        C2 = np.zeros(len(v_rel))
        for i, (v_sec,phi) in enumerate(zip(v_rel, phi_vec)):
            C1[i] = integrate.trapz(0.5 * turbine.rho * turbine.chord * v_sec[0]**2 * turbine.span * Kcl * np.cos(phi))
            C2[i] = integrate.trapz(0.5 * turbine.rho * turbine.chord * v_sec[0]**2 * turbine.span * Kcd * np.sin(phi))
            self.kappa[i]=C1[i]+C2[i]

        # ------ Controller tuning -------
        # Open loop blade response
        zetaf  = turbine.bld_flapwise_damp
        omegaf = turbine.bld_flapwise_freq
        
        # Desired Closed loop response
        # zeta  = self.zeta_flp
        # omega = 4.6/(ts*zeta)

        # PI Gains
        if (self.zeta_flp == 0 or self.omega_flp == 0) or (not self.zeta_flp or not self.omega_flp):
            sys.exit('ERROR! --- Zeta and Omega flap must be nonzero for Flp_Mode >= 1 ---')

        self.Kp_flap = (2*self.zeta_flp*self.omega_flp - 2*zetaf*omegaf)/(self.kappa*omegaf**2)
        self.Ki_flap = (self.omega_flp**2 - omegaf**2)/(self.kappa*omegaf**2)
        self.Kp_flap = (2*self.zeta_flp*self.omega_flp - 2*zetaf*omegaf)/(self.kappa*omegaf**2)
        self.Ki_flap = (self.omega_flp**2 - omegaf**2)/(self.kappa*omegaf**2)

    def power_control(self, Cp, nR = 12):

        Cp_TSRopt = Cp.interp_surface(Cp.pitch_initial_rad, Cp.TSR_opt)
        Cp_opt      = max(Cp_TSRopt)

        Cp_inv      = interpolate.interp1d(Cp_TSRopt,Cp.pitch_initial_rad)
        
        # want to dedicate more to values close to 1 because that's where the controller will operate mostly
        # l parameter scales this
        l           = 2.5
        R           = 1/l * np.log10(np.linspace(0,10**l - 1,num=nR,endpoint=True)+1)
        beta_PC     = Cp_inv(R*Cp_opt)

        # append R > 1
        beta_PC     = np.append(beta_PC,beta_PC[-1])
        R           = np.append(R,2.0)

        return R, beta_PC

class SoftStart():
    '''
        Open loop soft start timeseries
        attributes:     tt - time indices of timeseries
                        R_ss - power rating at time indices
                        filename - open loop filename

        TODO: Eventually, make general open loop power class that this will inherit
    '''

    def __init__(self,controller,soft_start_params):
        
        # set default parameters
        if 'R_start' in soft_start_params:
            R_start = soft_start_params['R_start']
        else:
            R_start = 0.75  # default

        if 'T_fullP' in soft_start_params:
            T_fullP = soft_start_params['T_fullP']
        else:
            T_fullP = 60  # default

        if 'filename' in soft_start_params:
            filename = soft_start_params['filename']
        else:
            filename = 'soft_start.dat'  # default

        if hasattr(controller,'PwC_ConstPwr'):
            full_power = controller.PwC_ConstPwr
        else:
            full_power = 1.0


        # make timeseries
        self.tt         = np.linspace(0,T_fullP)
        self.R_ss       = sigma(self.tt,0,T_fullP,y0=R_start,y1=full_power)
        self.filename   = filename

class SoftCutOut():
    '''
    Open loop control for soft cut-out: power rating vs. slow LPF wind speed estimate

            attributes:     uu - wind speed breakpoints
                            R_scu - power rating at wind speed breakpoints 
                        filename - open loop filename

        note: could be generalized to any power rating vs. wind speed if desired in future
    '''
    def __init__(self,controller,soft_cut_params):
        
        # set default parameters
        if 'wind_speeds' in soft_cut_params:
            u_bp = soft_cut_params['wind_speeds']
        else:
            u_bp = [0.,50.]
            print('WARNING: Soft cut-out wind_speeds not set')

        if 'power_reference' in soft_cut_params:
            R_bp = soft_cut_params['power_reference']
        else:
            R_bp = [1.,1.]
            print('WARNING: Soft cut-out power_reference not set')

        if 'filename' in soft_cut_params:
            filename = soft_cut_params['filename']
        else:
            filename = 'soft_cut_out.dat'  # default

        # interpolate
        self.uu         = np.linspace(min(u_bp),max(u_bp),num=100)
        self.R_scu      = interpolate.pchip_interpolate(u_bp,R_bp,self.uu)
        self.filename   = filename
        
class ControllerBlocks():
    '''
    Class ControllerBlocks defines tuning parameters for additional controller features or "blocks"

    Methods:
    --------
    peak_shaving

    '''
    def __init__(self):
        pass
    
    def peak_shaving(self,controller, turbine):
        ''' 
        Define minimum blade pitch angle for peak shaving routine based on a maximum allowable thrust 

        Parameters:
        -----------
        controller: class
                    Controller class containing controller operational information
        turbine: class
                 Turbine class containing necessary wind turbine information for controller tuning
        '''

        # Re-define Turbine Parameters for shorthand
        J = turbine.J                           # Total rotor inertial (kg-m^2) 
        rho = turbine.rho                       # Air density (kg/m^3)
        R = turbine.rotor_radius                    # Rotor radius (m)
        A = np.pi*R**2                         # Rotor area (m^2)
        Ng = turbine.Ng                         # Gearbox ratio (-)
        rated_rotor_speed = turbine.rated_rotor_speed               # Rated rotor speed (rad/s)

        # Initialize some arrays
        Ct_op = np.empty(len(controller.TSR_op),dtype='float64')
        Ct_max = np.empty(len(controller.TSR_op),dtype='float64')
        beta_min = np.empty(len(controller.TSR_op),dtype='float64')
        # Find unshaved rotor thurst coefficients and associated rotor thrusts
        # for i in len(controller.TSR_op):
        for i in range(len(controller.TSR_op)):
            Ct_op[i] = turbine.Ct.interp_surface(controller.pitch_op[i],controller.TSR_op[i])
            T = 0.5 * rho * A * controller.v**2 * Ct_op

        # Define minimum max thrust and initialize pitch_min
        Tmax = controller.ps_percent * np.max(T)
        pitch_min = np.ones(len(controller.pitch_op)) * controller.min_pitch

        # Modify pitch_min if max thrust exceeds limits
        for i in range(len(controller.TSR_op)):
            # Find Ct values for operational TSR
            # Ct_tsr = turbine.Ct.interp_surface(turbine.pitch_initial_rad, controller.TSR_op[i])
            Ct_tsr = turbine.Ct.interp_surface(turbine.pitch_initial_rad,controller.TSR_op[i])
            # Define max Ct values
            Ct_max[i] = Tmax/(0.5 * rho * A * controller.v[i]**2)
            if T[i] > Tmax:
                Ct_op[i] = Ct_max[i]
            else:
                Ct_max[i] = np.minimum( np.max(Ct_tsr), Ct_max[i])
            # Define minimum pitch angle
            f_pitch_min = interpolate.interp1d(Ct_tsr, turbine.pitch_initial_rad, kind='cubic', bounds_error=False, fill_value=(turbine.pitch_initial_rad[0],turbine.pitch_initial_rad[-1]))
            pitch_min[i] = max(controller.min_pitch, f_pitch_min(Ct_max[i]))

        controller.ps_min_bld_pitch = pitch_min

        # save some outputs for analysis or future work
        self.Tshaved = 0.5 * rho * A * controller.v**2 * Ct_op
        self.pitch_min = pitch_min
        self.v = controller.v
        self.Ct_max = Ct_max
        self.Ct_op = Ct_op
        self.T = T

    def min_pitch_saturation(self, controller, turbine):
        
        # Find TSR associated with minimum rotor speed
        TSR_at_minspeed = (controller.pc_minspd/turbine.Ng) * turbine.rotor_radius / controller.v_below_rated
        for i in range(len(TSR_at_minspeed)):
            if TSR_at_minspeed[i] > controller.TSR_op[i]:
                controller.TSR_op[i] = TSR_at_minspeed[i]
        
                # Initialize some arrays
                Cp_op = np.empty(len(turbine.pitch_initial_rad),dtype='float64')
                min_pitch = np.empty(len(TSR_at_minspeed),dtype='float64')
                
        
                # Find Cp-maximizing minimum pitch schedule
                # Find Cp coefficients at below-rated tip speed ratios
                Cp_op = turbine.Cp.interp_surface(turbine.pitch_initial_rad,TSR_at_minspeed[i])
                Cp_max = max(Cp_op)
                f_pitch_min = interpolate.interp1d(Cp_op, turbine.pitch_initial_rad, bounds_error=False, fill_value=(turbine.pitch_initial_rad[0],turbine.pitch_initial_rad[-1]))
                min_pitch[i] = f_pitch_min(Cp_max)
                
                # modify existing minimum pitch schedule
                controller.ps_min_bld_pitch[i] = np.maximum(controller.ps_min_bld_pitch[i], min_pitch[i])
            else:
                return


class ControllerTypes():
    '''
    Class ControllerTypes used to define any types of controllers that can be tuned. 
        Generally, calculates gains based on some pre-defined tuning parameters. 

    Methods:
    --------
    second_order_PI
    '''
    def __init__(self):
        pass

    def second_order_PI(self,zeta,om_n,A,B,linearize=False,v=None):
        '''
        Define proportional integral gain schedule for a closed
            loop system with a standard second-order form.

        Parameters:
        -----------
        zeta : int (-)
               Desired damping ratio 
        om_n : int (rad/s)
               Desired natural frequency 
        A : array_like (1/s)
            Plant poles (state transition matrix)
        B : array_like (varies)
            Plant numerators (input matrix)
        linearize : bool, optional
                    If 'True', find a gain scheduled based on a linearized plant.
        v : array_like (m/s)
            Wind speeds for linearized plant model, if desired. 
        '''
        # Linearize system coefficients w.r.t. wind speed if desired
        if linearize:
            pA = np.polyfit(v,A,1)
            pB = np.polyfit(v,B,1)
            A = pA[0]*v + pA[1]
            B = pB[0]*v + pB[1]

        # Calculate gain schedule
        self.Kp = 1/B * (2*zeta*om_n + A)
        self.Ki = om_n**2/B           

class OpenLoopControl(object):
    '''
    attributes:
    - time: breakpoint of times
    - generator_torque: generator torque vs. time (optional)
    - blade_pitch: blade pitch angle vs. time (optional)

    '''

    def __init__(self,controller,ol_control_params):
        self.dt = 1/20
        self.max_time  = 200

        ol_timeseries = {}
        # common time input
        start_times = [ol_control_params[ol_input]['time'][0] for ol_input in ol_control_params if 'time' in ol_control_params[ol_input]]
        end_times   = [ol_control_params[ol_input]['time'][-1] for ol_input in ol_control_params if 'time' in ol_control_params[ol_input]]

        # are all the start/end times the same?
        all_same = lambda items : all(x == items[0] for x in items)
        if not all_same(start_times):
            print('WARNING: all start times are not the same, unexpected behavior may occur')

        if not all_same(end_times):
            print('WARNING: all end times are not the same, unexpected behavior may occur')        

        # Go from lowest start time to greatest end time
        ol_timeseries['time'] = np.arange(0,self.max_time,self.dt)
        
        for ol_key in ol_control_params:
            if ol_key != 'filename':
                ol_input = ol_control_params[ol_key]
                if 'time' in ol_input:
                    # append first value to 0s breakpoint
                    if ol_timeseries['time'][0] > 0:
                        ol_input['time'] = np.append(ol_input['time'],0)
                        ol_input['value'] = np.append(ol_input['value'],ol_input['value'][0])

                    # append last value to max_time breakpoint
                    if self.max_time > ol_timeseries['time'][-1]:
                        ol_input['time'] = np.append(ol_input['time'],self.max_time)
                        ol_input['value'] = np.append(ol_input['value'],ol_input['value'][-1])
                    
                    # set up interpolated timeseries
                    ol_timeseries[ol_key] = multi_sigma(ol_timeseries['time'],ol_input['time'],ol_input['value'])

                elif 'sine' in ol_input:
                    # set up sinusoidal timeseries
                    ol_timeseries[ol_key] = ol_input['sine']['amplitude'] * \
                                            np.sin( \
                                                2 * np.pi *  ol_timeseries['time'] / \
                                                ol_input['sine']['period'] \
                                                )

                else:
                    raise Exception(
                        'WARNING: no timeseries or sine input specified for for open loop control of {}. \
                        This is only index currently supported'.ol_input)

        # convert yaw angle to yaw rate
        if 'yaw_angle' in ol_timeseries:
            print('ROSCO Toolbox: converting yaw angle to yaw rate for DISCON.IN')
            ol_timeseries['yaw_rate'] = np.concatenate(([0],np.diff(ol_timeseries['yaw_angle'])))/self.dt

        # Save timeseries to OpenLoopControl object
        self.ol_timeseries  = ol_timeseries

    def plot_timeseries(self):
        '''
        Debugging script for showing open loop timeseries
        '''
        import matplotlib.pyplot as plt
        fig, ax = plt.subplots(len(self.ol_timeseries)-1,1)
        i_ax = -1
        for ol_input in self.ol_timeseries:
            if ol_input != 'time':
                i_ax += 1
                if len(ax) == 1:
                    ax.plot(self.ol_timeseries['time'],self.ol_timeseries[ol_input])
                    ax.set_ylabel(ol_input)
                else:
                    ax[i_ax].plot(self.ol_timeseries['time'],self.ol_timeseries[ol_input])
                    ax[i_ax].set_ylabel(ol_input)
        return fig, ax




# helper functions

def sigma(tt,t0,t1,y0=0,y1=1):
    ''' 
    generates timeseries for a smooth transition from y0 to y1 from x0 to x1

    inputs: tt - time indices
            t0 - start time
            t1 - end time
            y0 - start output
            y1 - end output

    outputs: yy - output timeseries corresponding to tt
    '''

    a3 = 2/(t0-t1)**3
    a2 = -3*(t0+t1)/(t0-t1)**3
    a1 = 6*t1*t0/(t0-t1)**3
    a0 = (t0-3*t1)*t0**2/(t0-t1)**3

    a = np.array([a3,a2,a1,a0])  

    T = np.vander(tt,N=4)       # vandermonde matrix

    ss = T @ a.T                # base sigma

    yy = (y1-y0) * ss + y0      # scale and offset

    return yy


def multi_sigma(tt,t_bp,y_bp):
    yy = np.empty([len(tt)])
    for i_sigma in range(0,len(t_bp)-1):
        ind_i       = (tt >= t_bp[i_sigma]) & (tt < t_bp[i_sigma+1])
        tt_i        = tt[ind_i]
        yy_i        = sigma(tt_i,t_bp[i_sigma],t_bp[i_sigma+1],y0=y_bp[i_sigma],y1=y_bp[i_sigma+1])
        yy[ind_i]   = yy_i

    if False:  # debug plot
        import matplotlib.pyplot as plt
        plt.plot(tt,yy)
        plt.show()
        print('here')

    return yy

