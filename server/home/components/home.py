from django_unicorn.components import UnicornView
from home.utils.load_data_from_db import load_data_from_db
from home.utils.validate_address import validate_address
from home.utils.timestamp_from_datetime_str import timestamp_from_datetime_str
from home.utils.validate_date import validate_date

class HomeView(UnicornView):

    networks = ['Ethereum', 'BSC'] 
    
    network = networks[0]
    blocks = []
    transactions = []
    traces = []

    filtered_blocks = []
    filtered_transactions = []
    filtered_traces = []

    from_address = ''
    from_address_valid = True

    to_address = ''
    to_address_valid = True

    begin_date = '2023-12-14T23:59'
    begin_date_timestamp = timestamp_from_datetime_str(begin_date)
    begin_date_valid = True

    end_date = '2024-01-14T23:59'
    end_date_timestamp = timestamp_from_datetime_str(end_date)
    end_date_valid = True

    def validate_load_request(self):

        if (len(self.from_address) == 0 and len(self.to_address) == 0
            or not (self.from_address_valid and self.to_address_valid
                 and self.begin_date_valid and self.end_date_valid)):
            print('not validated')
            return
        
        else:
            print('validated')
            self.load_data()
            

    def load_data(self):

        print('loading data')

        (self.blocks,
         self.transactions,
         self.traces) = load_data_from_db(self.network,
                                          self.from_address,
                                          self.to_address)

        print('loaded')
        print(f'traces: {len(self.traces)}')
        print(f'txs: {len(self.transactions)}')
        print(f'blocks: {len(self.blocks)}')
        
        self.filter_data()

    
    def filter_data(self):

        filtered = False

        print(f'self.begin_date_timestamp: {self.begin_date_timestamp}, self.end_date_timestamp: {self.end_date_timestamp}')


        if (self.begin_date_valid and int(float(self.begin_date_timestamp)) > 1702598340):
            filtered = True
            self.filtered_blocks = list(filter(lambda block: int(block['timestamp']) >= int(float(self.begin_date_timestamp)), self.blocks))
            self.filter_by_block_numbers()
            
        if (self.end_date_valid and int(float(self.end_date_timestamp)) < 1705276740):
            filtered = True
            self.filtered_blocks = list(filter(lambda block: int(block['timestamp']) <= int(float(self.end_date_timestamp)), self.blocks))
            self.filter_by_block_numbers()

        if not filtered:
            (self.filtered_blocks,
            self.filtered_transactions,
            self.filtered_traces) = (self.blocks,
                                    self.transactions,
                                    self.traces)

        self.force_render = True

        print('filtered')
        print(f'traces: {len(self.filtered_traces)}')
        print(f'txs: {len(self.filtered_transactions)}')
        print(f'blocks: {len(self.filtered_blocks)}')

 
    def filter_by_block_numbers(self):
        print('filter_by_block_numbers')
        filtered_block_numbers = frozenset([block['id'] for block in self.filtered_blocks])
        self.filtered_transactions = list(filter(lambda tx: tx['block_number'] in filtered_block_numbers, self.transactions))
        filtered_tx_hashes = frozenset([tx['id'] for tx in self.filtered_transactions])
        self.filtered_traces = list(filter(lambda trace: trace['trace']['transaction_hash'] in filtered_tx_hashes, self.traces))


    def count_metrics(self):
        print('count metrix')


    def updated_from_address(self, prompt):
        self.from_address_valid = validate_address(prompt)

    def updated_to_address(self, prompt):
        self.to_address_valid = validate_address(prompt)

    def updated_begin_date(self, prompt):
        self.begin_date_timestamp = timestamp_from_datetime_str(prompt)
        self.begin_date_valid = validate_date(self.begin_date_timestamp)
        if (self.begin_date_valid):
            self.filter_data()

    def updated_end_date(self, prompt):
        self.end_date_timestamp = timestamp_from_datetime_str(prompt)
        self.end_date_valid = validate_date(self.end_date_timestamp)
        if (self.end_date_valid):
            self.filter_data()


    def updated_network(self, prompt):
        # save to cache
        # clear all filters
        pass