################## test script ##################
# nextflow run nf-core/rnaseq -profile test,docker

nextflow run nf-core/ampliseq  -profile docker \
    --input samplesheet.csv \
    --metadata metadata.tsv \
    --FW_primer "GTGYCAGCMGCCGCGGTAA" \ 
    --RV_primer "GGACTACNVGGGTWTCTAAT" \
    --outdir ./results
