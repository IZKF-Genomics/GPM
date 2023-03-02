#!/bin/bash

# this script will run the scVDJ analysis
# make sure cellranger is available in your environment
# otherwise scource shared enviroment from /data/shared_env/shared_paths.sh
# this script can be run directly from shell

# set directory
Multi_Output="./multi_out"

mkdir -p $Multi_Output

#sample 132

Conf="/data/projects/220504_Simons_Pabst_MolMedizin_scVDJseq/analysis/multi_config_220504.csv"
sampleid=132
cd $outDir
cellranger multi --id=$sampleid \
--csv=$Conf \
--localcores=8 \
--localmem=64

#sample 133
Conf="/data/projects/220504_Simons_Pabst_MolMedizin_scVDJseq/analysis/multi_config_220504_1.csv"
sampleid=133
cd $outDir
cellranger multi --id=$sampleid \
--csv=$Conf \
--localcores=8 \
--localmem=64