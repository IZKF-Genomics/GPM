#!/bin/bash
# Usage:
# bash update_GENCODE_nfcore_rnaseq.sh FASTA_Genome FASTA_transcripts GTF FOLDER NAME

# Check if the required number of arguments is provided
if [ "$#" -lt 5 ]; then
    echo "This script will generate the indices needed for nfore/rnaseq pipeline and duplicate another set of files with ERCC Spike-ins."
    echo "Usage: bash $0 FASTA_Genome FASTA_transcripts GTF FOLDER NAME"
    echo "    FASTA_Genome: Define path to the genome FASTA file"
    echo "    FASTA_transcripts: Define path to the transcript FASTA file"
    echo "    GTF: Define path to the annotation GTF file"
    echo "    FOLDER: Define the target folder for storing the files with indices"
    echo "    NAME: Define the name for this genome assembly"
    exit 1
fi

Num_cores=30

# Accessing command-line arguments
FASTA_Genome=$1
FASTA_transcripts=$2
GTF=$3
FOLDER=$4
NAME=$5

ERCC_FASTA="/data/genomes/spikein/ERCC_ExFold_RNA_SpikeIn_Mixes/ERCC92.fa"
ERCC_GTF="/data/genomes/spikein/ERCC_ExFold_RNA_SpikeIn_Mixes/ERCC92.gtf"
log_file="${FOLDER}/output.log"

# Displaying the arguments
echo "FASTA genome:      $FASTA_Genome" 2>&1 | tee -a "$log_file"
echo "FASTA transcripts: $FASTA_transcripts" 2>&1 | tee -a "$log_file"
echo "GTF annotation: $GTF" 2>&1 | tee -a "$log_file"
echo "Target Folder:  $FOLDER" 2>&1 | tee -a "$log_file"
echo "Genome name:    $NAME" 2>&1 | tee -a "$log_file"

# Create a new folder
mkdir -p $FOLDER

# Run STAR index
STAR_INDEX="${FOLDER}/STAR_index"
STAR --runThreadN ${Num_cores} --runMode genomeGenerate --genomeDir $STAR_INDEX --genomeFastaFiles $FASTA_Genome 2>&1 | tee -a "$log_file"

# Run Salmon index
salmon_index="${FOLDER}/salmon_index"
salmon index -t ${FASTA_transcripts} -i $salmon_index --gencode -p ${Num_cores} 2>&1 | tee -a "$log_file"

# Combining ERCC sequences

# FASTA
cat $FASTA_Genome $ERCC_FASTA > ${FOLDER}/${NAME}_ERCC.fasta
cat $FASTA_transcripts $ERCC_FASTA > ${FOLDER}/${NAME}_ERCC_transcripts.fasta
# GTF
cat $GTF $ERCC_GTF > ${FOLDER}/${NAME}_ERCC.gtf
# Transcripts
gffread -w ${FOLDER}/${NAME}_ERCC_transcripts.gtf -g ${FOLDER}/${NAME}_ERCC.fasta ${FOLDER}/${NAME}_ERCC.gtf 2>&1 | tee -a "$log_file"
# Run STAR index
STAR --runThreadN ${Num_cores} --runMode genomeGenerate --genomeDir ${STAR_INDEX}_ERCC --genomeFastaFiles ${FOLDER}/${NAME}_ERCC.fasta 2>&1 | tee -a "$log_file"
# Run Salmon index
salmon index -t ${FOLDER}/${NAME}_ERCC_transcripts.fasta -i ${salmon_index}_ERCC --gencode -p ${Num_cores} 2>&1 | tee -a "$log_file"

# Export the config parameters for nextflow.config
echo "Please add the following codes into nextflow.config:" 2>&1 | tee -a "$log_file"
echo "'${NAME}' {
      fasta  = '${FASTA_Genome}'
      gtf = '${GTF}'
      transcript_fasta = '${FASTA_transcripts}'
      star = '${STAR_INDEX}'
      salmon = '${salmon_index}'
      gencode = true
    }" 2>&1 | tee -a "$log_file"

echo "'${NAME}_ERCC' {
      fasta  = '${FOLDER}/${NAME}_ERCC.fasta'
      gtf = '${FOLDER}/${NAME}_ERCC.gtf'
      transcript_fasta = '${FOLDER}/${NAME}_ERCC_transcripts.gtf'
      star = '${STAR_INDEX}_ERCC'
      salmon = '${salmon_index}_ERCC'
      gencode = true
    }" 2>&1 | tee -a "$log_file"