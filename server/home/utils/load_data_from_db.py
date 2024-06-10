import pymongo
from home.utils.filter_traces_by import FilterTracesBy
from home.utils.parse_data import parse_data
from home.utils.filter_tx_by_traces import filter_tx_by_traces
from home.utils.shorten_initial_trace_addresses.shorten_initial_from_trace_addresses import shorten_initial_from_trace_addresses
from home.utils.shorten_initial_trace_addresses.shorten_initial_to_trace_addresses import shorten_initial_to_trace_addresses
from home.utils.mark_traces.after_from import after_from
from home.utils.mark_traces.before_to import before_to
from home.utils.compare_traces import compare_traces
from functools import cmp_to_key
import bson
from datetime import datetime

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

    from_binary = bson.Binary(bytearray.fromhex(from_address_hex))
    to_binary = bson.Binary(bytearray.fromhex(to_address_hex))

    mongo_query_from = {"from": from_binary}
    traces_cursor_from = traces_collection.find(mongo_query_from)
    traces_from_count = traces_cursor_from.count()

    mongo_query_to = {"to": to_binary}
    traces_cursor_to = traces_collection.find(mongo_query_to)
    traces_to_count = traces_cursor_to.count()

    print(f'traces_from_count = {traces_from_count}, traces_to_count = {traces_to_count}')

    # load from database only smaller set of traces in order to sort it by address, which gives bigger set
    # for example we specify from address as 0x3183FCDE405cD3Ef0A0D4aB995Ddd4Ce1aeC51A3 (regular user, has ~60 traces in db)
    # and to address as 0xC02aaA39b223FE8D0A0e5C4F27eAD9083C756Cc2 (wrapped ether contract, has ~300k+ traces in db)
    # then we just load traces of regular user, get transactions by them and filter them by condition, if certain tx contains
    # trace with wrapped contract address

    if (traces_from_count == 0 or traces_to_count == 0):
        filter_traces_by = FilterTracesBy.NONE
    else:
        filter_traces_by = FilterTracesBy.FROM if (traces_from_count > traces_to_count) else FilterTracesBy.TO
    
    print(f'filter_traces_by: {filter_traces_by}')

    traces_list = []

    if (traces_from_count == 0 or traces_to_count == 0):
        if (traces_from_count > traces_to_count):
            traces_list = list(traces_cursor_from)
        else:
            traces_list = list(traces_cursor_to)
    else:
        if (traces_from_count > traces_to_count):
            traces_list = list(traces_cursor_to)
        else:
            traces_list = list(traces_cursor_from)

    print(f'loaded {len(traces_list)} traces')

    transactions_hashes = [trace['transaction_hash'] for trace in traces_list]

    transactions_hashes = frozenset(transactions_hashes)

    transactions_list = []
    print(f'{len(transactions_hashes)} transactions')
    for tx_hash in transactions_hashes:
        transactions_list.append(transactions_collection.find_one({'_id': bson.Binary(tx_hash)}))

    block_numbers = [transaction['block_number'] for transaction in transactions_list]
    block_numbers = sorted(set(block_numbers))

    result_data = {}
    for block_number in block_numbers:
        result_data[str(block_number)] = blocks_collection.find_one({'_id': block_number})

    for block_number in result_data:

        block_data = result_data[block_number]

        block_data['transactions'] = {}

        txs_of_current_block = list(filter(lambda tx: tx['block_number'] == block_data['_id'], transactions_list))
        for tx in txs_of_current_block:

            tx_hash = tx['_id']

            all_traces_from_current_tx_cursor = traces_collection.find({'transaction_hash': tx_hash})
            all_traces_from_current_tx_list = list(all_traces_from_current_tx_cursor)
            all_traces_from_current_tx_list.sort(key = cmp_to_key(compare_traces), reverse = True)

            add_tx = filter_tx_by_traces(all_traces_from_current_tx_list, filter_traces_by, from_binary, to_binary)

            # here we are filtering transaction as described above. if user specified both from and to addresses
            # we load only smaller traces and transactions set and filter it
            if (not add_tx):
                continue

            initial_from_traces_of_current_tx = list(filter(
                lambda trace: ('from' in trace.keys() and trace['from'].hex() == from_binary.hex()),
                all_traces_from_current_tx_list))

            initial_to_traces_of_current_tx = list(filter(
                lambda trace: ('to' in trace.keys() and trace['to'].hex() == to_binary.hex()),
                all_traces_from_current_tx_list))

            initial_from_trace_addresses_list = [trace['trace_address'] for trace in initial_from_traces_of_current_tx] # [[], []]
            initial_to_trace_addresses_list = [trace['trace_address'] for trace in initial_to_traces_of_current_tx]

            shorten_initial_from_trace_addresses(initial_from_trace_addresses_list)
            shorten_initial_to_trace_addresses(initial_to_trace_addresses_list)

            tx['traces_len'] = len(all_traces_from_current_tx_list)
            tx['from'] = all_traces_from_current_tx_list[0]['from']
            tx['to'] = all_traces_from_current_tx_list[0]['to']

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
                
            tx['traces'] = marked_traces_from_current_tx

            block_data['transactions'][f'0x{tx["_id"].hex()}'] = {'tx': tx, 'show_traces': False}
            
            
    for block_number in result_data:
        block_data = result_data[block_number]
        parse_data(block_data)
        for tx_hash in block_data['transactions']:
            tx_data = block_data['transactions'][tx_hash]
            parse_data(tx_data['tx'])
            tx_data['tx']['datetime'] = datetime.fromtimestamp(block_data['timestamp'])
            for trace_data in tx_data['tx']['traces']:
                parse_data(trace_data['trace'])

    return result_data
