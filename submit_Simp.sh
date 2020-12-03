#!/bin/bash
#SBATCH --account=fwky
#SBATCH --time=1:00:00
#SBATCH --job-name=SimpSweep
#SBATCH --nodes=1             # This should be nC/36 (36 cores on eagle)
#SBATCH --ntasks-per-node=36
#SBATCH --mail-user dzalkind@nrel.gov
#SBATCH --mail-type BEGIN,END,FAIL
#SBATCH --output=/scratch/dzalkind/job_SimpSweep.%j.out

#SBATCH --partition=debug

# Init_batch-env.sh:
source deactivate
module purge
module use /nopt/nrel/ecom/hpacf/compilers/modules
module use /nopt/nrel/ecom/hpacf/utilities/modules/
module use /nopt/nrel/ecom/hpacf/software/modules/intel-18.0.4/
module load mkl/2019.1.144 cmake/3.12.3
module load gcc/7.4.0 intel-parallel-studio/cluster.2018.4
conda activate weis-env3


python /scratch/dzalkind/WEIS-3/examples/aeroelasticse/run_Simp.py
