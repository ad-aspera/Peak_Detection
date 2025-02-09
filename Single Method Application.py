#This file applies a singular method to the whole dataset

from pathlib import Path
import numpy as np
import pandas as pd
import gc
import h5py
import neurokit2 as nk
import time
import sys

def filter_intervals(r_intervals, threshold):
    Q1 = np.percentile(r_intervals, 25)
    Q3 = np.percentile(r_intervals, 75)
    IQR = Q3 - Q1
    lower_bound = Q1 - threshold * IQR
    upper_bound = Q3 + threshold * IQR
    return r_intervals[(r_intervals >= lower_bound) & (r_intervals <= upper_bound)]

def add_dataset(dataset_name, data, group):
    # Check if dataset exists, delete and replace it
    if dataset_name in group:
        del group[dataset_name]  # Delete the existing dataset

    # Create a new dataset with the new data
    group.create_dataset(dataset_name, data=data)

fz = 250  # Sampling frequency of Holter Monitor
sampling_time = 1000/fz
eight_digit_designators = [
    "19070921", "19072205", "19072214",
    "19072938", "19072939", "19072940",
    "19080106", "19080715", "19081506",
    "19082406", "19090308", "19090320",
    "19101607", "19101619", "19102102",
    "19102103", "19102524", "19102622",
    "19112609", "19120302", "19120323",
    "19120704", "19120723", "19121303",
    "19121735", "20010826", "20010827",
    "20011712", "20050628", "20052606",
    "20061729", "20092226", "20092535",
    "20101424", "20101822", "20102029",
    "20120116", "20120922", "20121033",
    "20121716", "20121718", "20122932",
    "20123017"
]
# Create dictionary mapping of 8-digit designators 
entry = {i: eight_digit_designators[i] for i in range(len(eight_digit_designators))}

# Define the current directory
current_dir = Path(__file__).parent

detect_method = 'nabian2018' # Configure the method here, emrich2023 is restircted to 3363 seconds max
#NOTE: "20101424" had 2 seconds trimmed from the start to allow ramikandan2012 to work

#Certain methods may require processing in Chunks
#start = 0 # Start index of the chunk
#end = 43 #End index of the chunk
#chunk = np.arange(start, end, 1)
#print(chunk)

for i in range(len(entry)):
    #Define the path for the HDF5 file
    file_path = current_dir / "HDF5 Files" / f"{entry[i]}.h5" # Change the index to the file you want to process

    with h5py.File(file_path, "r") as h5file:
        group = h5file['Cheng2023']
        data = group['ECG_signal'][()]
        data = [x + 1 for x in data] # Add 1 to all values to avoid log(0) error

        try:
            signal_peaks, ECG_info = nk.ecg_peaks(data, sampling_rate= fz, method= detect_method)
        except Exception as e:
            print("Error in processing peaks")
            gc.collect()
            print(e)
            sys.exit()
        
        r_peaks = signal_peaks['ECG_R_Peaks']
        r_peak_indices = r_peaks[r_peaks == 1].index  # Get indices where R-peaks are present
        r_intervals = sampling_time*np.diff(r_peak_indices) # Calculate R-R intervals
        #filtered_intervals = filter_intervals(r_intervals, 1.5) No need for if using nabian2018 

    # Open (or create) the HDF5 file
    with h5py.File(file_path, "a") as hdf:
        group_name = detect_method

        # Step 1: Check if group exists, create if not
        if group_name not in hdf:
            group = hdf.create_group(group_name)
        else:
            group = hdf[group_name]

        add_dataset("r_peaks", r_peaks, group)
        add_dataset("r_peak_indices", r_peak_indices, group)
        add_dataset("r_intervals", r_intervals, group)
        #add_dataset("filtered_intervals", filtered_intervals, group)

        del data, r_peaks, r_peak_indices, r_intervals #Delete to conserve memory

        print(f"{entry[i]} done")
        print(f"{i + 1} out of {len(entry)} done")
        gc.collect()
print("All files processed")