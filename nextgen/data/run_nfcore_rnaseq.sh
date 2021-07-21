# test script
# nextflow run nf-core/rnaseq -profile test,docker

nextflow run nf-core/rnaseq -bg \
     --input samplesheet.csv \
     --genome GRCh38 \ # Please define the genome ID: hg38, mm10
     --email ckuo@ukaachen.de \ # define in ~/.nextflow/config
     --multiqc_title "$(dirname $PWD | xargs basename)"
