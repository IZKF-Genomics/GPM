import json
import pandas as pd
import numpy as np
import os 


def parse_multiqc_files(fastq_folder_name):
    multiqc_bcl2fastq_bysample_path = os.path.join("..", "fastq", fastq_folder_name, "multiqc", "multiqc_data", "multiqc_bcl2fastq_bysample.txt")
    if not os.path.exists(multiqc_bcl2fastq_bysample_path):
        return [None, None, None, None, None]
    df_by_sample = pd.read_csv(multiqc_bcl2fastq_bysample_path, sep='\t')
    
    count_total_reads = df_by_sample['total'].sum()
    count_undetermined_reads = df_by_sample.loc[df_by_sample['Sample'] == 'undetermined', 'total'].iloc[0]
    undertermined_read_percentage = round(count_undetermined_reads / count_total_reads * 100, 1)

    read_counts = df_by_sample['total']
    std_deviation = np.std(read_counts)
    mean_value = np.mean(read_counts)
    # Calculate the coefficient of variation (CV) as a percentage
    cv_percentage = round((std_deviation / mean_value) * 100, 1)
    total_counts = read_counts.sum()
    percentages = np.round((read_counts / total_counts) * 100, decimals=1)
    distribution_string = '-'.join(map(str, percentages))

    return [std_deviation, cv_percentage, undertermined_read_percentage, distribution_string, count_total_reads]


def parse_fastq_stats_folder(fastq_folder_name):
    # Outstanding undetermined barcodes
    stats_json_path = os.path.join("..", "fastq", fastq_folder_name, "Stats", "Stats.json")
    if not os.path.exists(stats_json_path):
        print(f"the path: '{stats_json_path}' does not exists!")
        return [None, None, None]
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

    unknown_reads_array = [value for value in unknown_barcodes.values()]
    total_counts = sum(unknown_reads_array)
    percentages = [round((count / total_counts) * 100, 1) for count in unknown_reads_array]
    percentages = list(filter(lambda x: x != 0, percentages))
    main_unknown_barcode_percentage = percentages[0]
    distribution_string = '-'.join(map(str, percentages))

    return [unknown_barcodes_array[0][0], distribution_string, main_unknown_barcode_percentage]