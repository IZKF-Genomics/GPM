#!/bin/bash
APP="RNAseq tRNAseq mRNAseq 3mRNAseq"

# Exit on error
set -e

# Initiating a project
# APP="RNAseq"

formatted_date=$(date +%y%m%d)

for AP in $APP; do
    Project_name=${formatted_date}_Contact_PI_TEST_${AP}
    if [ -d "$Project_name" ]; then
        rm -r "$Project_name"  
    fi
    echo "#####################################"
    echo $AP
    gpm init -fq FASTQPath -n $Project_name
    cd $Project_name

    # nfcore
    cd nfcore/
    # rm nextflow.config
    # cp ../../RNAseq/nextflow.config .
    # nextflow run nf-core/rnaseq -r 3.12.0 -profile test,docker --outdir results #--quiet
    # lowercase_AP=$(echo "$AP" | tr '[:upper:]' '[:lower:]')
    # bash run_nfcore_${lowercase_AP}.sh
    cp -r ../../RNAseq/results .
    cd ../

    gpm analysis config.ini
    gpm analysis config.ini --add DGEA_RNAseq
    cp -f ../RNAseq/samplesheet_RNAseq.csv ./analysis/DGEA/samplesheet.csv
    # mkdir -p nfcore/results/pipeline_info/
    # cp ../RNAseq/software_versions.yml ./nfcore/results/pipeline_info/software_versions.yml
    # gpm analysis config.ini --list
    
    cd analysis
    Rscript -e "rmarkdown::render('Analysis_Report_RNAseq.Rmd')"
    # gpm export export_folder -config config.ini -user auser -bcl BCLPath -fastq FASTQPath
    cd ../..
done
# Run nf-core pipeline

# Create analysis reports

# Export data

#