################## test script ##################
# nextflow run nf-core/rnaseq -profile test,docker

################## GPM samplesheet #####################
# gpm samplesheet -st 'forward' samplesheet.csv FASTQ_DIR

nextflow run nf-core/smrnaseq -profile docker \
     --input samplesheet.csv \
     --genome gencode_hg38 --mirna_gtf /data/genomes/hg38/miRNA/hsa.gff3 --mature /data/genomes/hg38/miRNA/mature.fa.gz --hairpin /data/genomes/hg38/miRNA/hairpin.fa.gz

# Options for --genome:
# gencode_hg38, gencode_mm10, hg38, mm10
# --mirna_gtf /data/genomes/hg38/miRNA/hsa.gff3 --mature /data/genomes/hg38/miRNA/mature.fa.gz --hairpin /data/genomes/hg38/miRNA/hairpin.fa.gz