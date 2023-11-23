################## test script ##################
# nextflow run nf-core/clipseq -profile test, docker

nextflow run nf-core/clipseq -profile docker \
     --input samples.csv \
     --genome gencode_hg38 --smrna_org mouse \
     --peakcaller all --motif
