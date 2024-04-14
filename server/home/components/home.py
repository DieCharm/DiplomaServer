from django_unicorn.components import UnicornView
import enum
from home.utils.load_data_from_db import load_data_from_db
from home.utils.validate_address import validate_address
from home.utils.validate_date import validate_date
from datetime import datetime

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
    prev_from = ''
    from_address_valid = True

    to_address = ''
    prev_to = ''
    to_address_valid = True

    begin_date = '2023-12-14T23:59'
    prev_begin_date = ''
    begin_date_valid = True

    end_date = '2024-01-14T23:59'
    prev_end_date = ''
    end_date_valid = True
 
    only_direct = False
    prev_only_direct = False 

    def updated_from_address(self, prompt):
        self.from_address_valid = validate_address(prompt)
        if (self.from_address_valid):
            self.validate_load_request()

    def updated_to_address(self, prompt):
        self.to_address_valid = validate_address(prompt)
        if (self.to_address_valid):
            self.validate_load_request()

    def updated_begin_date(self, prompt):
        self.begin_date_valid = validate_date(prompt)
        if (self.begin_date_valid):
            self.filter_data()

    def updated_end_date(self, prompt):
        self.end_date_valid = validate_date(prompt)
        if (self.end_date_valid):
            self.filter_data()

    def update_only_direct(self): 
        print('Update')

    # def updated_only_direct(self, prompt):
    #     # recount metrics
    #     pass

    def validate_load_request(self):

        if (len(self.from_address) == 0 and len(self.to_address) == 0
            or not (self.from_address_valid and self.to_address_valid
                 and self.begin_date_valid and self.end_date_valid)):
            return
        
        else:
            self.prev_from = self.from_address
            self.prev_to = self.to_address
            self.prev_begin_date = self.begin_date
            self.prev_end_date = self.end_date
            self.prev_only_direct = self.only_direct
            

    def load_data(self):

        (self.blocks,
         self.traces,
         self.transactions) = load_data_from_db(self.network,
                                                self.from_address,
                                                self.to_address)

        self.filter_data()

    
    def filter_data(self):

        begin_timestamp = 0
        try:
            begin_timestamp = datetime.timestamp(self.begin_date)
        except:
            pass

        end_timestamp = 0
        try:
            end_timestamp = datetime.timestamp(self.end_date)
        except:
            pass

        if (begin_timestamp >= 1702598399 and begin_timestamp <= 19008564):
            self.filtered_blocks = filter(lambda block: block['timestamp'] > begin_timestamp, self.blocks)
            #self.filtered_transactions = filter(lambda tx: tx[])
        if (end_timestamp >= 1702598399 and end_timestamp <= 19008564):
            self.filtered_blocks = filter(lambda block: block['timestamp'] < end_timestamp, self.blocks)

