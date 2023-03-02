#!/bin/bash

# this script will run the scVDJ analysis
# make sure cellranger is available in your environment
# otherwise scource shared enviroment from /data/shared_env/shared_paths.sh
# this script can be run directly from shell

Local_Cores=30

Sample_ID="sample_1"
# Sample_ID="sample_1 sample_2"

for sample in ${Sample_ID}; do
  Config_File="./multi_config_${sample}.csv"
  cellranger multi --id=$sample --csv=$Config_File --localcores=$Local_Cores
done