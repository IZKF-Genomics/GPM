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
     --genome gencode_hg38 \ 
     --multiqc_title TITLE_NAME

# Options for --genome:
# gencode_hg38, gencode_mm10, hg38, mm10
