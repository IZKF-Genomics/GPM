#!/bin/bash

FastIn="/data/fastq/220211_NB501289_0587_AHK5WLAFX3/HK5WLAFX3"
FastOut="/data/fastq/220211_NB501289_0587_AHK5WLAFX3/merged_fastq"

mkdir -p $FastOut

for sample in `ls $FastIn`
do

	for i in $(find "$FastIn"/"$sample" -type f -name "*.fastq.gz" | while read F; do basename $F | rev | cut -c 22- | rev; done | sort | uniq)

    		do echo "$i"
        	echo "Merging R1"
        

        	cat "$FastIn"/"$sample"/"$i"_L00*_R1_001.fastq.gz > "$FastOut"/"$i"_ME_R1_001.fastq.gz

#       echo "$FastIn"/"$sample"/"$i"_L00*_R1_001.fastq.gz
       		echo "Merging R2"

        	cat "$FastIn"/"$sample"/"$i"_L00*_R2_001.fastq.gz > "$FastOut"/"$i"_ME_R2_001.fastq.gz


        	echo "Merging I1"

        	cat "$FastIn"/"$sample"/"$i"_L00*_I1_001.fastq.gz > "$FastOut"/"$i"_ME_I1_001.fastq.gz



	done;

done;

#run multiQC on the merged fastqs


