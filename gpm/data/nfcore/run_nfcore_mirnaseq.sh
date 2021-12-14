################## test script ##################
# nextflow run nf-core/rnaseq -profile test,docker

################## ~/.nextflow/config ##################
# params {
#   config_profile_description = 'Nextgen3 IZKF'
#   config_profile_contact = 'Chao-Chung Kuo'
#   config_profile_url = 'http://genomics.rwth-aachen.de'
#   email = 'ckuo@ukaachen.de'
# }

nextflow run nf-core/smrnaseq -profile docker \
     --input '*.fastq.gz' \
     --genome GRCh38

# Options for --genome:
# gencode_hg38, gencode_mm10, hg38, mm10