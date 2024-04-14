import pymongo
from home.utils.parse_data import parse_data
import bson

mongo = pymongo.MongoClient('mongodb://localhost:27017')

def load_data_from_db(network, from_address, to_address):

    mongo_query = {}

    if (len(from_address) >= 40):
        mongo_query['from'] = bson.Binary(bytearray.fromhex(from_address))
    if (len(to_address) >= 40):
        mongo_query['to'] = bson.Binary(bytearray.fromhex(to_address))

    db = mongo[network]
    traces_collection = db["Traces"]
    transactions_collection = db["Transactions"]
    blocks_collection = db['Blocks']

    print(mongo_query)

    traces_cursor = traces_collection.find(mongo_query)

    traces_list = [trace for trace in traces_cursor]
    print(f'{len(traces_list)} traces')

    transactions_hashes = [trace['transaction_hash'] for trace in traces_list]
    transactions_hashes = set(transactions_hashes)
    transactions_list = []
    print(f'{len(transactions_hashes)} transactions')
    for tx_hash in transactions_hashes:
        transactions_list.append(transactions_collection.find_one({'_id': bson.Binary(tx_hash)}))

    block_numbers = [transaction['block_number'] for transaction in transactions_list]
    block_numbers = set(block_numbers)
    blocks_list = []
    for block_number in block_numbers:
        blocks_list.append(blocks_collection.find_one({'_id': block_number}))

    for trace in traces_list:
        parse_data(trace)
    for transaction in transactions_list:
        parse_data(transaction)
    for block in blocks_list:
        parse_data(block)

    return (blocks_list, transactions_list, traces_list)