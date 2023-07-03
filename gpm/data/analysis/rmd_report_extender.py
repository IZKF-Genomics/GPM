import csv
import os
import pandas as pd


###############################################################################
## Global variables to be used throughout the script
###############################################################################

SECTION_TEMPLATE = """
```{r, echo=FALSE, results="hide", warning=FALSE, message=FALSE}
description <- "DESCRIPTION"
filetag <- str_replace_all(description, " ", "_")
samples2 <- samples
samples2$VARIABLE <- factor(samples2$VARIABLE, levels = c("GROUP_B","GROUP_A"))
add_DGEA(description, filetag, samples2, paired=PAIRED)
rmarkdown::render(paste0('DGEA_',filetag,'.Rmd'), output_format = 'html_document',
                  output_file = paste0('DGEA_',filetag,'.html'))
```
### [`r description`](`r paste0('DGEA_',filetag,'.html')`)
"""


# marker string in the markdown file
rmd_analysis_file = "Analysis_Report_RNAseq.Rmd"
group_comparison_marker = "# GROUP_COMPARISON_POINTER"

# Specify the path to the CSV file
contrasts_file = "contrasts.csv"
samplesheet_file = "samplesheet.csv"
comparisons = []


###############################################################################
## Generate the required comparisons to be injected into the markdown file
###############################################################################

with open(contrasts_file, 'r') as file:
    csv_reader = csv.DictReader(file)
    for row in csv_reader:
        comparisons.append(row)

comparison_section_content = ""

for comparison in comparisons:
    current_section = SECTION_TEMPLATE
    current_section = current_section.replace('DESCRIPTION', comparison['id'])
    current_section = current_section.replace('VARIABLE', comparison['variable'])
    current_section = current_section.replace('GROUP_B', comparison['reference'])
    current_section = current_section.replace('GROUP_A', comparison['target'])
    current_section = current_section.replace('PAIRED', comparison['paired'])
    current_section += "\n\n"

    comparison_section_content += current_section



###############################################################################
## Inject the created sections into rnd Analysis Report file
###############################################################################

with open(rmd_analysis_file, 'r') as file:
    rmd_contents = file.read()

# Replace the group comparison marker with the comparison section content
updated_rmd_contents = rmd_contents.replace(group_comparison_marker, comparison_section_content, 1)


# Write the updated contents back to the R Markdown file
with open(rmd_analysis_file, 'w') as file:
    file.write(updated_rmd_contents)
