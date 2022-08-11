################## test script ##################
# nextflow run nf-core/rnaseq -profile test,docker

################## ~/.nextflow/config ##################
# params {
#   config_profile_description = 'Nextgen3 IZKF'
#   config_profile_contact = 'Chao-Chung Kuo'
#   config_profile_url = 'http://genomics.rwth-aachen.de'
#   email = 'ckuo@ukaachen.de'
# }


nextflow run nf-core/ampliseq -profile docker \
    --input samplesheet.csv \
    --FW_primer GTCTCGTGGGCTCGGAGATGTGTATAAGAGACAGcgtgacgtagaaagtaataa \
    --RV_primer TCGTCGGCAGCGTCAGATGTGTATAAGAGACAGgactagccttattttaacttgct \
    --metadata metadata.tsv
    --outdir ./results
