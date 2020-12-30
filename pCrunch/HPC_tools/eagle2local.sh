# ------ Sync DLC Data from eagle runs locally -------

# --- 5MW LAND LEGACY ---
# outdir='/scratch/dzalkind/WEIS-1/results/NASA/c_pitch/'
# indir='/Users/dzalkind/Tools/WEIS/results/NASA/c_pitch/'
# mkdir -p $indir;
# rsync -aP --no-g dzalkind@eagle.hpc.nrel.gov:$outdir $indir

outdir='/scratch/dzalkind/WEIS-1/results/NASA/'
indir='/Users/dzalkind/Tools/WEIS-1/results/NASA/'
mkdir -p $indir;
rsync -aP --no-g --include="*/" --include="*.yaml" --exclude="*" dzalkind@eagle.hpc.nrel.gov:$outdir $indir

# # --- 5MW LAND ROSCO ---
# outdir2='/projects/ssc/nabbas/DLC_Analysis/5MW_OC3Spar'
# indir2='../BatchOutputs/5MW_Land/5MW_Land_ROSCO/'
# mkdir -p $indir2;
# rsync nabbas@eagle.hpc.nrel.gov:$outdir2*.outb $indir2
# rsync nabbas@eagle.hpc.nrel.gov:$outdir2/case_matrix.yaml $indir2
