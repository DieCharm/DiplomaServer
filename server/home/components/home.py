from django_unicorn.components import UnicornView
from home.utils.load_data_from_db import load_data_from_db
from home.utils.validate_address import validate_address
from home.utils.timestamp_from_datetime_str import timestamp_from_datetime_str
from home.utils.validate_date import validate_date
from home.utils.get_token_transfers import get_token_transfers
from home.utils.get_counterparty_interactions import get_counterparty_interactions
from home.utils.get_timeline_data import get_timeline_data
import pandas

class HomeView(UnicornView):

    networks = ['Ethereum', 'BSC']
    show_txs_or_countracts_options = ['Transactions', 'Contracts']
    
    show_txs_or_countracts = show_txs_or_countracts_options[0]
    network = networks[0]

    data = []

    filtered_data = []

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

    loaded = False

    token_codes = []
    token_names = []
    token_addresses = []
    token_number_of_operations = []

    counterparty_addresses = []
    counterparty_numbers_of_interactions = []

    dates = []
    value_sums = []

    def validate_load_request(self):

        if (len(self.from_address) == 0 and len(self.to_address) == 0
            or not (self.from_address_valid and self.to_address_valid
                 and self.begin_date_valid and self.end_date_valid)):
            print('not validated')
            return
        
        else:
            print('validated')
            self.loaded = False
            self.load_data()
            

    def load_data(self):
        self.data = load_data_from_db(self.network,
                                      self.from_address,
                                      self.to_address)
        print(f'loaded {len(self.data)} blocks')
        self.filter_data() 

    
    def filter_data(self):

        filtered = False
        self.filtered_data = self.data

        if (self.begin_date_valid and int(float(self.begin_date_timestamp)) > 1702598340):
            filtered = True
            self.filtered_data = dict((block_number, self.filtered_data[block_number])
                for block_number 
                in self.filtered_data.keys() 
                if (self.filtered_data[block_number]['timestamp'] >= int(float(self.begin_date_timestamp))))
            #self.filtered_data = list(filter(lambda block_data: int(block_data['timestamp']) >= int(float(self.begin_date_timestamp)), self.filtered_data))
            
        if (self.end_date_valid and int(float(self.end_date_timestamp)) < 1705276740):
            filtered = True
            self.filtered_data = dict((block_number, self.filtered_data[block_number])
                for block_number 
                in self.filtered_data.keys() 
                if (self.filtered_data[block_number]['timestamp'] <= int(float(self.end_date_timestamp))))
            
            #self.filtered_data = list(filter(lambda block_data: int(block_data['timestamp']) <= int(float(self.end_date_timestamp)), self.filtered_data))

        self.force_render = True

        self.count_metrics()

        print(f'filtered: {filtered}')


    def count_metrics(self):

        blocks_set = [int(block_number) for block_number in self.filtered_data.keys()]

        if (len(blocks_set) > 0):

            min_block_number = min(blocks_set)
            max_block_number = max(blocks_set)

            (
                self.token_codes,
                self.token_names,
                self.token_addresses,
                self.token_number_of_operations
                ) = get_token_transfers(
                    min_block_number,
                    max_block_number,
                    self.from_address,
                    self.to_address
                    )
            
            (
                self.counterparty_addresses,
                self.counterparty_numbers_of_interactions
                ) = get_counterparty_interactions(
                    self.filtered_data,
                    self.from_address,
                    self.to_address,
                    self.token_addresses)
            
            (
                self.dates,
                self.value_sums
                ) = get_timeline_data(
                    self.filtered_data)
            print(self.dates)
            print(self.value_sums)

            # here count deviation
            
            self.loaded = True
            self.call('renderGraphs')
            self.force_render = True


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


    def set_show_traces(self, block_number, tx_index_in_block):
        print(f'called with {block_number}, {tx_index_in_block}')
        for tx_data in self.filtered_data[str(block_number)]['transactions'].values():
            if(tx_data['tx']['transaction_index'] == tx_index_in_block):
                print(f'set show traces {tx_data["tx"]["id"]}')
                tx_data['show_traces'] = not tx_data['show_traces']


    # def updated_show_txs_or_countracts(self, prompt):
    #     print('change view')



    def updated_network(self, prompt):

        self.data = []

        self.filtered_data = []

        self.from_address = ''
        self.from_address_valid = True

        self.to_address = ''
        self.to_address_valid = True

        self.begin_date = '2023-12-14T23:59'
        self.begin_date_timestamp = timestamp_from_datetime_str(self.begin_date)
        self.begin_date_valid = True

        self.end_date = '2024-01-14T23:59'
        self.end_date_timestamp = timestamp_from_datetime_str(self.end_date)
        self.end_date_valid = True

        self.loaded = False

        self.token_codes = []
        self.token_names = []
        self.token_addresses = []
        self.token_number_of_operations = []

        self.counterparty_addresses = []
        self.counterparty_numbers_of_interactions = []

        self.dates = []
        self.value_sums = []