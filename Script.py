from io import BytesIO
import sys
import os


module_path = os.path.abspath(os.path.join('../'))
if module_path not in sys.path:
    sys.path.append(module_path)
from Work.Opcodes import *
from Helper import little_endian_to_int

    # "OP_DUP OP_HASH160 OP_PUSHBYTES_20 6085312a9c500ff9cc35b571b0a1e5efb7fb9f16 OP_EQUALVERIFY OP_CHECKSIG",
# "scriptpubkey":["OP_HASH160", "OP_PUSHBYTES_20","<20_BYTE_HASH>", "OP_EQUAL"],
#             "script_sig":[]
script_types= {
    
        "p2pkh":{
            "scriptpubkey":["OP_DUP","OP_HASH160","OP_PUSHBYTES_20","<20_BYTE_HASH>","OP_EQUALVERIFY","OP_CHECKSIG"],
            "script_sig":["<Signature>","<pubkey>"]
        },
        "p2sh":{
             "scriptpubkey":["OP_HASH160", "OP_PUSHBYTES_20", "<20_BYTE_HASH>", "OP_EQUAL"],
             "script_sig":"" ## can be anything depending on redeem script but will contain redeem script          
            
        },
        "bare-multisig":{
            "scriptpubkey":["OP_PUSHNUM_M","N(PushBytes + PubKeys)", "OP_PUSHNUM_N", "OP_CHECKMULTISIG"],
            "script_sig":[]
        },   

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
        "v0_p2sh_p2wpkh":{
            "scriptpubkey":["OP_HASH160", "OP_PUSHBYTES_20", "<20_BYTE_HASH>", "OP_EQUAL"],
            "script_sig":["OP_PUSHBYTES_22","<20 BYTE REDEEM_SCRIPT HASH>"],
            "witness":[]
        },
        "v0_p2sh_p2wsh":{
            "scriptpubkey":["OP_HASH160", "OP_PUSHBYTES_20", "<20_BYTE_HASH>", "OP_EQUAL"],
            "script_sig":["OP_PUSHBYTES_34","<20 BYTE REDEEM_SCRIPT HASH>"],
            "witness":[]
        }
   
    #    "op_return":"OP_RETURN"
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
    
    

    
    # function to check whether a given scriptpubkey matches with the type mentioned in scripttype
    @classmethod
    def is_scriptpubkey_match_scripttype(cls,script_pubkey_asm,script_type):
        cmd= script_pubkey_asm.split(" ")
        if script_type == 'op_return':
            return cmd[0] == "OP_RETURN"
        elif script_type == 'p2pkh':
            return len(cmd)==6 and [cmd[0],cmd[1],cmd[2]]== ['OP_DUP','OP_HASH160','OP_PUSHBYTES_20']  and len(bytes.fromhex(cmd[3])) == 20 \
                  and [cmd[4],cmd[5]] == ['OP_EQUALVERIFY','OP_CHECKSIG']
        
        elif script_type in ['p2sh','v0_p2sh_p2wpkh','v0_p2sh_p2wsh']:
            return len(cmd)==4 and cmd[0]=='OP_HASH160' \
            and cmd[1]=='OP_PUSHBYTES_20' \
            and len(bytes.fromhex(cmd[2])) == 20 and cmd[3]=='OP_EQUAL'
        
        elif script_type == 'v1_p2tr':
            return len(cmd)== 3 and [cmd[0], cmd[1]]==['OP_PUSHNUM_1','OP_PUSHBYTES_32'] \
            and len(bytes.fromhex(cmd[2])) == 32
        
        elif script_type =='v0_p2wpkh':
            return len(cmd)== 3 and [cmd[0], cmd[1]]==['OP_0','OP_PUSHBYTES_20'] \
            and len(bytes.fromhex(cmd[2])) == 20
        
        elif script_type == 'v0_p2wsh':
             return len(cmd)== 3 and [cmd[0], cmd[1]]==['OP_0','OP_PUSHBYTES_32'] \
            and len(bytes.fromhex(cmd[2])) == 32
        
        else: # bare-multisig
            return is_bare_multisig_script_type(cmd)



        


def is_bare_multisig_script_type(cmd):         
       #OP_PUSHNUM_1  
        counter=1
        if cmd[0][:-2] == 'OP_PUSHNUM' and cmd[-2][:-2]== 'OP_PUSHNUM': 
           threshold= int(cmd[0][-1])
           total= int(cmd[-2][-1])
           if total*2 + 3 != len(cmd):
               return False
           if total>= threshold:
               for _ in range(total):
                   if  not (cmd[counter]=='OP_PUSHBYTES_33' and len(bytes.fromhex(cmd[counter+1])) ==33):
                       return False
                   counter+=2
                   
               if (cmd[-1] =='OP_CHECKMULTISIG'):   
                 return True    
               else:
                 return False                 
                   

           else:
               return False    
           
        else:
             return False
    



    

            
    


# {'bare-multisig',
#  'op_return',
#  'p2pkh',
#  'p2sh',
#  'v0_p2wpkh',
#  'v0_p2wsh',
#  'v1_p2tr'}

