################## test script ##################
# nextflow run nf-core/scrnaseq -profile test,docker

################## ~/.nextflow/config ##################
# params {
#   config_profile_description = 'Nextgen3 IZKF'
#   config_profile_contact = 'Chao-Chung Kuo'
#   config_profile_url = 'http://genomics.rwth-aachen.de'
#   email = 'ckuo@ukaachen.de'
# }

nextflow run nf-core/scrnaseq -profile docker \
    --reads 'FASTQ_DIR/*/*_R{1,2}_*.fastq.gz' \
    --type '10x' \
    --chemistry 'V3'
    --genome gencode_hg38 # Please define the genome ID: hg38, mm10
    --multiqc_title TITLE_NAME
