from io import BytesIO
import sys
import os


# module_path = os.path.abspath(os.path.join('../'))
# if module_path not in sys.path:
#     sys.path.append(module_path)
from Work.Opcodes import *
from Work.Helper import little_endian_to_int

    # "OP_DUP OP_HASH160 OP_PUSHBYTES_20 6085312a9c500ff9cc35b571b0a1e5efb7fb9f16 OP_EQUALVERIFY OP_CHECKSIG",
# "scriptpubkey":["OP_HASH160", "OP_PUSHBYTES_20","<20_BYTE_HASH>", "OP_EQUAL"],
#             "script_sig":[]
script_types= {
    "legacy":{
        "p2pkh":{
            "scriptpubkey":["OP_DUP","OP_HASH160","OP_PUSHBYTES_20","<20_BYTE_HASH>","OP_EQUALVERIFY","OP_CHECKSIG"],
            "script_sig":["<Signature>","<pubkey>"]
        },
        "p2sh":{
            "normal-p2sh"
            
        },
        "bare-multisig":{
            "scriptpubkey":["OP_PUSHNUM_M","N(PushBytes + PubKeys)", "OP_PUSHNUM_N", "OP_CHECKMULTISIG"],
            "script_sig":[]
        }        
    },
    "segwit":{
        "v0_p2wpkh":{
            "scriptpubkey":["OP_0", "OP_PUSHBYTES_20","<20_BYTE_HASH>"],
            "script_sig":""
        },
        "v0_p2wsh":{
            "scriptpubkey":["OP_0" "OP_PUSHBYTES_32" "<32_Byte_Hash>"],
            "script_sig":""
        },
        "v1_p2tr":{
            "scriptpubkey":["OP_PUSHNUM_1", "OP_PUSHBYTES_32", "<32_BYTE_HASH>"],
            "script_sig":""
        },
    },
    "op_return":"OP_RETURN"
}
class Script:
    def __init__(self,cmds=None):
        if cmds is None:
            self.cmds= []
        else:
            self.cmds= cmds 


    def __repr__(self):
        result= []
        errors=[]
        # for cmd in self.cmds:
        #     if type(cmd) == int:
        #         if OP_CODE_NAMES.get(cmd):
        #             semi_parse.append("\t".join (OP_CODE_NAMES.get(cmd))) 
        #         else:
        #             errors.append("\t".join (cmd))

        #     else:
        #         semi_parse.append("\t".join (cmd)) 
        # return ' '.join(semi_parse)

        for cmd in self.cmds:
            if type(cmd) == int:
                if OP_CODE_NAMES.get(cmd):
                    name = OP_CODE_NAMES.get(cmd)
                else:
                    name = 'OP_[{}]'.format(cmd)
                result.append(name)
            else:
                result.append(str(cmd))
        return ' '.join(result)  
    
    @classmethod
    def parse(cls,script_in_hex):  
        # in the files scrippubkey and scriptsig , lenght of these are not encoded
        # we have to find length of script here
        bytes_data= bytes.fromhex(script_in_hex)
        
        length= len(bytes_data)
        s = BytesIO(bytes_data)
       
        # initialize the cmds array
        cmds = []
        # initialize the number of bytes we've read to 0
        count = 0
        # loop until we've read length bytes
        while count < length:

            data_length=0
            # get the current byte
            current = s.read(1)
            # increment the bytes we've read
            count += 1
            # convert the current byte to an integer
            current_byte = current[0]

            #Pushing the op code -> 
            # hex_format= hex(current_byte)[2:].zfill(2)
            # print("current buyte : {}".format(current_byte))
            op_code = OP_CODE_NAMES.get(current_byte)
            

                # add the op_code to the list of cmds
            cmds.append(op_code)
            # if the current byte is between 1 and 75 inclusive
            if current_byte >= 1 and current_byte <= 75:
                # we have an cmd set n to be the current byte
                data_length = current_byte
                
                # increase the count by n
                count += data_length
            elif current_byte == 76:
                # op_pushdata1
                data_length = little_endian_to_int(s.read(1))
                count += data_length + 1
            elif current_byte == 77:
                # op_pushdata2
                data_length = little_endian_to_int(s.read(2))
                count += data_length + 2
            
            if  data_length:
             cmds.append((s.read(data_length)).hex())

        if count != length:
            raise SyntaxError('parsing script failed')
        
        return cls(cmds)
    

#     # "OP_DUP OP_HASH160 OP_PUSHBYTES_20 6085312a9c500ff9cc35b571b0a1e5efb7fb9f16 OP_EQUALVERIFY OP_CHECKSIG",
#     # @classmethod
#     # def is_p2pkh_scriptpubkey(script_pub_key_hex):
#     #     cmds= Script.parse(script_pub_key_hex)
#     #     for cmd in cmds



# # a= "0014392f28fde2dcf2cccbd05885e22d7b823fb2b5d9"
# # b=Script.parse(a)
# # print(b)


# types of script used in here-> 
# {'bare-multisig',
#  'op_return',
#  'p2pkh',
#  'p2sh',
#  'v0_p2wpkh',
#  'v0_p2wsh',
#  'v1_p2tr'}

