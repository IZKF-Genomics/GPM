import json
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np


def parse_multiqc_files():
    multiqc_bcl2fastq_bysample_path = "/Users/ilyafradlin/Library/CloudStorage/OneDrive-StudentsRWTHAachenUniversity/RWTH-Aachen/Uniklinik/Tmp_multiqc/multiqc_bcl2fastq_bysample.txt"
    df_by_sample = pd.read_csv(multiqc_bcl2fastq_bysample_path, sep='\t')

    count_total_reads = df_by_sample['total'].sum()
    count_undetermined_reads = df_by_sample.loc[df_by_sample['Sample'] == 'undetermined', 'total'].iloc[0]
    undertermined_read_percentage = round(count_undetermined_reads / count_total_reads * 100, 2)
    print(f"Percentage of undetermined reads is: {undertermined_read_percentage}%")

    samples = df_by_sample['Sample']
    read_counts = df_by_sample['total']

    std_deviation = np.std(read_counts)
    mean_value = np.mean(read_counts)
    # Calculate the coefficient of variation (CV) as a percentage
    cv_percentage = (std_deviation / mean_value) * 100
    print("The Standard Deviation: {:.2f}".format(std_deviation))
    print("Coefficient of Variation (CV): {:.2f}%".format(cv_percentage))

    plt.figure(figsize=(8, 6))
    sns.barplot(x=samples, y=read_counts)
    plt.title('Distribution of reads over samples')
    plt.xlabel('samples')
    plt.ylabel('read count')
    plt.xticks(rotation=45)  # Rotate x-axis labels for better readability

    # Show the plot
    plt.tight_layout()
    plt.show()

    #------------------------------------------------------------------------------------#
    multiqc_fastqc_path = "/Users/ilyafradlin/Library/CloudStorage/OneDrive-StudentsRWTHAachenUniversity/RWTH-Aachen/Uniklinik/Tmp_multiqc/multiqc_fastqc.txt"
    multiqc_general_stats_path = "/Users/ilyafradlin/Library/CloudStorage/OneDrive-StudentsRWTHAachenUniversity/RWTH-Aachen/Uniklinik/Tmp_multiqc/multiqc_general_stats.txt"

    df_fastqc = pd.read_csv(multiqc_fastqc_path, sep='\t')
    df_general_stats = pd.read_csv(multiqc_general_stats_path, sep='\t')
    #------------------------------------------------------------------------------------#

def parse_stats_folder():
    # Outstanding undetermined barcodes
    stats_json_path = "/Users/ilyafradlin/Library/CloudStorage/OneDrive-StudentsRWTHAachenUniversity/RWTH-Aachen/Uniklinik/Tmp_multiqc/Stats/stats.json"
    with open(stats_json_path, 'r') as file:
        stats_data = json.load(file)
    unknown_barcodes_per_lane = stats_data.get('UnknownBarcodes', [])
    unknown_barcodes = {}

    # Iterate through each dictionary in the list
    for lane in unknown_barcodes_per_lane:
        # Iterate through key-value pairs in each dictionary
        lane_dict =lane['Barcodes']
        for key, value in lane_dict.items():
            # Update the combined dictionary, summing up values for duplicate keys
            unknown_barcodes[key] = unknown_barcodes.get(key, 0) + value

    unknown_barcodes_array = [[key, value] for key, value in unknown_barcodes.items()]
    unknown_barcodes_array = sorted(unknown_barcodes_array, key=lambda x: x[1], reverse=True)
    print(f"The most common undetermined barcode is '{unknown_barcodes_array[0][0]}' with an overall {unknown_barcodes_array[0][1]} reads.")
    # Slice to get the first 20 values in the first column
    Outstanding_undetermined_barcodes = [row[0] for row in unknown_barcodes_array[:20]]
    print("top twenty most abundant undetermined barcodes:")
    print(Outstanding_undetermined_barcodes)

    # print("Count of the top twenty most abundant undetermined barcodes:")
    # print(unknown_barcodes_array[:20])

    


def main():
    parse_multiqc_files()
    parse_stats_folder()
    

if __name__ == '__main__':
    main()