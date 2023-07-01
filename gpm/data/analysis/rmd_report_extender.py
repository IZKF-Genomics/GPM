import csv
import os
import pandas as pd


###############################################################################
## Global variables to be used throughout the script
###############################################################################

SECTION_TEMPLATE = """
```{r, echo=FALSE, results="hide", warning=FALSE, message=FALSE}
description <- DESCRIPTION
filetag <- str_replace_all(description, " ", "_")
samples2 <- samples
samples2$VARIABLE <- factor(samples2$VARIABLE, levels = c("GROUP_B","GROUP_A"))
add_DGEA(description, filetag, samples2, paired=paired)
rmarkdown::render(paste0('DGEA_',filetag,'.Rmd'), output_format = 'html_document',
                  output_file = paste0('DGEA_',filetag,'.html'))
```
### [`r description`](`r paste0('DGEA_',filetag,'.html')`)
"""

UPLOADING_SAMPLES_PREFIX = """
```{r, echo=FALSE, results="hide", warning=FALSE, message=FALSE}
################# Loading samples ################################################
## Load sample sheets from nf-core configuration
samples <- read.table(file.path(DIR_base,"/nfcore/samplesheet.csv"), header=TRUE, sep = ",")
rownames(samples) <- samples$sample

"""

UPLOADING_SAMPLES_SUFFIX = """
# samples$VARIABLE <- labels_group
# d <- samples %>% separate(sample, c("cell", "rest"))
# samples$cell <- d$cell
# samples$rename <- paste0(samples$VARIABLE, "_", samples$sample)
```
"""

# marker string in the markdown file
rmd_analysis_file = "Analysis_Report_RNAseq.Rmd"
group_comparison_marker = "# GROUP_COMPARISON_POINTER"
sample_upload_marker = "# SAMPLE_UPLOAD_POINTER"

# Specify the path to the CSV file
contrasts_file = "contrasts.csv"
samplesheet_file = "samplesheet.csv"
comparisons = []


###############################################################################
## Generate the sample laoding section to be injected into the markdown file
###############################################################################

sample_upload_content = UPLOADING_SAMPLES_PREFIX

analysis_samplesheet_df = pd.read_csv(os.path.join(os.getcwd(),'samplesheet.csv'))
variable_columns = analysis_samplesheet_df.columns[3:].tolist()

columns_string = 'c({})'.format(', '.join(['"{}"'.format(col) for col in variable_columns]))
seperation_string = "d <- samples %>% separate(sample," + columns_string + ")\n"

for variable in variable_columns:
    seperation_string += f"samples${variable} <- d${variable} \n"


sample_upload_content += seperation_string

sample_upload_content += UPLOADING_SAMPLES_SUFFIX



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
    current_section += "\n\n"

    comparison_section_content += current_section



###############################################################################
## Inject the created sections into rnd Analysis Repord file
###############################################################################

with open(rmd_analysis_file, 'r') as file:
    rmd_contents = file.read()

# Insert the comparsions sections content into the R Markdown contents
marker_position = rmd_contents.find(group_comparison_marker)
updated_rmd_contents = rmd_contents[:marker_position] + comparison_section_content + rmd_contents[marker_position:]

# Insert the sample upload section content into the R Markdown contents
marker_position = updated_rmd_contents.find(group_comparison_marker)
updated_rmd_contents = rmd_contents[:marker_position] + sample_upload_content + rmd_contents[marker_position:]

# Write the updated contents back to the R Markdown file
with open(rmd_analysis_file, 'w') as file:
    file.write(updated_rmd_contents)
