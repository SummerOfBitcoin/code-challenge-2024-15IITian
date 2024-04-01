## This file contains all the code which are unrelated to Bitcoin 
## But they are used as helping tools 

import os
import json

## This function will return  all the the transactions
## JSON files in mempool folder in a list 
def list_all_tx():
    # List containing all transaction files
    all_files= []
    # Specify the folder containing the JSON files
    folder_path = "./mempool"

    # List all files in the folder
    files = os.listdir(folder_path)

    # Filter only JSON files
    json_files = [f for f in files if f.endswith('.json')]

    # Iterate through each JSON file
    for file in json_files:
        # Construct the full path to the JSON file
        file_path = os.path.join(folder_path, file)
    
        # Read the JSON file
        with open(file_path, 'r') as f:
            data = json.load(f)
        all_files.append(data)
    return all_files        
    
   
  
