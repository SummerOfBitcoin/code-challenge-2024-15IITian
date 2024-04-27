from Helper import *
from Script import *
from Block import *



# constants related to Sequence values
SEQUENCE_MAX=4294967295

# If sequence value < MIN_NO_RBF -> then tx has enabled RBF
MIN_NO_RBF=4294967294 

# all getting sig_hash
SIGHASH_ALL = 0x01



# this list contains all tx files in mempool folder
all_files= list_all_tx()
    
    
class Tx:

    def __init__(self,version, tx_ins, tx_outs, locktime):
        self.version = version
        self.tx_ins = tx_ins  
        self.tx_outs = tx_outs
        self.locktime = locktime
       

    def __repr__(self):
        tx_ins = ''
        for tx_in in self.tx_ins:
            tx_ins += tx_in.__repr__() + '\n'
        tx_outs = ''
        for tx_out in self.tx_outs:
            tx_outs += tx_out.__repr__() + '\n'
        return 'tx: {}\nversion: {}\ntx_ins:\n{}tx_outs:\n{}locktime: {}'.format(
            self.id(),
            self.version,
            tx_ins,
            tx_outs,
            self.locktime,
        )
    
    @classmethod
    def modified_tx_files(cls,all_files):
      new_files= all_files.copy()
      for file in new_files:    
          file["is_segwit"]= False
          for input in file["vin"]:
               # add sequence category field 
               input["sequence_result"] = categorize_sequence(input["sequence"])
               if input["prevout"]["scriptpubkey_type"] in ["v1_p2tr","v0_p2wpkh","v0_p2sh_p2wpkh","v0_p2sh_p2wsh","v0_p2wsh"]:
                   file["is_segwit"]= True
   
          weights= Tx.get_tx_weights(file)
          file["fee"] = Tx.fee_for_each_tx(file) 
          file["fee_rate"]=  file["fee"] / weights
          file["weights"] =weights
          


  
      return new_files
    
    @classmethod
    def fee_for_each_tx(cls ,tx_file):
        input_amt, output_amt= 0,0
        for section in ["vin","vout"]:
            for input in tx_file[section]:
                if section == "vin":
                    input_amt+=input["prevout"]["value"]

                else:
                    output_amt+= input["value"]

        fee= input_amt- output_amt
        return fee        


    ### serialising tx -> 
    @classmethod
    def serialize(cls,file):
        if file["is_segwit"] == True:
            return Tx.serialize_segwit(file)
        else:
            return Tx.serialize_legacy(file)
        

   
    @classmethod
    def serialize_legacy(cls,file): 
        result = int_to_little_endian(file["version"], 4)
        input_tx= file["vin"]
        result += encode_varint(len(input_tx))
        for tx_in in input_tx:
            result += Transaction_Input.serialize(tx_in)

        outputs= file["vout"]    
        result += encode_varint(len(outputs))
        for tx_out in outputs:
            result += Transaction_Output.serialize(tx_out)

        locktime= file["locktime"]    
        result += int_to_little_endian(locktime, 4)
        return result


    @classmethod
    def serialize_segwit(cls,file):
        result = int_to_little_endian(file["version"], 4)

        # add Marker -> 00 and Flag -> 01 to show that the tx is segwit
        result += b'\x00\x01'

        # inputs of tx
        input_tx= file["vin"]
        # add input count
        result += encode_varint(len(input_tx))
        
        #serialise each tx_input
        for tx_in in input_tx:
            result += Transaction_Input.serialize(tx_in)


        # outputs of Tx
        outputs= file["vout"] 
        # add output count
        result += encode_varint(len(outputs))

        # serialise each tx output
        for tx_out in outputs:
            result += Transaction_Output.serialize(tx_out)


        # add witness portion
        # For legacy part -> witness = ""
        for tx_in in input_tx:  
            # check if the tx_input is legacy -> witness = ""
            if tx_in["prevout"]["scriptpubkey_type"] in ["p2sh","p2pkh","bare-multisig","op_return"]:
                result+= int_to_little_endian(0,1)
            
            else:
               result += int_to_little_endian(len(tx_in["witness"]), 1)
                # add item of witness field

               for item in tx_in["witness"]:
                   
                   if type(item) == int:
                       result += int_to_little_endian(item, 1)
                   else:
                       result += encode_varint(int(len(item)/2)) + bytes.fromhex(item)



        # add locktime             
        result += int_to_little_endian(file["locktime"], 4)
        return result
    


    @classmethod
    def get_tx_hash(cls,file):
        serliased_tx_for_txid= Tx.serialize_legacy(file)

        tx_hash= hash256(serliased_tx_for_txid)
        return tx_hash


    @classmethod    
    def sig_hash_legacy(cls,file,input_index,redeem_script=None):
        file_copy =file.copy()
        s= int_to_little_endian(file_copy["version"], 4)

        # add no of inputs
        inputs_tx= file_copy["vin"]
        s += encode_varint(len(inputs_tx))

        #  loop through each input using enumerate, so we have the input index
        for i,tx_in in enumerate(inputs_tx):
            
            # if we get the input index
            if i == input_index:

                if redeem_script:
                    tx_in["script_sig"]= redeem_script
                else:
                    tx_in["script_sig"] = tx_in["prevout"]["scriptpubkey"]

            else:
                tx_in["script_sig"] = "" # have doubt it can be None


            #the particular input scriptsig is changed -> serialised all the inputs now 

            s+= Transaction_Input.serialize(tx_in)
          

            # encode no of outputs  
            outputs= file_copy["vout"]          
            s+= encode_varint(len(outputs))

            # add the serialisation of each output
            for output in outputs:
                s+= Transaction_Output.serialize(output)

            # add locktime 
            s+= int_to_little_endian(file_copy["locktime"],4)    

            # add SIGHASH_ALL in little endian form
            s+= int_to_little_endian(SIGHASH_ALL, 4)    

            # hash256 the serialisation
            h256 = hash256(s)              

            return int.from_bytes(h256,"big") # doubt
    
   

   # Finding Sig_hash for segwit transaction -> 

     # hash of all prevouts in a segwit transaction inputs
    @classmethod
    def hash_prevouts(cls,file):
            tx_ins= file["vin"]
            all_prevouts = b''
            # all_sequence = b''
            for tx_in in tx_ins:
                all_prevouts += bytes.fromhex(tx_in["txid"][::-1]) + int_to_little_endian(tx_in["vout"], 4)
            all_prevouts_hash = hash256(all_prevouts)
            return all_prevouts_hash

    # hash of sequence of all inputs
    @classmethod
    def hash_sequence(cls,file):
        tx_ins= file["vin"]
        all_sequence = b''      
        for tx_in in tx_ins:
            all_sequence += int_to_little_endian(tx_in["sequence"],4)

            return  hash256(all_sequence)        

    
   # hash of all outputs of a tx
    @classmethod
    def hash_outputs(cls,file):
        tx_outs= file["vout"]
        all_outputs = b''
        for tx_out in tx_outs:
            all_outputs += Transaction_Output.serialize(tx_out)             
        return hash256(all_outputs)
    

    
    def sig_hash_bip143(file, input_index, redeem_script=None, witness_script=None):
        file_copy = file.copy()

        # get the specific input for which we are signing
        tx_in = file_copy["vin"][input_index]

        
        s = int_to_little_endian(file_copy["version"], 4)
        s += Tx.hash_prevouts(file_copy) 
        s+=  Tx.hash_sequence(file_copy)
        
        
        # here we want tx_id -> so it is already reverse of tx_hash -> no need to reverse it again
        s += bytes.fromhex(tx_in["txid"]) + int_to_little_endian(tx_in["vout"], 4)

        if witness_script:
            serliased_witness_script=tx_in["witness"][-1]
            script_code = encode_varint(int(len(serliased_witness_script)/2)).hex() + serliased_witness_script
        elif redeem_script:
            # script_code is in seriliased hex format
            script_code = p2pkh_script(redeem_script.split(" ")[2]) 
        else:
            # print(tx_in)
            script_code = p2pkh_script(tx_in["prevout"]["scriptpubkey_asm"].split(" ")[2])

        # convert script_code in bytes as we want in bytes not hex
        s += bytes.fromhex(script_code)

        s += int_to_little_endian(tx_in["prevout"]["value"], 8)
        s += int_to_little_endian(tx_in["sequence"], 4)
        s += Tx.hash_outputs(file_copy)
        s += int_to_little_endian(file_copy["locktime"], 4)
        s += int_to_little_endian(SIGHASH_ALL, 4)

        # return int.from_bytes(hash256(s), 'big')  `

        return int.from_bytes(hash256(s),"big")  



#  funtion which directs the result of verify the whole transaction
    @classmethod
    def verify(cls,file):
        if file["fee"] < 0 :
            return False
        
        for i in range(len(file["vin"])):
            
            if not Tx.verify_input(file,i):
                return False
            
            # verify the signatures provided.
        return True
        

# verify given input -> checks whether the script sig unlocks scriptpubkey or not
    @classmethod
    def verify_input(cls,file,input_index):
        

        # get the relevant input
        tx_in= file["vin"][input_index] # type: ignore

        # for now I am not verfying pay-to-taproot script -> just return that it is passing
        if tx_in["prevout"]["scriptpubkey_type"] == "v1_p2tr":
            return True

        # get the script_pubkey
        script_pubkey= tx_in["prevout"]["scriptpubkey_asm"] # type: ignore

        # check whether the scrip_pubkey is p2sh
        if is_p2sh_script_pubkey(script_pubkey):
        # OP_HASH160 OP_PUSHBYTES_20 524c9cae5ea3fa7639754d46540a7f67bb5c2642 OP_EQUAL
            # then the last cmd would be Redeem Script of 20 bytes
            cmd= script_pubkey[-2]  # this will be serialised redeem script 

            # get the paresed redeem_script
            redeem_script= tx_in["inner_redeemscript_asm"]

            # Possible that it is p2wpkh / p2wsh scrip-pubkey
            if is_p2wpkh_script_pubkey(redeem_script):
                z= Tx.sig_hash_bip143(file,input_index,redeem_script)
                witness= tx_in["witness"]

            elif is_p2wsh_script_pubkey(redeem_script):
                # get the parsed witness script 
                witness_script= tx_in["inner_witnessscript_asm"]  

                # calculate sig_hash
                z= Tx.sig_hash_bip143(file,input_index, witness_script= witness_script)

                # get the whole witness
                witness= tx_in["witness"]

            else:
                 z= Tx.sig_hash_legacy(file, input_index,redeem_script)  
                 witness =None  

        else:

            # script-pubkey might be a p2wpkh  or p2wsh
            if is_p2wpkh_script_pubkey(script_pubkey):
                z= Tx.sig_hash_bip143(file,input_index)
                witness= tx_in["witness"]

            elif is_p2wsh_script_pubkey(script_pubkey):
                
                # get the inner_witness script
                witness_script= tx_in["inner_witnessscript_asm"] # type: ignore

                z= Tx.sig_hash_bip143(file,input_index,witness_script= witness_script)
                witness= tx_in["witness"]
            
            else: # script may  be legacy other than p2sh
                z= Tx.sig_hash_legacy(file,input_index)
                witness=None

            # now we get the z & witness for each possible script type
        combined = tx_in["scriptsig_asm"].split(" ") + script_pubkey.split(" ")
            

        return Script.evaluate(combined,z,witness)     


    

    # get_tx_weights
    @classmethod
    def get_tx_weights(cls,file) -> int :
        # this will be used to compare fee-rates

        # legacy tx -> same as get_size()

        # get the serialised tx
        serialise_tx= Tx.serialize(file)
        if not file["is_segwit"]:
            return len(serialise_tx) * 4 # Tx.serialize give in bytes
        
        marker_size= 2

        wit_size= 0
        data= b""

        #count witness data
        # segwit tx may use inputs from both segwit and legacy -> for legacy witness -> emptY

        for input in file["vin"]:
            if input.get("witness") == None:
                # add witness = "" -> 00 -> 1 byte
                wit_size+=1
            else:
                wit_size+= 1 #len(int_to_little_endian(len(input["witness"]),1))  

                for item in input["witness"]:
                    if type(item) == int:
                        wit_size+= len(int_to_little_endian(item,1))

                    else:
                        wit_size+= len(encode_varint(int(len(item)/2))  + bytes.fromhex(item))



            # now find the bytes count in non-witness
            non_witness_count= len(serialise_tx) - (marker_size+wit_size)

            # tx_weight= non_witness_bytes*4 + witness_bytes*1
            tx_weight = non_witness_count*4 + (marker_size+ wit_size)  
            return tx_weight

    @classmethod
    def get_serliased_coinbase_tx(cls,fees_collected,tx_files):
        version =1
        locktime= 0
        tx_id= "0000000000000000000000000000000000000000000000000000000000000000"
        vout= 4294967295
        script_sig= "030cd3bf0c004f4345414e2e58595a002e"
        sequence ="ffffffff"


        # Ist Output ->   
        amount_1 = 312500000 + fees_collected

        script_pubkey_1 = "76a9142c30a6aaac6d96687291475d7d52f4b469f665a688ac"

        # IInd Output->

        # get witness_commitment
        witness_commitment = Tx.get_witness_commitment(tx_files)
        amount_2 = 0
        script_pubkey_2 = "6a24aa21a9ed" + witness_commitment 


        witness_reserved_value = "0000000000000000000000000000000000000000000000000000000000000000"
       

       # now serliase the coinbase tx
        
        s = int_to_little_endian(version,4).hex()
        s+= (b'\x00\x01').hex()

        s+="01" # no of inputs = 1

        # serliase tx input
        s+=tx_id

        s+= vout.to_bytes(4,"big").hex()

        s+= encode_varint(int(len(script_sig)/2)).hex()
        s+= script_sig

        s+= sequence 

        # serliased the output

        # output 1->

        s+= "02"

        s+= int_to_little_endian(amount_1,8).hex()
        s+= encode_varint(int(len(script_pubkey_1) / 2)).hex()
        s+= script_pubkey_1

        s+= int_to_little_endian(amount_2,8).hex()
        s+= encode_varint(int(len(script_pubkey_2) / 2)).hex()
        s+= script_pubkey_2


        # add witness
        s+= "01"
        s+="20"
        s+=witness_reserved_value
        s+=int_to_little_endian(locktime,4).hex()

        return s



                       

    @classmethod
    def get_witness_commitment(cls, tx_files):
        wit_hashes = []

        for tx in tx_files:
            wit_hashes.append(hash256(Tx.serialize(tx)))

        # now calculate witness root hash
        witness_root_hash = merkle_root(wit_hashes) 

        # witness_reserved_value 
        witness_reserved_value = "0000000000000000000000000000000000000000000000000000000000000000"

        # calculate witness_commitment 
        witness_commitment = hash256(witness_root_hash+ bytes.fromhex(witness_reserved_value))

        return witness_commitment.hex()
    

    @classmethod
    def get_unlocked_tx(cls,tx_files):
        # here we use tx_files must contain the additional fields which are included using modify tx fn
        tx_locked = []
        tx_unlocked=[]
        zeroes= 0
        for file in tx_files:
            unlock_flag= 1
            for input in file["vin"]:
                lock_enabled= input["sequence_result"]["relative_locktime"]
                if lock_enabled!= False:
                    if lock_enabled["value"] > 0:
                        tx_locked.append(file)
                        unlock_flag-=1
                        break
                    else:
                        zeroes+=1


            if unlock_flag:
                tx_unlocked.append(file)    

        return (tx_unlocked,tx_locked,zeroes)  
             
            


class Transaction_Input:

    def __init__(self,prev_txid,vout,script_sig="",sequence=0xffffffff,witness=None):
        self.prev_txid= prev_txid
        self.vout= vout
        if script_sig == "":
            self.script_sig= Script()
        else:    
            self.script_sig= script_sig
        self.sequence= sequence
       
        self.witness= witness    

    def __repr__(self):
        return '{}:{}'.format(
            self.prev_tx.hex(),
            self.prev_index,
        ) 
    
    
    # function to serialize a transaction input
    # Returns the byte serialization of the transaction input

    # Note -> whether a tx is a segwit or legacy -> tx_input serialisation will be same -> 
    # txid + sript_sig + sequence
    @classmethod
    def serialize(cls,tx_in):
        # serialize prev_tx, little endian
        tx_id= bytes.fromhex(tx_in["txid"]) 

        # we require tx_hash but tx_id in the file is reverse of tx_hash so we have to reverse it
        result =(tx_id[::-1])
        # serialize prev_index, 4 bytes, little endian
        result += int_to_little_endian(tx_in["vout"], 4)

         # script sig
        script_sig= tx_in["scriptsig"]
        # put the scriptsig size 
        result+= encode_varint(int(len(script_sig) / 2)) # scriptsig in hex
        # serialize the script_sig -> there is no need to do it -> provided in tx file
        result += bytes.fromhex(script_sig)
        # serialize sequence, 4 bytes, little endian
        result += int_to_little_endian(tx_in["sequence"], 4)
        return result
    


class Transaction_Output:

    @classmethod
    def serialize(cls, tx_out):
        result =  int_to_little_endian(tx_out["value"],8)


        # scriptpubkey 
        scriptpubkey= tx_out["scriptpubkey"]  # in hex

        # put the scriptpubkey size
        result += encode_varint(int(len(scriptpubkey) / 2))

        # add its serialised form
        result+= bytes.fromhex(scriptpubkey)

        return result
    

    

   


def categorize_sequence(sequence):   
    result= {"rbf":False,"relative_locktime":False}
    
    if sequence >= MIN_NO_RBF  or sequence == SEQUENCE_MAX:
         return result
    
    if sequence < MIN_NO_RBF:
        disable_flag= 1<<31
        if (sequence & disable_flag) != 0:
            result["rbf"]= True
            return result
        else:
            # boht rbf and relative locktime of inputs are enabled
            result["rbf"]=True
            result["relative_locktime"]={"BlockHeight":False,"Timestamp":False,"value":0}

            type_flag= 1<<22
            value = sequence & 0b111111111111111
            result["relative_locktime"]["value"]= value
          
            if (sequence & type_flag) == 0:
                result["relative_locktime"]["BlockHeight"]=True
                
            else:
                result["relative_locktime"]["Timestamp"]=True   


            return result
        

        