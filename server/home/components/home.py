from django_unicorn.components import UnicornView
from home.utils.load_data_from_db import load_data_from_db
from home.utils.validate_address import validate_address
from home.utils.timestamp_from_datetime_str import timestamp_from_datetime_str
from home.utils.validate_date import validate_date

class HomeView(UnicornView):

    networks = ['Ethereum', 'BSC'] 
    
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
        self.data = load_data_from_db(self.network,
                                      self.from_address,
                                      self.to_address)
        self.filter_data() 

    
    def filter_data(self):

        filtered = False

        if (self.begin_date_valid and int(float(self.begin_date_timestamp)) > 1702598340):
            filtered = True
            self.filtered_data = list(filter(lambda block_data: int(block_data['timestamp']) >= int(float(self.begin_date_timestamp)), self.data))
            
        if (self.end_date_valid and int(float(self.end_date_timestamp)) < 1705276740):
            filtered = True
            self.filtered_data = list(filter(lambda block_data: int(block_data['timestamp']) <= int(float(self.end_date_timestamp)), self.data))

        if not filtered:
            self.filtered_data = self.data

        self.force_render = True

        self.count_metrics()

        print(f'filtered: {filtered}')


    def count_metrics(self):
        print('count metrix')

        

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
        self.force_render = True


    def updated_network(self, prompt):
        # save to cache
        # clear all filters
        pass