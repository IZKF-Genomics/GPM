# Please make sure cellranger-7.1.0 is available in your environment
# You should review the paramenters and run:
# screen -S cellranger
# bash run_cellranger.sh

# Please execute this command in the directory OUTPUT_DIR
cellranger mkfastq --id=mkfastq --localcores=30 \
                   --run=FLOWCELL_DIR \
                   --csv=./samplesheet.csv

# Below script can be used to run cellranger count by modifying sample names and adding project name.