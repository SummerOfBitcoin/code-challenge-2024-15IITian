from io import BytesIO
import sys
import os


module_path = os.path.abspath(os.path.join('../'))
if module_path not in sys.path:
    sys.path.append(module_path)

    
from Opcodes import *
from Helper import *

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
    def add(cls,script1, script2):
        return script1.split(" ") + script2.split(" ")
        
    

    # this function is used for testing whether we are given correct asm of script or not
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
        
        return cmds
    
    

    @ classmethod
    def evaluate(cls,cmds,z,witness):
        stack =[]
        altstack= []

        while len(cmds) > 0 :
            cmd= cmds.pop(0)

            if cmd[:3] == "OP_": # this is op_code
            
              if cmd[:12] == "OP_PUSHBYTES":
                  operation = get_function_by_name(cmd[:12])

              elif cmd[:-2] == "OP_PUSHNUM":
                  operation = get_function_by_name(cmd[:-2])

              else: 
                  operation = get_function_by_name(cmd)



              if cmd in ["OP_IF","OP_NOTIF"]:
                  if not operation(stack, cmds):
                        LOGGER.info('bad op: {}'.format(cmd))
                        return False
                  
              elif cmd in ["OP_TOALTSTACK","OP_FORMALTSTACK"]:    
                  if not operation(stack, cmds):
                        LOGGER.info('bad op: {}'.format(cmd))
                        return False
                  
              elif cmd[:-2]== "OP_PUSHNUM":
                   if not operation(stack, cmd):
                       LOGGER.info('bad op: {}'.format(cmd))
                       return False
                        
              elif cmd in ["OP_CHECKSIG","OP_CHECKSIGVERIFY","OP_CHECKMULTISIG","OP_CHECKMULTISIGVERIFY"]:
                   if not operation(stack, z):
                        LOGGER.info('bad op: {}'.format(cmd))
                        return False

              else:
                 if not operation(stack):                     
                        LOGGER.info('bad op: {}'.format(cmd))
                        return False
                     

            else:
                 # this is simple data to be pushed
                 stack.append(cmd)

                 # that can be redeem script in case of p2sh
                 # OP_HASH160 OP_PUSHBYTES_20 615ee1da1eefb2f92a646ffb58a84d72240129f6 OP_EQUAL",
                 if len(cmd)==4 and cmd[0]=='OP_HASH160' \
            and cmd[1]=='OP_PUSHBYTES_20' \
            and len(bytes.fromhex(cmd[2])) == 20 and cmd[3]=='OP_EQUAL':
                     
                     # means that is p2sh
                     redeem_script= encode_varint(int(len(cmd)/2)) + cmd

                     # we execute the next three opcodes
                     
                     cmds.pop(0) # remove hash160
                     cmd.pop(0) # pushbytes20
                     h160= cmd.pop(0) # get the 20 bytes hash
                     cmd.pop(0) # remove OP_EQUAL

                     if not OP_HASH160(stack):
                         return False
                     stack.append(h160)

                     if not OP_EQUAL(stack):
                         return False
                     
                     # final result should be 1 
                     if not OP_VERIFY(stack):
                        LOGGER.info('bad p2sh h160')
                        return False
                     

                     # hash matched -> add the redeem script
                     redeem_script= encode_varint(int(len(cmd)/2)) + cmd

                     cmds.extend(Script.parse(redeem_script))

                # witness program version 0 rule. if stack cmds are:
                # 0 PUSHBYTES_20 <20 byte hash> -> p2wpkh

                 if len(stack) == 3 and stack[0]=="OP_0" and len(stack[2]) == 40:
                     stack.pop(0)
                     stack.pop(0)
                     h160= stack.pop(0)
                    
                     cmds.extend(witness)
                     cmds.extend(Script.parse(p2pkh_script(h160)))


                 # witness program version 0 rule. if stack cmds are:
                # 0 PUSHBYTES_32 <32 byte hash> this is p2wsh 

                 if len(stack) == 3 and stack[0] == "OP_0" and len(stack[2]) == 64:
                     stack.pop(0)
                     stack.pop(0)
                     s256= stack.pop(0)

                     # this will give inner_witnessscript
                     witness_script= witness[:-1]
                     witness_script_asm= Script.parse(witness_script)
                     witness_script_hash= (sha256(bytes.fromhex(witness_script))).hex()
                     cmds.extend(witness_script_asm) 

                     if s256 != witness_script_hash:
                         print('bad sha256 {} vs {}'.format(
                             s256.hex()
                         ))
                         return False
                     
        
                     final_witness_script=encode_varint(len(witness_script/2)) + witness_script
                     witness_script_cmds= Script.parse(final_witness_script)
                     cmds.extend(witness_script_cmds)



        if len(stack) == 0 :
             return False
        if stack.pop(0) == b'':
            return False
        return True




     
                         
                     
                       
                            
                       
                  







    
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


def is_p2sh_script_pubkey(script_pubkey_asm):
        cmd= script_pubkey_asm.split(" ")
        return len(cmd)==4 and cmd[0]=='OP_HASH160' \
            and cmd[1]=='OP_PUSHBYTES_20' \
            and len(bytes.fromhex(cmd[2])) == 20 and cmd[3]=='OP_EQUAL'

def is_p2wpkh_script_pubkey(script_pubkey_asm): 
        cmd= script_pubkey_asm.split(" ")
         
        return len(cmd)== 3 and [cmd[0], cmd[1]]==['OP_0','OP_PUSHBYTES_20'] \
            and len(bytes.fromhex(cmd[2])) == 20
    

def is_p2wsh_script_pubkey(script_pubkey_asm):
        cmd= script_pubkey_asm.split(" ")
        
        return len(cmd)== 3 and [cmd[0], cmd[1]]==['OP_0','OP_PUSHBYTES_32'] \
            and len(bytes.fromhex(cmd[2])) == 32

# this gives the p2pkh script corresponding to given public key hash
def p2pkh_script(h160):
    '''Takes a hash160 and returns the p2pkh ScriptPubKey in serialised hex format'''
    return  ("76a914"+  h160+"88ac")
    



            
b=  "OP_HASH160 OP_PUSHBYTES_20 dfe791507cb5a44c9a527982f5a69ade6c5421c9 OP_EQUAL"
a="OP_0 OP_PUSHBYTES_72 3045022100e1804c80eb6aecbb423d1a1223bedc3de5300ce32825a5fe979643727ebb56b00220351385c13fc79e7f8405e433bdd18c8630a446db06b693362f288a7615f7075701 OP_PUSHBYTES_72 3045022100f4dda558ecfae6d2acb68a07f51d8314e6819afebc79fba2674f79320e60d3d002204e497fa8d610514e652939f07876589fa1f2ea36d4ae2570079251a46d4d2f6001 OP_PUSHBYTES_71 522102fa3e97f867f6dd61c8f3870174a62212c568bbfa1d55fd57b8d355343d35a65c2103031d20b72222b1f6fe8217783c0adf898358afc24dee408e518e4af0dc899e7052ae"
# c=  Script.add(a,b)   
# c= c[::-1]
# print(c)
# print(c.pop(0))
# print(c.pop())
# print(c[:])

d= "001429862d65368280039b5454830c4bb728e3e87412"
e= "76a9141ef7874d338d24ecf6577e6eadeeee6cd579c67188ac"
pkh="29862d65368280039b5454830c4bb728e3e87412"
script= p2pkh_script(pkh)
# print(script)

# print(Script.parse(script))

# print(d)
# print(type(d))
# print(d[1])
# print(d.split(" "))
# print(d)
# b= b.split(" ")
# d.extend(b)
# print(d)

target= 100
# print(target.to_bytes(32, 'big'))

# {'bare-multisig',
#  'op_return',
#  'p2pkh',
#  'p2sh',
#  'v0_p2wpkh',
#  'v0_p2wsh',
#  'v1_p2tr'}

