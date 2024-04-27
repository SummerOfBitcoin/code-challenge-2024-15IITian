from io import BytesIO
from unittest import TestCase
import Transacttions
from Helper import *
import time



GENESIS_BLOCK = bytes.fromhex('0100000000000000000000000000000000000000000000000000000000000000000000003ba3edfd7a7b12b27ac72c3e67768f617fc81bc3888a51323a9fb8aa4b1e5e4a29ab5f49ffff001d1dac2b7c')
TESTNET_GENESIS_BLOCK = bytes.fromhex('0100000000000000000000000000000000000000000000000000000000000000000000003ba3edfd7a7b12b27ac72c3e67768f617fc81bc3888a51323a9fb8aa4b1e5e4adae5494dffff001d1aa4ae18')
LOWEST_BITS = bytes.fromhex('ffff001d')

MAX_BLOCK_SIZE= 4000000
BLOCK_HEADER_SIZE= 320
BLOCK_SIZE_FOR_TX= MAX_BLOCK_SIZE - BLOCK_HEADER_SIZE



class Block:

    def __init__(self, version, prev_block, merkle_root,
                 timestamp, bits, nonce, tx_hashes=None):
        self.version = version
        self.prev_block = prev_block
        self.merkle_root = merkle_root
        self.timestamp = timestamp
        self.bits = bits
        self.nonce = nonce
        self.tx_hashes = tx_hashes


    def serialize_blockheader(self):
        '''Returns the 80 byte block header in hex'''
        # version - 4 bytes, little endian
        result = int_to_little_endian(self.version, 4)
        # prev_block - 32 bytes, little endian
        result += self.prev_block[::-1]
        # merkle_root - 32 bytes, little endian  -> require it in natural order in grader
        result += self.merkle_root
        # timestamp - 4 bytes, little endian
        result += int_to_little_endian(self.timestamp, 4)
        # bits - 4 bytes
        result += self.bits[::-1]
        # nonce - 4 bytes
       
        result += (self.nonce).to_bytes(4,"little")
        return result.hex()



    def hash(self):
        '''Returns the hash256 interpreted little endian of the block'''
        # serialize
        s = bytes.fromhex(self.serialize_blockheader())
        # hash256
        h256 = hash256(s)
        # reverse
        return h256.hex()


    @classmethod
    def get_mined_tx_data(cls, tx_files):
      # we assume that the tx_files are in sorted in fee_rate 
        tx_count= 0
        weight_stored= 0
        fee_collected = 0
        tx_included= []

        for tx in tx_files:
            if (BLOCK_SIZE_FOR_TX -weight_stored)> tx["weights"]:
                  tx_count+= 1
                  weight_stored+= tx["weights"]
                  fee_collected+= tx["fee"]
                  tx_included.append(tx)
            else:
                if weight_stored>= BLOCK_SIZE_FOR_TX:
                      print("shit")
                      break      
                else:
                      continue

        # sort the tx_included list
        tx_included =  sorted(tx_included, key=lambda x: x['fee_rate'],reverse=True)
           


        return (tx_count,tx_included,fee_collected,weight_stored)         


      

    @classmethod
    def create_block(cls, tx_files):
      # we assume that the tx_files are in sorted in fee_rate 
      version = 803823616
      timestamp = int(time.time())

      prev_block= "000000000000000000030ed9d2b8643c4c1d8519f34fbecaf150136e20ee183f"
      prev_block_in_bytes= bytes.fromhex(prev_block)
      
      #------------------------------------------------------------------------------------------

    

      #---------------------------------------------------------------------------------------------

      bits= "1f00ffff"
      bits_in_bytes=bytes.fromhex(bits) 
      target ="0000ffff00000000000000000000000000000000000000000000000000000000"
      nonce = 0    

      
      # get the data related to tx mined in our block
      (tx_count,tx_included,fees_collected,weight_stored)=Block.get_mined_tx_data(tx_files)

      
      #-------------------------------------------------------------------------------------------
      
      # create coinbase tx and get serliased form     
        
      
 
       # get the serliased coinbase transaction 
      serliased_coinbase_tx= Transacttions.Tx.get_serliased_coinbase_tx(fees_collected,tx_files) 

      #______________________________________________________________________________________________


      # create a list of tx_hashes of all tx which are to be mined in our block

      # First element in it -> coinbase tx_hash
      tx_hashes_list= [hash256(bytes.fromhex(serliased_coinbase_tx))]

      for tx in tx_files:
            tx_hash = Transacttions.Tx.get_tx_hash(tx)
            tx_hashes_list.append(tx_hash)

      #___________________________________________________________________________________________
       
      # we need to have coinbase tx_hash to get correct merkle root  
      merkle_root_hash= merkle_root(tx_hashes_list)


      # create an instance of a block
      block= Block(version,prev_block_in_bytes,merkle_root_hash,timestamp,bits_in_bytes,nonce,tx_hashes_list)
      # get the serliased block header
      serliased_block_header= block.serialize_blockheader()

      # get valid block header/ pow
      valid_block= block.get_valid_nonce(target)

      #______________________________________BLOCK_HEADER_________________________________________

      # Now print all the txids which are included in our block

      # get the txids from tx_hashes_list

      # As per Readme -> first tx will be coinbase tx_id  
            # wit_hashes.append(hash256(Tx.serialize(tx)))
      # coinbase_txid_in_bytes= (hash256(bytes.fromhex(serliased_coinbase_tx)))[::-1]      
      tx_ids_list= []
      for tx_hashes in tx_hashes_list:
          tx_ids_list.append((tx_hashes[::-1]).hex())


       #______________________________________________________________________________________________________

       # now print the required block details in the output.txt

       # print the serliased block header
      serliased= valid_block.serialize_blockheader()
      print(serliased)      


    #   serliased coinbase transaction
      print(serliased_coinbase_tx)

    #   print all txids
      for tx_id in tx_ids_list:
          print(tx_id)       


    

    @classmethod
    def check_pow(cls,serliased_block_header,target,nonce):
        # we assume that serliased block header is in hex 

        '''Returns whether this block satisfies proof of work'''
        # get the hash256 of the serialization of this block
        h256= hash256(bytes.fromhex(serliased_block_header))
        # interpret this hash as a little-endian number
        proof = little_endian_to_int(h256)
        # return whether this integer is less than the target
        target= int.from_bytes(bytes.fromhex(target),"big")
        return proof < target 
    
    def get_valid_nonce(self,target):
        flag = False
        MAX_NONCE_VALUE= 4294967295
        while(not flag):
            self.nonce+=1
            if self.nonce <= MAX_NONCE_VALUE: 
                serliased_block_header= self.serialize_blockheader()
                flag= Block.check_pow(serliased_block_header,target,self.nonce)
            else:
                print("shit-man")
                break
        return self    
             

