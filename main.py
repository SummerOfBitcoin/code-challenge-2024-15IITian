from Helper import *
from Transacttions import *
from Block import *
all_files = list_all_tx()

# modify the tx files which contains some additional fields which are important
new_files= Tx.modified_tx_files(all_files)

# sort the tx_files on fee-rate basis
new_files= sorted(new_files, key=lambda x: x['fee_rate'],reverse=True)


invalid_tx = 0
valid_tx = 0
valid_tx_list=[]
invalid_tx_list = []
for file in new_files:
    if Tx.verify(file):
        valid_tx+=1
        valid_tx_list.append(file)

    else:
        invalid_tx+=1
        invalid_tx_list.append(file)


# now segregate the transactions which can be included in our block i.e do not have any locktime constraints
 
(valid_tx_unlocked,_,zeroes)= Tx.get_unlocked_tx(valid_tx_list)
          
(tx_count,tx_included,fee_collected,weight_stored) =Block.get_mined_tx_data(valid_tx_unlocked)

# now create a block
Block.create_block(tx_included)
