#This file is being used to modify the data in the database
from pathlib import Path
import numpy as np
import pandas as pd
import gc
import h5py
import neurokit2 as nk
import time
import sys

def replace_dataset(dataset_name, data, group):
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

#Define the path for the Target HDF5 file
Target_dir = current_dir / "Our_Data.h5"

source_group = "nabian2018"      # The group in each source file
dataset_name = "r_intervals"     # The dataset to extract and copy

for i in range(len(entry)):
    #Open the source file and read the data
    source_dir = current_dir / "HDF5 Files" / f"{entry[i]}.h5" # Change the index to the file you want to process
    with h5py.File(source_dir, "r") as source_file:
        copy_group = source_file[source_group]
        data = copy_group[dataset_name][()]
        #Write the data to the target file
        with h5py.File(Target_dir, "a") as target_file:
            target_group = target_file.require_group(entry[i])
            replace_dataset(dataset_name, data, target_group)
    print(f"{entry[i]} added to the file")
    print(f"{i + 1} out of {len(entry)} added")
print("All datasets added")

