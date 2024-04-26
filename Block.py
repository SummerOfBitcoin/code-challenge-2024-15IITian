from io import BytesIO
from unittest import TestCase
import Transacttions
# from Transacttions import *
from Helper import *

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
        '''Returns the 80 byte block header'''
        # version - 4 bytes, little endian
        result = int_to_little_endian(self.version, 4)
        # prev_block - 32 bytes, little endian
        result += self.prev_block[::-1]
        # merkle_root - 32 bytes, little endian
        result += self.merkle_root[::-1]
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
      timestamp = 1714064564

      prev_block= "000000000000000000030ed9d2b8643c4c1d8519f34fbecaf150136e20ee183f"
      prev_block_in_bytes= bytes.fromhex(prev_block)
      
      #------------------------------------------------------------------------------------------

      # create a list of tx_hashes of all tx which are to be mined in our block
      tx_hashes_list= []

      for tx in tx_files:
            tx_hash = Transacttions.Tx.get_tx_hash(tx)
            tx_hashes_list.append(tx_hash)

      #---------------------------------------------------------------------------------------------

      merkle_root_hash= merkle_root(tx_hashes_list)
    #   print("merkle_root_hash: {}".format(merkle_root_hash.hex()))
      bits= "1f00ffff"
      bits_in_bytes=bytes.fromhex(bits) 
      target ="0000ffff00000000000000000000000000000000000000000000000000000000"
      nonce = 0    

      
      # get the data related to tx mined in our block
      (tx_count,tx_included,fees_collected,weight_stored)=Block.get_mined_tx_data(tx_files)
    #   print("tx_count:{} , fees_collected :{} , weight_stored : {}".format(tx_count,fees_collected,weight_stored)) 

      # create an instance of a block
      block= Block(version,prev_block_in_bytes,merkle_root_hash,timestamp,bits_in_bytes,nonce,tx_hashes_list)
      # get the serliased block header
      serliased_block_header= block.serialize_blockheader()

    #   print("block header:{}\n".format(serliased_block_header))

    #   print("block_hash: {}".format(block.hash()))
      #-------------------------------------------------------------------------------------------

      # get valid block header/ pow
        
        
      valid_block= block.get_valid_nonce(target)
    #   print(valid_block.serialize_blockheader())
      #______________________________________BLOCK_HEADER_________________________________________
 
       # get the serliased coinbase transaction 
      serliased_coinbase_tx= Transacttions.Tx.get_serliased_coinbase_tx(fees_collected,tx_files) 
    #   print("coinbase transaction: {}".format(serliased_coinbase_tx))

      #______________________________________________________________________________________________

      # Now print all the txids which are included in our block

      # get the txids from tx_hashes_list

      tx_ids_list= []
      for tx_hashes in tx_hashes_list:
          tx_ids_list.append((tx_hashes[::-1]).hex())


       #______________________________________________________________________________________________________

       # now print the required block details in the output.txt

       # block header
      
      print("{} {} {} {} {} {} ".format(valid_block.version,(valid_block.prev_block).hex(),(valid_block.merkle_root).hex(),valid_block.timestamp,(valid_block.bits).hex(),valid_block.nonce))    

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

    
        # print("{} : {} \n".format(nonce,proof.to_bytes(32,"big").hex()) )
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
        # if flag:
        #     print("required nonce: {}".format(self.nonce))      

        return self    
             


# block_header= "0060e92f3f18ee206e1350f1cabe4ff319851d4c3c64b8d2d90e030000000000000000005f73d58ab5be2407065a26a290750250c1ebebc46a280e6f2b1c5032b3397c2ab48c2a66ffff001f00000000"
# target ="0000ffff00000000000000000000000000000000000000000000000000000000"

# print(Block.check_pow(block_header,target))