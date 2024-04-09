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

    def mount(self):
        self.load_data('3183FCDE405cD3Ef0A0D4aB995Ddd4Ce1aeC51A3')

    def load_data(self, address_str):
        address = bson.Binary(bytearray.fromhex(address_str))
        mongo = pymongo.MongoClient('mongodb://localhost:27017')
        db = mongo[self.network.value]
        traces_collection = db["Traces"]
        transactions_collection = db["Transactions"]

        traces_cursor = traces_collection.find({'from': address})
        traces_list = [trace for trace in traces_cursor]
        print(f'{len(traces_list)} traces')

        transactions_hashes = [trace['transaction_hash'] for trace in traces_list]
        transactions_hashes = set(transactions_hashes)
        transactions_list = []
        print(f'{len(transactions_hashes)} transactions')
        for tx_hash in transactions_hashes:
            transactions_list.append(transactions_collection.find_one({'_id': bson.Binary(tx_hash)}))

        for trace in traces_list:
            parse_data(trace)
        for transaction in transactions_list:
            parse_data(transaction)

        self.traces = traces_list
        self.transactions = transactions_list