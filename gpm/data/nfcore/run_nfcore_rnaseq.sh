################## test script ##################
# nextflow run nf-core/rnaseq -profile test,docker

################## ~/.nextflow/config ##################
# params {
#   config_profile_description = 'Nextgen3 IZKF'
#   config_profile_contact = 'Chao-Chung Kuo'
#   config_profile_url = 'http://genomics.rwth-aachen.de'
#   email = 'ckuo@ukaachen.de'
# }

nextflow run nf-core/rnaseq -r 3.5 -profile docker \
     --pseudo_aligner salmon \
     --input samplesheet.csv \
     --genome gencode_hg38 --gencode --featurecounts_group_type gene_type \ 
     --multiqc_title GPM_TITLE_NAME \
     --rseqc_modules 'bam_stat,inner_distance,infer_experiment,junction_annotation,junction_saturation,read_distribution,read_duplication'


# Options for --genome:
# gencode_hg38, gencode_mm10, hg38, mm10
# Useful options: --removeRiboRNA
