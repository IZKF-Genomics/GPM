import json
import pandas as pd
import numpy as np
import os 



def parse_multiqc_files(fastq_folder_name):
    multiqc_bcl2fastq_bysample_path = os.path.join("..", "fastq", fastq_folder_name, "multiqc", "multiqc_data", "multiqc_bcl2fastq_bysample.txt")
    if not os.path.exists(multiqc_bcl2fastq_bysample_path):
        return [None, None, None]
    df_by_sample = pd.read_csv(multiqc_bcl2fastq_bysample_path, sep='\t')
    
    count_total_reads = df_by_sample['total'].sum()
    count_undetermined_reads = df_by_sample.loc[df_by_sample['Sample'] == 'undetermined', 'total'].iloc[0]
    undertermined_read_percentage = round(count_undetermined_reads / count_total_reads * 100, 2)
    # print(f"Percentage of undetermined reads is: {undertermined_read_percentage}%")
    #samples = df_by_sample['Sample']

    read_counts = df_by_sample['total']

    std_deviation = np.std(read_counts)
    mean_value = np.mean(read_counts)
    # Calculate the coefficient of variation (CV) as a percentage
    cv_percentage = (std_deviation / mean_value) * 100

    total_counts = read_counts.sum()
    percentages = np.round((read_counts / total_counts) * 100, decimals=1)
    distribution_string = '-'.join(map(str, percentages))

    return [std_deviation, cv_percentage, undertermined_read_percentage, distribution_string]

    # plt.figure(figsize=(8, 6))
    # sns.barplot(x=samples, y=read_counts)
    # plt.title('Distribution of reads over samples')
    # plt.xlabel('samples')
    # plt.ylabel('read count')
    # plt.xticks(rotation=45)  # Rotate x-axis labels for better readability






def parse_fastq_stats_folder(fastq_folder_name):
    # Outstanding undetermined barcodes
    stats_json_path = os.path.join("..", "fastq", fastq_folder_name, "Stats", "Stats.json")
    if not os.path.exists(stats_json_path):
        print(f"the pat: '{stats_json_path}' does not exists!")
        return None
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
    
    # Slice to get the first 20 values in the first column
    # Outstanding_undetermined_barcodes = [row[0] for row in unknown_barcodes_array[:20]]
    # print("Count of the top twenty most abundant undetermined barcodes:")
    # print(unknown_barcodes_array[:20])

    print(f"the unknown_barcodes_array:{unknown_barcodes_array[0][0]}")
    return unknown_barcodes_array[0][0]