################## test script #########################
# nextflow run nf-core/rnaseq -profile test,docker

################## GPM samplesheet #####################
# gpm samplesheet -st 'forward' -sn true -si  samplesheet.csv FASTQ_DIR

nextflow run nf-core/rnaseq -r 3.8.1 -profile docker \
     --input samplesheet.csv --clip_r1 12 --outdir results \
     # --genome gencode_GRCh38 \
     # --genome gencode_GRCm39 \
     --gencode --featurecounts_group_type gene_type \
     --star_index false --save_reference \
     #--additional_fasta /data/genomes/spikein/ERCC_ExFold_RNA_SpikeIn_Mixes/ERCC92.fa  


# Options for --genome:
# gencode_GRCh38, gencode_GRCm39, hg38, mm10
# Useful options: 
# --removeRiboRNA
# 