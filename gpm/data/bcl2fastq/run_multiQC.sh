#!/bin/bash

FastIn="/data/fastq/220211_NB501289_0587_AHK5WLAFX3/merged_fastq"

Fastqc="/data/fastq/220211_NB501289_0587_AHK5WLAFX3/QC/fastqc"
Multiqc="/data/fastq/220211_NB501289_0587_AHK5WLAFX3/QC/Multiqc"



mkdir -p $Fastqc

#run fastqc  on the merged fastqs

#fastqc -o $Fastqc "$FastIn"/*.fastq.gz

#run multiqc on the fastqc result

mkdir -p $Multiqc

multiqc --title "Genomics Facility IZKF Aachen sequencing quality report" -o $Multiqc $Fastqc


