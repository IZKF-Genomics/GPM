################## test script #########################
# nextflow run nf-core/rnaseq -profile test,docker

################## GPM samplesheet #####################
# gpm samplesheet -st 'forward' samplesheet.csv FASTQ_DIR

nextflow run nf-core/rnaseq -r 3.8.1 -profile docker \
     --input samplesheet.csv --clip_r1 12 --outdir results \
     --genome gencode_hg38 --gencode --featurecounts_group_type gene_type \
     # --rseqc_modules 'bam_stat,inner_distance,infer_experiment,junction_annotation,junction_saturation,read_distribution,read_duplication' \
     --additional_fasta /data/genomes/spikein/ERCC_ExFold_RNA_SpikeIn_Mixes/ERCC92.fa --star_index false --save_reference 


# Options for --genome:
# gencode_hg38, gencode_mm10, hg38, mm10
# Useful options: 
# --removeRiboRNA
# 