# GPM (Genomic Project Manager)
This command line tool is designed to simplifiy and automatize the bioinformatic workflow. The main tasks include:
- Demultiplexing
- nf-core pipeline
- Basic analysis report in Rmd for various applications
- Exporting data to a web server
- Clean temporary files
- Archive the crucial files for regenerating data in the future

## Target users

Bioinformaticians who manage various projects and analyses with a standard practice.

## Installation

The script below will install GPM and save the configuration files under ~/GPMDATA/. If you want to save the configuration files in a shared directory with others, please define GPMDATA variable in the environment.
```
# GPMDATA="YOUR_DEFINED_PATH"
git clone https://github.com/IZKF-Genomics/GPM.git
cd GPM
pip install .
gpm --help
```

## Demuliplexing

### Bulk sequencing applications:

```
gpm demultiplex --raw PATH_TO_BCL --output OUTPUT_DIR
```
This command will prepare two files for you:
- samplesheet.csv
- run_bcl2fastq.sh

You will have to modify samplesheet.csv with your sample information and indeces, then run run_bcl2fastq.sh by the following command:
```
screen -S fastq
bash run_bcl2fastq.sh
```

### Single-cell applications:
```
gpm demultiplex --raw PATH_TO_BCL --output OUTPUT_DIR -sc
```
This command will prepare two files for you:
- samplesheet.csv
- run_cellranger.sh

