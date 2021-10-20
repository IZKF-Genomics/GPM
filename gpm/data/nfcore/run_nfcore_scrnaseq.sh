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
    --reads '*_R{1,2}.fastq.gz' \
    --fasta human.fasta \
    --gtf human.gtf \
    --type '10x' \
    --chemistry 'V3'
    --genome gencode_hg38 # Please define the genome ID: hg38, mm10
    --multiqc_title YYMMDD...\

