# Please make sure bcl2fastq V.2 is available in your environment
# You should review the paramenters and run:
# screen -S bcl2fastq
# bash run_idemux.sh

# Please execute these commands in the directory OUTPUT_DIR

# Demultiplexing with bcl2fastq to generated reads pool:
bcl2fastq -R FLOWCELL_DIR -o FASTQ_DIR -l WARNING --no-lane-splitting --sample-sheet blank_sample.csv --barcode-mismatches 0 --mask-short-adapter-reads 10

# use iDemux for demultiplexing with error correction
idemuxCPP --r1 FASTQ_DIR/Undetermined_S0_R1_001.fastq.gz  --sample-sheet samplesheet_idemux.csv --out ./demux

###### Running FASTQC ######################################
mkdir -p ./fastqc
find * -maxdepth 1 -name "*.fastq.gz" | parallel -j 30 "fastqc {} -o ./fastqc"

###### Running MultiQC #####################################
mkdir -p multiqc
multiqc -f . -o ./multiqc