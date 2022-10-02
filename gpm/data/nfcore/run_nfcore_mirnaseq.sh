################## test script ##################
# nextflow run nf-core/rnaseq -profile test,docker

################## GPM samplesheet #####################
# gpm samplesheet -st 'forward' samplesheet.csv FASTQ_DIR

nextflow run nf-core/smrnaseq -r 2.0.0 -profile docker \
     --input samplesheet.csv --outdir results --mirtrace_species hsa --mirtrace_protocol qiaseq \
     --three_prime_adapter AACTGTAGGCACCATCAAT --protocol qiaseq \
     --genome GRCh38 \
     --mirna_gtf /data/genomes/hg38/miRNA/hsa.gff3 \
     --mature /data/genomes/spikein/QIASeq_miRNAseq_SpikeIn/mature_with_qiaseq_spikein.fa \
     --hairpin /data/genomes/spikein/QIASeq_miRNAseq_SpikeIn/hairpin_with_qiaseq_spikein.fa
     
# Options for --genome:
# gencode_hg38, gencode_mm10, hg38, mm10
# --mirna_gtf /data/genomes/hg38/miRNA/hsa.gff3 --mature /data/genomes/hg38/miRNA/mature.fa.gz --hairpin /data/genomes/hg38/miRNA/hairpin.fa.gz