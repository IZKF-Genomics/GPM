# Configure the test folder and files
rm -r FASTQ* 220101*

# Demultiplexing
gpm demultiplex --raw BCLPath --output FASTQ
gpm demultiplex --raw BCLPath --output FASTQsc -sc True

# Initiating a project
# APP="RNAseq"
APP="RNAseq tRNAseq mRNAseq 3mRNAseq ChIPseq ATACseq ampliseq scRNAseq miRNAseq BWGS WES fastq"
for AP in $APP; do
echo $AP
gpm init -fq FASTQPath -n 220101_Contact_PI_UKA_${AP}
cd 220101_Contact_PI_UKA_${AP}
gpm analysis config.ini
gpm export export_folder -config config.ini -user auser -bcl BCLPath -fastq FASTQPath
cd ..
done
# Run nf-core pipeline

# Create analysis reports

# Export data

#