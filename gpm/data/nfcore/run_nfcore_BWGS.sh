################## test script ##################
# nextflow run nf-core/rnaseq -profile test,docker

################## ~/.nextflow/config ##################
# params {
#   config_profile_description = 'Nextgen3 IZKF'
#   config_profile_contact = 'Chao-Chung Kuo'
#   config_profile_url = 'http://genomics.rwth-aachen.de'
#   email = 'ckuo@ukaachen.de'
# }

################## ~/.nextflow/config ##################
# params {
#   config_profile_description = 'Nextgen3 IZKF'
#   config_profile_contact = 'Lin Gan'
#   config_profile_url = 'http://genomics.rwth-aachen.de'
#   email = 'lgan@ukaachen.de'
# }

#default
nextflow run nf-core/bacass -profile docker  --input samplesheet.csv --kraken2db "https://genome-idx.s3.amazonaws.com/kraken/k2_standard_8gb_20210517.tar.gz" -bg

#wo kraken
nextflow run nf-core/bacass -profile docker  --input samplesheet.csv  -bg --skip_kraken2

#
nextflow run nf-core/bacass -profile docker  --input samplesheet.csv --kraken2db "https://genome-idx.s3.amazonaws.com/kraken/k2_standard_8gb_20210517.tar.gz" --multiqc_title "Genomics_Facility_IZKF_Aachen_Sequencing_Quality_Report" -bg

# Options for --genome:
# gencode_hg38, gencode_mm10, hg38, mm10
# Useful options: --removeRiboRNA
