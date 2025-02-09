from pathlib import Path
import os
import scipy.io
import h5py
import gc

# List of 8-digit numbers
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

# Create dictionary mapping of 7-digit designators 
entry = {i: eight_digit_designators[i] for i in range(len(eight_digit_designators))}

# Define the current directory
current_dir = Path(__file__).parent 
print(current_dir)

# Define the path for the HDF5 file
hdf5_dir = current_dir / "HDF5 Files"

# Create the output directory if it doesn't exist
os.makedirs(hdf5_dir, exist_ok=True)

# Loop through the files
for i in entry:
    work_file = i  # Current file identifier

    # Load the .MAT file
    file_path = current_dir / "ECG" / f"{work_file}.mat"
    mat_data = scipy.io.loadmat(file_path)

    # Extract ECG data
    if 'all' not in mat_data:
        print(f"Warning: 'all' key not found in {work_file}.mat")
        continue

    ECG_data = mat_data['all'][0]

    # Define output file name
    output_file_path = hdf5_dir / f"{work_file}.h5"

    # Define group and dataset names
    group_name = 'Cheng2023'
    dataset_name = 'ECG_signal'

    # Save data to HDF5 file
    with h5py.File(output_file_path, 'w') as hdf5_file:
        group = hdf5_file.require_group(group_name)
        group.require_dataset(dataset_name, data=ECG_data)

    print(f"ECG data successfully saved to {output_file_path}")

    # Cleanup memory
    gc.collect()
