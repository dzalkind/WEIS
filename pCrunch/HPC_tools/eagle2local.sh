# ------ Sync DLC Data from eagle runs locally -------

# --- 5MW LAND LEGACY ---
# outdir='/scratch/dzalkind/WEIS-3/results/'
# indir='/Users/dzalkind/Tools/WEIS-3/results/'
# mkdir -p $indir;
# rsync -aP --no-g --include="*/" --include="*.yaml" --exclude="*" dzalkind@eagle.hpc.nrel.gov:$outdir $indir
# # rsync dzalkind@eagle.hpc.nrel.gov:$outdir/case_matrix.yaml $indir

outdir='/scratch/dzalkind/WEIS-3/results/'
indir='/Users/dzalkind/Tools/WEIS-3/results/'
mkdir -p $indir;
# rsync -aP --no-g dzalkind@eagle.hpc.nrel.gov:$outdir $indir
rsync -aP --no-g --include="*/" --include="*.yaml" --exclude="*" dzalkind@eagle.hpc.nrel.gov:$outdir $indir


# outdir='/scratch/dzalkind/WEIS-3/results/CT-spar/DISCON-CT-spar_90/simp+pc_mode/'
# indir='/Users/dzalkind/Tools/WEIS-3/results/CT-spar/DISCON-CT-spar_90/simp+pc_mode/'
# mkdir -p $indir;
# rsync -aP --no-g dzalkind@eagle.hpc.nrel.gov:$outdir $indir

# outdir='/scratch/dzalkind/WEIS-3/results/CT-semi/DISCON-CT-semi_90/simp+pc_mode/'
# indir='/Users/dzalkind/Tools/WEIS-3/results/CT-semi/DISCON-CT-semi_90/simp+pc_mode/'
# mkdir -p $indir;
# rsync -aP --no-g dzalkind@eagle.hpc.nrel.gov:$outdir $indir

# outdir='/scratch/dzalkind/WEIS-3/results/CT-barge/DISCON-CT-barge_90/simp+pc_mode/'
# indir='/Users/dzalkind/Tools/WEIS-3/results/CT-barge/DISCON-CT-barge_90/simp+pc_mode/'
# mkdir -p $indir;
# rsync -aP --no-g dzalkind@eagle.hpc.nrel.gov:$outdir $indir

# outdir='/scratch/dzalkind/WEIS-3/results/CT-TLP/DISCON-CT-TLP_90/simp+pc_mode/'
# indir='/Users/dzalkind/Tools/WEIS-3/results/CT-TLP/DISCON-CT-TLP_90/simp+pc_mode/'
# mkdir -p $indir;
# rsync -aP --no-g dzalkind@eagle.hpc.nrel.gov:$outdir $indir

# rsync -aP --no-g --include="*/" --include="*.yaml" --exclude="*" dzalkind@eagle.hpc.nrel.gov:$outdir $indir

# /scratch/dzalkind/WEIS-3/results/CT-barge/DISCON-CT-barge/ntm

# # --- 5MW LAND ROSCO ---
# outdir2='/projects/ssc/nabbas/DLC_Analysis/5MW_OC3Spar'
# indir2='../BatchOutputs/5MW_Land/5MW_Land_ROSCO/'
# mkdir -p $indir2;
# rsync nabbas@eagle.hpc.nrel.gov:$outdir2*.outb $indir2
# rsync nabbas@eagle.hpc.nrel.gov:$outdir2/case_matrix.yaml $indir2
