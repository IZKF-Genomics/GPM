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