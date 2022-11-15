# Please make sure bcl2fastq V.2 is available in your environment
# You should review the paramenters and run:
# screen -S bcl2fastq
# bash run_bcl2fastq.sh

# Please execute this command in the directory OUTPUT_DIR
bcl2fastq \
  --no-lane-splitting \
  --runfolder-dir FLOWCELL_DIR \
  --output-dir . \
  --interop-dir ./InterOp/ \
  --sample-sheet ./samplesheet.csv \
  --processing-threads 30


  # --use-bases-mask=Y,I8,I8,Y
  # --create-fastq-for-index-reads \
  # --minimum-trimmed-read-length=8 \
  # --mask-short-adapter-reads=8 \
  # --ignore-missing-positions \
  # --ignore-missing-controls \
  # --ignore-missing-filter \
  # --ignore-missing-bcls \
  # --loading-threads 2 \
  # --writing-threads 2 \
  # Other amazing parameter

###### Running FASTQC ######################################
mkdir -p ./fastqc
find * -maxdepth 1 -name "*.fastq.gz" | parallel -j 30 "fastqc {} -o ./fastqc"

###### Running MultiQC #####################################
mkdir -p multiqc
multiqc -f . -o ./multiqc

###### UMItools for Qiaseq miRNAseq Kit #####################################
# umitool_miRNAseq () {
#   echo $1
#   filename=$(basename -- $1)
#   echo $filename
#   TRIMMED_FASTQ="./UMI_trimmed/${filename}"
#   echo $TRIMMED_FASTQ
#   umi_tools extract --stdin=$1 --stdout=${TRIMMED_FASTQ} --extract-method=regex --bc-pattern='.+AACTGTAGGCACCATCAAT{s<=2}(?P<umi_1>.{12})(?P<discard_2>.*)'
# }

# export -f umitool_miRNAseq
# mkdir -p UMI_trimmed
# parallel umitool_miRNAseq ::: $samples

###### UMItools for trimming reads #####################################

# samples="22_N1291_DNA_UP09_S9"
# umitool_trim_paired () {
#   filename=$(basename -- $1)
#   echo $filename
#   TRIMMED_FASTQ="./UMI_trimmed/${filename}"
#   R1=${1}_R1_001.fastq.gz
#   R2=${1}_R2_001.fastq.gz
#   TR1="./UMI_trimmed/${1}_R1_trimmed.fastq.gz"
#   TR2="./UMI_trimmed/${1}_R2_trimmed.fastq.gz"
#   umi_tools extract --stdin=$R1 --read2-in=$R2 --stdout=$TR1 --read2-out $TR2 \
#   --extract-method=string --bc-pattern=NNNNNNN --bc-pattern2=NNNNNNN
# }

# export -f umitool_trim_paired
# mkdir -p UMI_trimmed
# parallel umitool_trim_paired ::: $samples