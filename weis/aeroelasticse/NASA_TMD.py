'''NASA project TMD


'''
import numpy as np
import os


class NASA_TMD(object):

    def __init__(self):
        # set default params
        self.num_dampers = 4

        # parameters
        self.tank_radial_cog     = 41
        self.tank_vertical_cog   = -1.3
        self.mass_per_tank       = 856640
        self.damper_freq         = 0.9 # rad/s
        self.damping_ratio       = 0.05


        # geometry
        self.x           = [41,-41,0,0]
        self.y           = [0,0,41,-41]
        self.z           = [self.tank_vertical_cog] * self.num_dampers
        self.r1          = [0,0,0,0]
        self.r2          = [1.571,1.571,1.571,1.571]
        self.r3          = [0,0,0,0]

        # TMD properties
        self.update_tmd_props()


        # Default TMD Control (lookup table: w_n vs. Tp)
        self.omega_control = [0,11.7,12.7,20]
        self.period_control = [1.36,1.1,0.5,.34]        




    def update_tmd_props(self):
        # TMD properties
        self.m           = [self.mass_per_tank] * self.num_dampers
        self.stiffness   = [self.damper_freq*self.damper_freq * self.mass_per_tank] * self.num_dampers
        self.damping     = (2 * self.damping_ratio * np.sqrt(np.array(self.stiffness) * np.array(self.m))).tolist()

    def write_tmd_input(self,filename):
        if not os.path.isdir(os.path.dirname(filename)):
            os.makedirs(os.path.dirname(filename))

        with open(filename,mode='w') as f:
            f.write('Num. of Dampers\n')
            f.write('{}\n'.format(self.num_dampers))
            f.write('Mass (kg)	 Stiffnesss (N/m)	 Linear Damping (N/(m/s))	 Nonlinear Damping (N/(m/s)^2)	 X (m)	 Y (m)	 Z (m)	 r1 (rad)	 r2 (rad)	 r3 (rad)\n')
            for iDamp in range(self.num_dampers):
                f.write('{}\t{:10.1f}\t{:10.1f}\t{}\t{}\t{}\t{}\t{}\t{}\t{}\t\n'.format(self.m[iDamp],self.stiffness[iDamp],self.damping[iDamp],0,self.x[iDamp],\
                    self.y[iDamp],self.z[iDamp],self.r1[iDamp],self.r2[iDamp],self.r3[iDamp]))
            f.close()


    def write_tmd_control(self,filename):
        
        with open(filename,mode='w') as f:
            f.write('! Period\tNatural Freq.\n')
            f.write('! (sec.)\t(rad/s)\n')

            for bp,co in zip(self.omega_control,self.period_control):
                f.write('{:.3f}\t\t{:.3f}\n'.format(bp,co))



if __name__ == '__main__':  # testing script

    nt = NASA_TMD()

    nt.write_tmd_input('/Users/dzalkind/Tools/WEIS/weis/aeroelasticse/test_tmd_input_def.dat')

    nt.damper_freq = 0.3
    nt.update_tmd_props()
    nt.write_tmd_input('/Users/dzalkind/Tools/WEIS/weis/aeroelasticse/test_tmd_input_0d3.dat')
    nt.period_control = [0]
    nt.omega_control  = [1]

    nt.mass_per_tank  = 0
    nt.update_tmd_props()
    
    nt.write_tmd_control('/Users/dzalkind/Tools/WEIS/weis/aeroelasticse/test_tmd_control.dat')
    nt.write_tmd_input('/Users/dzalkind/Tools/WEIS/weis/aeroelasticse/test_tmd_no_mass.dat')

    print('here')

