#This reads and processes the H5 file.

from pathlib import Path
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import gc
import h5py
import neurokit2 as nk
import time
import sys

def trim_data(data, start_time, end_time):
    return data[fz*start_time:fz*end_time]


fz = 250  # Sampling frequency of Holter Monitor
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
# Define the path for the HDF5 file
print("Initialising")
# Start coutning time
start_time = time.time()

file_path = current_dir / "HDF5 Files" / f"{entry[16]}.h5" # Change the index to the file you want to process

with h5py.File(file_path, "r") as h5file:
    group = h5file['Cheng2023']
    data = group['ECG_signal'][()]
    data = [x + 1 for x in data] # Add 1 to all values to avoid division error
    data = trim_data(data, 0, 60) # Trim the data by seconds
    detect_method = 'elgendi2010' # Configure the method here
    print("Commencing peak detection algorithm")

    #data = data[500 :] # Trims off the first two seconds of ECG
    try:
        signal_peaks, ECG_info = nk.ecg_peaks(data, sampling_rate=250, method= detect_method)
    except Exception as e:
        print("Error in processing peaks")
        gc.collect()
        print(e)
        sys.exit()
    print("Peaks Detected")
    r_peaks = signal_peaks['ECG_R_Peaks']
    r_peak_indices = r_peaks[r_peaks == 1].index  # Get indices where R-peaks are 1
    print(f'Total Peaks Detected: {np.size(r_peak_indices)}')

    #Stop counting and display time elapsed
    end_time = time.time()
    print(f"Time taken: {end_time - start_time} seconds")

    plt.figure(figsize=(10, 4))
    plt.plot(data, label="Clean ECG", color='black')
    #Adding lines at every R Peak
    for peak in r_peak_indices:
        plt.axvline(x=peak, color='red', linestyle='--', alpha=0.6)  # Dashed red line
    plt.title('R Peaks Detected using ' + detect_method)
    plt.show()