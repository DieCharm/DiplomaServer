from django_unicorn.components import UnicornView
from home.models import Transaction, Trace
import enum
import bson
import pymongo
from home.utils.parse_data import parse_data

class Network(enum.Enum):
    ETH = 'Ethereum'
    BSC = 'BSC'

class HomeView(UnicornView):
    network = Network.ETH
    transactions = []
    traces = []

    prev_from = ''
    prev_to = ''

    def load_data(self, from_addr_str, to_addr_str, begin_date, end_date):
        print('load_data')
        if (len(from_addr_str) == 0 and len(to_addr_str) == 0):
            return
        
        if (from_addr_str == self.prev_from and to_addr_str == self.prev_to):
            return
        
        self.prev_from = from_addr_str
        self.prev_to = to_addr_str

        from_addr = bson.Binary(bytearray.fromhex(from_addr_str))
        to_addr = bson.Binary(bytearray.fromhex(to_addr_str))
        mongo = pymongo.MongoClient('mongodb://localhost:27017')
        db = mongo[self.network.value]
        traces_collection = db["Traces"]
        transactions_collection = db["Transactions"]

        mongo_query = {}
        if (len(from_addr_str) >= 40):
            mongo_query['from'] = from_addr
        if (len(to_addr_str) >= 40):
            mongo_query['to'] = to_addr

        print(mongo_query)

        # traces_cursor = traces_collection.find(mongo_query)

        # traces_list = [trace for trace in traces_cursor]
        # print(f'{len(traces_list)} traces')

        # transactions_hashes = [trace['transaction_hash'] for trace in traces_list]
        # transactions_hashes = set(transactions_hashes)
        # transactions_list = []
        # print(f'{len(transactions_hashes)} transactions')
        # for tx_hash in transactions_hashes:
        #     transactions_list.append(transactions_collection.find_one({'_id': bson.Binary(tx_hash)}))

        # for trace in traces_list:
        #     parse_data(trace)
        # for transaction in transactions_list:
        #     parse_data(transaction)

        # self.traces = traces_list
        # self.transactions = transactions_list