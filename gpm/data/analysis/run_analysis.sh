#!/bin/bash

################## anaylsis #####################
# please Review the config.ini and adjust the analysis default configuration according to the project
# Following that, please run"
# screen -S analysis
# bash run_analysis.sh

python rmd_report_extender.py
Rscript -e rmarkdown::render("Advanced_Analysis_Report_RNAseq.Rmd", output_format = 'html_document', output_file = 'Advanced_Analysis_Report_RNAseq.html')