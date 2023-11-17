import pandas as pd
import os

from datetime import datetime
from fastq_parser import parse_fastq_stats_folder, parse_multiqc_files


fastq_folder_path = os.path.join("..", "fastq")
bcl_folder_path = os.path.join("..", "fastq")
sciebo_fodler_path = ""


def main():
    fastq_folders = os.listdir(fastq_folder_path)
    fastq_dates = get_fastq_date(fastq_folders)
    data = {
        "Project Name": fastq_folders,
        "Date": fastq_dates,
        "std":  [None] * len(fastq_folders),
        "cv":  [None] * len(fastq_folders),
        "undetermined reads percentage":  [None] * len(fastq_folders),
        "most common undetermined barcode":  [None] * len(fastq_folders),
        "read distribution":  [None] * len(fastq_folders),
    }
    
    df = pd.DataFrame(data)
    df = df.sort_values(by="Date")
    df = df.set_index(['Project Name'])

    for folder in fastq_folders:
        df.loc[folder,'std'] , df.loc[folder,'cv'], df.loc[folder,'undetermined reads percentage'], df.loc[folder,'read distribution'] = parse_multiqc_files(folder)
        df.loc[folder,'most common undetermined barcode'] =  parse_fastq_stats_folder(folder)
 
    return df


def extract_date_from_folder(folder_name):
    try:
        # Extracting the YYMMDD part from the folder name
        date_str = folder_name[:6]
        # Converting the date string to a datetime object
        date_obj = datetime.strptime(date_str, '%y%m%d')
        # Formatting the datetime object as 'DD.MM.YYYY'
        formatted_date = date_obj.strftime('%d.%m.%Y')
        return formatted_date

    except ValueError:
        # Handle the case where the folder name doesn't match the expected format
        return None


def get_fastq_date(fastq_folders):
    dates = [extract_date_from_folder(folder) for folder in fastq_folders ]
    return dates



if __name__ == '__main__':
    """
    Create a data frame with the following attributes for each project:
    Name - Date - std - cv - undetermined reads percentage - most common undetermined barcode 
    """
    df = main()
    df.to_csv('sequencing_statistics.csv', index=True)
