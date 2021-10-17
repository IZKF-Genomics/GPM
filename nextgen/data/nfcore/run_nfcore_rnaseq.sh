################## test script ##################
# nextflow run nf-core/rnaseq -profile test,docker

################## ~/.nextflow/config ##################
# params {
#   config_profile_description = 'Nextgen3 IZKF'
#   config_profile_contact = 'Chao-Chung Kuo'
#   config_profile_url = 'http://genomics.rwth-aachen.de'
#   email = 'ckuo@ukaachen.de'
# }

nextflow run nf-core/rnaseq -profile docker \
     --pseudo_aligner salmon \
     --input samplesheet.csv \
     --genome gencode_hg38 # Please define the genome ID: hg38, mm10
     --multiqc_title YYMMDD...\

