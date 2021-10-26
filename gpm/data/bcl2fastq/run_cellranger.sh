# Please make sure cellranger-6.1.1 is available in your environment
# You should review the paramenters and run:
# screen -S cellranger
# bash run_cellranger.sh

# Please execute this command in the directory OUTPUT_DIR
cellranger mkfastq --id=mkfastq \
                   --run=FLOWCELL_DIR \
                   --csv=./samplesheet.csv

# Below script can be used to run cellranger count by modifying sample names and adding project name.
# 
# TRANSCRIPTOME="/data/shared_env/10xGenomics/refdata-gex-GRCh38-2020-A"
# SAMPLES=""
# for sample in $SAMPLES; do
# cellranger count --id=count --transcriptome $TRANSCRIPTOME --fastqs mkfastq/outs/fastq_path/PROJECT_NAME/$sample --sample=$sample
# done

