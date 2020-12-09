# ------ Sync DLC Data from eagle runs locally -------

# --- 5MW LAND LEGACY ---
outdir='/scratch/dzalkind/WEIS-3/results/CT-spar/DISCON_CT-spar_lowBW/steps/'
indir='/Users/dzalkind/Tools/WEIS-3/results/CT-spar/DISCON_CT-spar_lowBW/steps/'
mkdir -p $indir;
rsync -aP --no-g dzalkind@eagle.hpc.nrel.gov:$outdir $indir
# rsync dzalkind@eagle.hpc.nrel.gov:$outdir/case_matrix.yaml $indir

# # --- 5MW LAND ROSCO ---
# outdir2='/projects/ssc/nabbas/DLC_Analysis/5MW_OC3Spar'
# indir2='../BatchOutputs/5MW_Land/5MW_Land_ROSCO/'
# mkdir -p $indir2;
# rsync nabbas@eagle.hpc.nrel.gov:$outdir2*.outb $indir2
# rsync nabbas@eagle.hpc.nrel.gov:$outdir2/case_matrix.yaml $indir2
