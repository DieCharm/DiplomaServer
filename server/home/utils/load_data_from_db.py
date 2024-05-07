import pymongo
from home.utils.parse_data import parse_data
from home.utils.shorten_initial_trace_addresses.shorten_initial_from_trace_addresses import shorten_initial_from_trace_addresses
from home.utils.shorten_initial_trace_addresses.shorten_initial_to_trace_addresses import shorten_initial_to_trace_addresses
from home.utils.mark_traces.after_from import after_from
from home.utils.mark_traces.before_to import before_to
from home.utils.compare_traces import compare_traces
from functools import cmp_to_key
import bson

mongo = pymongo.MongoClient('mongodb://localhost:27017')

def load_data_from_db(network, from_address, to_address):

    db = mongo[network]
    traces_collection = db["Traces"]
    transactions_collection = db["Transactions"]
    blocks_collection = db['Blocks']

    from_address_hex = str(from_address)
    to_address_hex = str(to_address)

    if (len(from_address_hex) == 42):
        from_address_hex = from_address_hex[2:]
    if (len(to_address) == 42):
        to_address_hex = to_address_hex[2:]

    traces_from_list = []
    traces_to_list = []

    transactions_from_hashes = []
    transactions_to_hashes = []

    if (len(from_address_hex) == 40):
        mongo_query_from = {"from": bson.Binary(bytearray.fromhex(from_address_hex))}

        print(mongo_query_from)
        traces_cursor_from = traces_collection.find(mongo_query_from)
        traces_from_list = list(traces_cursor_from)
        print(f'{len(traces_from_list)} from traces')

        transactions_from_hashes = [trace['transaction_hash'] for trace in traces_from_list]

    if (len(to_address_hex) == 40):
        mongo_query_to = {"to": bson.Binary(bytearray.fromhex(to_address_hex))}

        print(mongo_query_to)
        traces_cursor_to = traces_collection.find(mongo_query_to)
        traces_to_list = list(traces_cursor_to)
        print(f'{len(traces_to_list)} to traces')

        transactions_to_hashes = [trace['transaction_hash'] for trace in traces_to_list]


    transactions_hashes = []

    if (len(transactions_from_hashes) > 0 and len(transactions_to_hashes) == 0):
        transactions_hashes = transactions_from_hashes

    if (len(transactions_from_hashes) == 0 and len(transactions_to_hashes) > 0):
        transactions_hashes = transactions_to_hashes

    if (len(transactions_from_hashes) > 0 and len(transactions_to_hashes) > 0):
        transactions_hashes = [tx_hash for tx_hash in transactions_from_hashes if tx_hash in transactions_to_hashes]

    transactions_hashes = frozenset(transactions_hashes)

    transactions_list = []
    print(f'{len(transactions_hashes)} transactions')
    for tx_hash in transactions_hashes:
        transactions_list.append(transactions_collection.find_one({'_id': bson.Binary(tx_hash)}))

    block_numbers = [transaction['block_number'] for transaction in transactions_list]
    block_numbers = sorted(set(block_numbers))

    print(block_numbers)

    result_data = {}
    for block_number in block_numbers:
        result_data[str(block_number)] = blocks_collection.find_one({'_id': block_number})

    for block_number in result_data:

        block_data = result_data[block_number]

        block_data['transactions'] = {}

        txs_of_current_block = filter(lambda tx: tx['block_number'] == block_data['_id'], transactions_list)
        for tx in txs_of_current_block:
            block_data['transactions'][f'0x{tx["_id"].hex()}'] = {'tx': tx, 'show_traces': False}

        for tx_hash in block_data['transactions']:

            transaction = block_data['transactions'][tx_hash]['tx']
            tx_hash = transaction['_id']

            initial_from_traces_of_current_tx = list(filter(
                lambda trace: trace['transaction_hash'] == bson.Binary(tx_hash),
                traces_from_list))
            
            initial_to_traces_of_current_tx = list(filter(
                lambda trace: trace['transaction_hash'] == bson.Binary(tx_hash),
                traces_to_list))

            initial_from_trace_addresses_list = [trace['trace_address'] for trace in initial_from_traces_of_current_tx] # [[], []]
            initial_to_trace_addresses_list = [trace['trace_address'] for trace in initial_to_traces_of_current_tx]

            shorten_initial_from_trace_addresses(initial_from_trace_addresses_list)
            shorten_initial_to_trace_addresses(initial_to_trace_addresses_list)

            all_traces_from_current_tx_cursor = traces_collection.find({'transaction_hash': tx_hash})

            all_traces_from_current_tx_list = list(all_traces_from_current_tx_cursor)

            all_traces_from_current_tx_list.sort(key = cmp_to_key(compare_traces), reverse = True)

            transaction['traces_len'] = len(all_traces_from_current_tx_list)
            transaction['from'] = all_traces_from_current_tx_list[0]['from']
            transaction['to'] = all_traces_from_current_tx_list[0]['to']

            min_ta_from_len = len(initial_from_trace_addresses_list[0]) if (len(initial_from_trace_addresses_list) > 0) else 0
            max_ta_from_len = len(initial_from_trace_addresses_list[-1]) if (len(initial_from_trace_addresses_list) > 0) else 0

            max_ta_to_len = len(initial_to_trace_addresses_list[0]) if (len(initial_to_trace_addresses_list) > 0) else 0

            marked_traces_from_current_tx = []

            for trace in all_traces_from_current_tx_list:
                del trace['_id']
                marked_traces_from_current_tx.append(
                    {
                        "trace": trace,
                        "after_from": after_from(trace['trace_address'], initial_from_trace_addresses_list, min_ta_from_len, max_ta_from_len),
                        "before_to": before_to(trace['trace_address'], initial_to_trace_addresses_list, max_ta_to_len)
                    })
                
            transaction['traces'] = marked_traces_from_current_tx
            
    for block_number in result_data:
        block_data = result_data[block_number]
        parse_data(block_data)
        for tx_hash in block_data['transactions']:
            tx_data = block_data['transactions'][tx_hash]
            parse_data(tx_data['tx'])
            for trace_data in tx_data['tx']['traces']:
                parse_data(trace_data['trace'])

    return result_data
