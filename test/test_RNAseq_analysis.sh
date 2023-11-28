#!/bin/bash
APP="RNAseq tRNAseq mRNAseq 3mRNAseq"

# Exit on error
set -e

# Initiating a project
# APP="RNAseq"

formatted_date=$(date +%y%m%d)

for AP in $APP; do
    
    # rm -r *_Contact_PI_TEST_${AP}
    echo "#####################################"
    echo $AP
    gpm init -fq FASTQPath -n ${formatted_date}_Contact_PI_TEST_${AP}
    cd ${formatted_date}_Contact_PI_TEST_${AP}

    gpm analysis config.ini
    gpm analysis config.ini --list
    gpm analysis config.ini --add DGEA_RNAseq

# gpm export export_folder -config config.ini -user auser -bcl BCLPath -fastq FASTQPath
cd ..
done
# Run nf-core pipeline

# Create analysis reports

# Export data

#