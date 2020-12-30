# ------ Sync DLC Data from eagle runs locally -------


# --- Steps ---
outdir='/scratch/dzalkind/WEIS-3/results/CT-barge/DISCON-CT-barge_90/simp+pc_mode/'
indir='/Users/dzalkind/Tools/WEIS-3/results/CT-barge/DISCON-CT-barge_90/simp+pc_mode/'
mkdir -p $indir;
rsync -aP --no-g --include="*/" --include="step_10.*" --exclude="*" dzalkind@eagle.hpc.nrel.gov:$outdir $indir
rsync -aP --no-g --include="*/" --include="step_14.*" --exclude="*" dzalkind@eagle.hpc.nrel.gov:$outdir $indir


# --- NTM ---
# outdir='/scratch/dzalkind/WEIS-3/results/CT-barge/'
# indir='/Users/dzalkind/Tools/WEIS-3/results/CT-barge/'
# mkdir -p $indir;
# rsync -aP --no-g --include="*/" --include="iea15mw_62.*" --exclude="*" dzalkind@eagle.hpc.nrel.gov:$outdir $indir


# rsync -aP --no-g --include="*/" --include="step_14.*" --exclude="*" dzalkind@eagle.hpc.nrel.gov:$outdir $indir
# rsync -aP --no-g --include="*/" --include="iea15mw_26.*" --exclude="*" dzalkind@eagle.hpc.nrel.gov:$outdir $indir

# rsync dzalkind@eagle.hpc.nrel.gov:$outdir/case_matrix.yaml $indir

# # --- 5MW LAND ROSCO ---
# outdir2='/projects/ssc/nabbas/DLC_Analysis/5MW_OC3Spar'
# indir2='../BatchOutputs/5MW_Land/5MW_Land_ROSCO/'
# mkdir -p $indir2;
# rsync nabbas@eagle.hpc.nrel.gov:$outdir2*.outb $indir2
# rsync nabbas@eagle.hpc.nrel.gov:$outdir2/case_matrix.yaml $indir2
