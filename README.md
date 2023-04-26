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
# export GPMDATA=/data/gpmdata
git clone https://github.com/IZKF-Genomics/GPM.git
cd GPM
pip install .
gpm --help
```

## Demuliplexing

### Bulk sequencing applications:

```
gpm demultiplex --raw PATH_TO_BCL --output OUTPUT_DIR --name YYMMDD_Name1_Name2_Institute_App
```
This command will prepare two files for you:
- samplesheet.csv
- run_bcl2fastq.sh
- config.ini: (only in case name is specied) All the initial information required for fastq/bcl export.
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

## Initialize a project

```
gpm init --fastq PATH_TO_FASTQs --name YYMMDD_Name1_Name2_Institute_App
```

The name of the project folder is strictly controlled:
- YYMMDD: The date must be a valid date.
- Name1: The surname of the contact person.
- Name2: The surname of the PI or the group name.
- Institute: The name of the department or company.
- App: The application defined in the gpm.config file.

This command will generate the folders and prepare the scripts:
- config.ini: All the initial information for this project.
- data: An empty folder for any future usage such as adding external data.
- nfcore: script and templates for running nfcore pipeline for this App.
- analysis: An empty folder for further analysis.

## Running nf-core pipeline

There are 3 files under nfcore folder:
- nextflow.config: A user-defined config file for nf-core
- samplesheet.csv: A sample sheet according to nfcore pipeline.
- run_nfcore_APP.sh: An application-specific script for running nf-core (recommend to run it in screen session).

Running nfcore script will generate 2 folders under nfcore:
- result: all output files from nfcore pipeline
- work: intermediate files which can be cleaned later.

## Analysis

After the data is processed, we can use the Rmd template for the downstream analysis by:
```
gpm analysis config.ini
```

This command will generate several Rmd files under analsis folder with all the parameters are properly defined according to the project information. Eventually, Analysis_Report_APP.html could be the landing page for the clients where they can download the data, browse the results and read the analysis reports.

## Configuration files

In the gpmdata folder (under home directory by default), you can find these files:
- gpm.config
- files.config
- nextflow.config
- export.config
- htaccess

Because these files will be overwritten when GPM is installed, please make a copy of your modified config files with the name below:
- gpm.config.user
- files.config.user
- nextflow.config.user
- export.config.user
- htaccess.user

These user-defined config files have higher priority than the default ones.

