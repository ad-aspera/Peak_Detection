#This file reads the Data on the HDF5 file and displays it
#NOTE : Anomaly (false positive) detected at 5*3600 + 30 to 5*3600 + 40 index for manikandan2012 and nabian2018 at Entry 16
#NOTE : 16 is noisy and 22 is non noisy
#NOTE : Noise data from entry 16 time_index = 5*3600 + 1160 to time_index = 5*3600 + 1160 + 20


from pathlib import Path
import h5py
import matplotlib.pyplot as plt
import numpy as np

def show_group_structure(file_path):
    with h5py.File(file_path, "r") as hdf:
        print("Groups and their datasets in the HDF5 file:\n") 

        def print_structure(name, obj):
            if isinstance(obj, h5py.Group):
                print(f"📁 Group: {name}")
            elif isinstance(obj, h5py.Dataset):
                print(f"📄 Dataset: {name} | Data Type: {obj.dtype}")

        # Walk through the file and print all groups and datasets
        hdf.visititems(print_structure)

def read_data(file_path, group_name, signal_name):
    with h5py.File(file_path, "r") as hdf:
        group = hdf[group_name]
        data = group[signal_name][()]
        return data

def plot_ecg_peaks(method, start_time, end_time):
    plt.figure(figsize=(5, 4))
    ECG_signal = read_data(file_path, "Cheng2023", "ECG_signal")
    ECG_signal = trim_signal(ECG_signal, start_time, end_time)
    plt.plot(ECG_signal)
    indices = read_data(file_path, method, "r_peak_indices")
    indices = indices[(indices >= 250*start_time) & (indices <= 250*end_time)] - 250*start_time
    for peak in indices:
        plt.axvline(x=peak, color='red', linestyle='--', alpha=0.6)  # Dashed red line
    plt.title('R Peaks Detected using ' + method)

def trim_signal(data, start_time, end_time):
    return data[250*start_time:250*end_time]

def plot_data(data):
    x = np.arange(len(data))
    plt.figure(figsize=(10,3))
    plt.plot(x, data, lw=1)
    plt.title(f"{view_signal} from {view_group}")

def plot_histogram(signal, bins=30):

    plt.figure(figsize=(8, 5))
    plt.hist(signal, bins=bins, color='blue', alpha=0.7, edgecolor='black')
    plt.xlabel('Signal Value')
    plt.ylabel('Frequency')
    plt.title(f'Histogram of {view_signal} from {view_group}')
    plt.grid(True)

def filter_intervals(r_intervals, threshold):
    Q1 = np.percentile(r_intervals, 25)
    Q3 = np.percentile(r_intervals, 75)
    IQR = Q3 - Q1
    lower_bound = Q1 - threshold * IQR
    upper_bound = Q3 + threshold * IQR
    no_outlier_intervals = r_intervals[(r_intervals >= lower_bound) & (r_intervals <= upper_bound)]
    lower_values = r_intervals[r_intervals < lower_bound]
    upper_values = r_intervals[r_intervals > upper_bound]
    print(f"For method: {view_group}")
    print(f"Original number of intervals: {len(r_intervals)}")
    print(f"Number of intervals after filtering: {len(no_outlier_intervals)}")
    print(f"Number of lower outliers: {len(lower_values)}")
    print(f"Number of upper outliers: {len(upper_values)}")
    return no_outlier_intervals, lower_values, upper_values

def find_unmatched_peaks(indices1, indices2, tolerance=5):
    #Return indices from indices1 that do not have a match in indices2 within the given tolerance.
    unmatched = [p1 for p1 in indices1 if not any(abs(p1 - p2) <= tolerance for p2 in indices2)]
    return unmatched

def compare_r_peaks(indices1, indices2, tolerance=5):
    #Checks if each peak in  has a corresponding peak in peaks2 within a given tolerance.
    matches = []
    
    for p1 in indices1:
        if any(abs(p1 - p2) <= tolerance for p2 in indices2):
            matches.append(True)  # Found a match within tolerance
        else:
            matches.append(False)  # No match found

    return matches



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
file_path = current_dir / "HDF5 Files" / f"{entry[22]}.h5" # Change the index to the file you want to process
#file_path = current_dir / "ML Data.h5"

#Which group and signal to view
view_group = "nabian2018"
view_signal = "r_intervals"
data = read_data(file_path, view_group, view_signal)

data = data[data < 5000] # Removes delays resulting from dead leads

#Filters out the outliers from the whole data
filtered_intervals, lower_values, upper_values = filter_intervals(data, 1.5)

#Calculating disagreements between the two methods
manikandan2012_indices = read_data(file_path,"manikandan2012", "r_peak_indices")
nabian2018_indices = read_data(file_path,"nabian2018", "r_peak_indices")
disagree_indices = find_unmatched_peaks(manikandan2012_indices, nabian2018_indices, tolerance=5)
print(f"Number of disagreements between manikandan2012 and nabian2018: {len(disagree_indices)}")
print(f"Disagreement indices: {disagree_indices}")

time_index = 5*3600 + 1160
plot_ecg_peaks("manikandan2012", time_index, time_index + 20)
plot_ecg_peaks("nabian2018", time_index , time_index + 20)
#Plots the data
plot_data(data)
#Plots the histogram
plot_histogram(data, bins= 400)
#plt.xlim(200, 1500)
#plt.ylim(0, 1500)
plt.show()
