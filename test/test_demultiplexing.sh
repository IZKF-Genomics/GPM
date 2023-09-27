# Configure the test folder and files
rm -r FASTQ* 220101*

# Demultiplexing
gpm demultiplex --raw BCLPath --output FASTQ
gpm demultiplex --raw BCLPath --output FASTQsc -sc True

# samplesheet
