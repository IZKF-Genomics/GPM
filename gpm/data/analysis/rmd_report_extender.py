import csv

SECTION_TEMPLATE = """
```{r, echo=FALSE, results="hide", warning=FALSE, message=FALSE}
description <- DESCRIPTION
filetag <- str_replace_all(description, " ", "_")
samples2 <- samples
samples2$group <- factor(samples2$group, levels = c("GROUP_B","GROUP_A"))
add_DGEA(description, filetag, samples2, paired=paired)
rmarkdown::render(paste0('DGEA_',filetag,'.Rmd'), output_format = 'html_document',
                  output_file = paste0('DGEA_',filetag,'.html'))
```
print
### [`r description`](`r paste0('DGEA_',filetag,'.html')`)
"""


# Specify the path to the CSV file
contrasts_file = "contrasts.csv"
comparisons = []

with open(contrasts_file, 'r') as file:
    csv_reader = csv.DictReader(file)
    for row in csv_reader:
        comparisons.append(row)

section_content = ""

for comparison in comparisons:
    current_section = SECTION_TEMPLATE
    current_section = current_section.replace('DESCRIPTION', comparison['id'])
    current_section = current_section.replace('GROUP_B', comparison['reference'])
    current_section = current_section.replace('GROUP_A', comparison['target'])
    current_section += "\n\n"

    section_content += current_section



# marker string in the markdown file
marker = "# GROUP_COMPARISON_POINTER"
rmd_file = "Analysis_Report_RNAseq.Rmd"

with open(rmd_file, 'r') as file:
    rmd_contents = file.read()

# Find the position to insert the new section
marker_position = rmd_contents.find(marker)

# Insert the section content into the R Markdown contents
updated_rmd_contents = rmd_contents[:marker_position] + section_content + rmd_contents[marker_position:]

# Write the updated contents back to the R Markdown file
with open(rmd_file, 'w') as file:
    file.write(updated_rmd_contents)
