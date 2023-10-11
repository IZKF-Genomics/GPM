# GPM (Genomic Project Manager)

This command line tool is designed to simplify and automatize the bioinformatic workflow. 

## Table of Contents
- [GPM (Genomic Project Manager)](#gpm-genomic-project-manager)
  - [Table of Contents](#table-of-contents)
  - [Features](#features)
  - [Target users](#target-users)
  - [Installation](#installation)
  - [Usage](#usage)
    - [Demultiplexing](#demultiplexing)
    - [Single-cell applications](#single-cell-applications)
    - [Initialize a project](#initialize-a-project)
    - [Running nf-core pipeline](#running-nf-core-pipeline)
    - [Analysis](#analysis)
    - [Export Project](#export-project)
    - [Export Raw Data](#export-raw-data)
    - [Create Export folder on Web Server](#create-export-folder-on-web-server)
  - [Configuration files](#configuration-files)
  - [Repository Structure](#repository-structure)
  - [License](#license)

 
## Features

The main tasks include:
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
```bash
# export GPMDATA=/data/gpmdata
git clone https://github.com/IZKF-Genomics/GPM.git
cd GPM
pip install .
gpm --help
```

## Usage:

## Demultiplexing

### Bulk sequencing applications:

```bash
gpm demultiplex --raw PATH_TO_BCL --output OUTPUT_DIR
```
This command will prepare two files for you:
- samplesheet_bcl2fastq.csv
- run_bcl2fastq.sh
- config.ini

You will have to modify samplesheet_bcl2fastq.csv with your sample information and indeces, then run run_bcl2fastq.sh by the following command:
```bash
screen -S fastq
bash run_bcl2fastq.sh
```

### Single-cell applications:
```bash
gpm demultiplex --raw PATH_TO_BCL --output OUTPUT_DIR -sc
```
This command will prepare two files for you:
- samplesheet_cellranger.csv
- run_cellranger.sh

## Initialize a project

```bash
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

Once the data has been processed, you can perform downstream analysis using the provided Rmd template. Execute the following command:

```bash
gpm analysis config.ini
```

This command will generate several Rmd files in the analysis folder, with all the parameters properly defined based on the project information.
In the analysis folder, there are key files that require further inspection and adjustments:

1. **config.yml**: This file contains project-specific parameters. Ensure that you adjust the default settings correctly. Here is an example of the structure:
    ```yaml
    default:
          spikein_ERCC: FALSE  # Choose either TRUE or FALSE
          organism: "hsapiens"  # Choose one of "hsapiens", "mmusculus", or "rnorvegicus"
    ```
            
2. **samplesheet.csv**:  This file is automatically generated and follows a specific format:

    ```csv
    sample,fastq_1,fastq_2,condition,column1,column2,... (depending on the samples' names)
    
    - please adjust the names of column1, column2... according to you project design.
    - These names will be used in combination with the contrasts.csv, Thus the corresponding names in both files have to be identical!
    ```

3. **contrasts.csv**: The contrasts file references the observations file to define groups of samples to compare. 
    For example, based on the sample sheet above we could define contrasts like:
   
    ```csv
    id,variable, paired, reference,target,blocking
    control_VS_treated,condition,FALSE, control,treated, batch
    control_VS_treated_paired,condition,TRUE,control,treated,batch
    ```

    The fields, in order, are:
    
    - id: An arbitrary identifier used to name contrast-specific output files.
    - variable: The column from the observations information used to define groups.
    - paired: Indicates whether the comparison should be performed in a paired manner. Use TRUE or FALSE.
    - reference: The base/reference level for the comparison. Features with higher values in this group will generate negative fold changes.
    - target: The target/non-reference level for the comparison. Features with higher values in this group will generate positive fold changes.
    - blocking: An optional field indicating a blocking factor, if applicable.
   
Review and adjust these files accordingly to perform the desired analysis.

Eventually, after the required adjustment specified above, run the 'run_analysis.sh' script, this will generate the following report: 'Analysis_Report_APP.html'.
This report could be the landing page for the clients where they can download the data, browse the results and read the analysis reports.

## Export Project
```bash
gpm export -config config.ini -symprefix /mnt/nextgen /mnt/web/var/www/html/data/YYMMDD_Name1_Name2_Institute_App
```
- This command needs to be executed in the folder for project where config.ini is.
- The name of the project folder is strictly controlled:
    - YYMMDD: The date must be a valid date.
    - Name1: The surname of the contact person.
    - Name2: The surname of the PI or the group name.
    - Institute: The name of the department or company.
    - App: The application defined in the gpm.config file.

This command will generate the folder structure with proper soft-links in the target path.

## Export Raw Data

```bash
gpm export-raw --symprefix MOUNT_PREFIX --config config.ini --name YYMMDD_Name1_Name2_Institute_App EXPORT_DIR_PATH
```
- This command needs to be executed in the folder for demultiplexing.
- multiqc is a bolean flag indicating if the multiqc report needs to be included as well.
- The name of the project folder is strictly controlled:
    - YYMMDD: The date must be a valid date.
    - Name1: The surname of the contact person.
    - Name2: The surname of the PI or the group name.
    - Institute: The name of the department or company.
    - App: The application defined in the gpm.config file.

This command will create a folder in the export dir path, containg the sym links to the fastq folder, bcl folder, and optionally the multiqc report.

## Create Export folder on Web Server
```bash
cd /var/www/html/data/ # on GF Web Server
gpm export -user USERNAME YYMMDD_Name1_Name2_Institute_FASTQ -bcl /mnt/PATH_to_BCL -fastq /mnt/PATH_to_FASTQ
```

Sometimes, it is more convenient to create the export folder on the web server and link to the old data. The above command can be used in this scenerio.

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

## Repository Structure


## License

MIT License

Copyright (c) 2021 IZKF-Genomics

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
