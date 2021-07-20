# test script
# nextflow run nf-core/rnaseq -profile test,docker

nextflow run nf-core/rnaseq \
     --input samplesheet.csv \
     --genome  # Please define the genome ID: hg38, mm10