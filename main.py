from Helper import *
from Transacttions import *
from Block import *
all_files = list_all_tx()
# print(len(all_files))

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
# print("valid_tx: {}".format(valid_tx))
# print("valid_tx_unlocked: {}".format(len(valid_tx_unlocked)))
# print("zeroes: {}".format(zeroes))

            


           

(tx_count,tx_included,fee_collected,weight_stored) =Block.get_mined_tx_data(valid_tx_unlocked)

# print("tx_count:{}".format(tx_count))
# print("tx_included: {}".format(tx_included))
# print("fee_collected:{}".format(fee_collected))
# print("weight_stored:{}".format(weight_stored))
# for tx in new_files:
#     print(tx["fee_rate"])

# print(new_files[0])


# now create a block
Block.create_block(tx_included)

# tx_hashes_list= []

# for tx in valid_tx_list:
#             tx_hash = Transacttions.Tx.get_tx_hash(tx)
#             tx_hashes_list.append(tx_hash)
# print(merkle_root(tx_hashes_list))