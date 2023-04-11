# You should review the paramenters and run:
# screen -S bcl2fastq
# bash run_qc.sh

# Please execute this command in the directory OUTPUT_DIR

###### Running FASTQC ######################################
mkdir -p ./fastqc
find FASTQ_DIR -maxdepth 1 -name "*.fastq.gz" | parallel -j 30 "fastqc {} -o ./fastqc"

###### Running MultiQC #####################################
mkdir -p multiqc
multiqc -f . -o ./multiqc