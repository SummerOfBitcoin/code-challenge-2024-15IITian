## This file contains all the code which are unrelated to Bitcoin 
## But they are used as helping tools 


import json,hashlib,os


## This function will return  all the the transactions
## JSON files in mempool folder in a list 
def list_all_tx():
    # List containing all transaction files
    all_files= []

    # Specify the folder containing the JSON files
    folder_path = "../../mempool"

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




def little_endian_to_int(b):
    '''little_endian_to_int takes byte sequence as a little-endian number.
    Returns an integer'''
    return int.from_bytes(b, 'little')

def int_to_little_endian(n, length):
    '''endian_to_little_endian takes an integer and returns the little-endian
    byte sequence of length'''
    return n.to_bytes(length, 'little')

def encode_num(num):
    if num == 0:
        return b''
    abs_num = abs(num)
    negative = num < 0
    result = bytearray()
    while abs_num:
        result.append(abs_num & 0xff)
        abs_num >>= 8
    # if the top bit is set,
    # for negative numbers we ensure that the top bit is set
    # for positive numbers we ensure that the top bit is not set
    if result[-1] & 0x80:
        if negative:
            result.append(0x80)
        else:
            result.append(0)
    elif negative:
        result[-1] |= 0x80
    return bytes(result)


def decode_num(element):
    if element == b'':
        return 0
    # reverse for big endian
    big_endian = element[::-1]
    # top bit being 1 means it's negative
    if big_endian[0] & 0x80:
        negative = True
        result = big_endian[0] & 0x7f
    else:
        negative = False
        result = big_endian[0]
    for c in big_endian[1:]:
        result <<= 8
        result += c
    if negative:
        return -result
    else:
        return result

def HASH160(s):
    #sha256 followed by ripemd160
    return hashlib.new('ripemd160', hashlib.sha256(s).digest()).digest()

    
   
  
