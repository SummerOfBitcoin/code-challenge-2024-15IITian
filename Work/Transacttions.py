from Script import *
from Helper import * 

# this list contains all tx files in mempool folder
all_files= list_all_tx()
class Tx:

    def __init__(self, version, tx_ins, tx_outs, locktime, testnet=False):
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
    def fee_for_each_tx(tx_file):
        input_amt, output_amt= 0,0
        for section in ["vin","vout"]:
            for input in tx_file[section]:
                if section == "vin":
                    input_amt+=input["prevout"]["value"]

                else:
                    output_amt+= input["value"]

        fee= input_amt- output_amt
        return fee                

                 

        
        
    




class Transaction_Input:

    def _init_(self,prev_txid,vout,script_sig="",sequence=0xffffffff,witness=None):
        self.prev_txid= prev_txid
        self.vout= vout
        if script_sig == "":
            self.script_sig= Script()
        else:    
            self.script_sig= script_sig
        self.sequence= sequence
       
        self.witness= witness   # doing this for now 

    def __repr__(self):
        return '{}:{}'.format(
            self.prev_tx.hex(),
            self.prev_index,
        ) 
    


class Tranasaction_Output:
    def __init__(self,amount,script_pubkey):
        self.amount= amount
        self.script_pubkey= script_pubkey

    def __repr__(self):
        return '{}:{}'.format(self.amount, self.script_pubkey) 

   
