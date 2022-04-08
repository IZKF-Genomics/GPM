#!/bin/bash -l


#define parameters

fastq=/data/fastq/220211_NB501289_0587_AHK5WLAFX3/HK5WLAFX3
refdata=/data/shared_env/10xGenomics/refdata-gex-GRCh38-2020-A


outDir=/data/projects/220211_Kalmer_Koschmieder_MedIV_scRNAseq/count


#echo $fastq
#echo $refdata
#echo $outDir

mkdir -p $outDir
cd $outDir

for sampleid in `ls $fastq`
do
	sample=$sampleid
#echo $sample
#echo $sampleid

	cellranger count --id=$sampleid \
                 --transcriptome=$refdata \
                 --fastqs=$fastq \
                 --sample=$sample \
                 --localcores=15 \
                 --localmem=100

done
