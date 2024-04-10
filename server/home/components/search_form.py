from django_unicorn.components import UnicornView
from django import forms
from django.core.exceptions import ValidationError
from datetime import datetime

def validate_address(address_input):
    if (not (address_input[0:2] == '0x' and len(address_input) == 42)
        and not (address_input[0:2] != '0x' and len(address_input) == 40)):
            raise ValidationError('Invalid address. Please input account address that begins with "0x" and contains 42 symbols')

def validate_date(datetime_input):
    input_timestamp = datetime.timestamp(datetime_input)
    if (input_timestamp < 1702598399 or input_timestamp > 19008564):
         raise ValidationError('Unfortunately, operations from this period are not available')      

class SearchForm(forms.Form):
    from_address = forms.CharField(max_length=42, required=False, validators = [validate_address])
    to_address = forms.CharField(max_length=42, required=False, validators = [validate_address])
    begin_date = forms.DateTimeField(required=False, )
    end_date = forms.DateTimeField(required=False, )
    only_direct = forms.BooleanField(label = 'In case of inspecting outgoing transactions take into account in the analysis only direct calls (select), or both direct and internal (unselect)')

class SearchFormView(UnicornView):

    form_class = SearchForm
    
    from_address = ''
    to_address = ''
    begin_date = ''
    end_date = ''
    only_direct = False

    def updated_from_address(self, prompt):
        print(f'UPDATED FROM {prompt}')

    def updated(self, from_addr, to_addr):
        print(f'UPDATED: {self.from_address}, {self.to_address}, {self.only_direct}, {self.begin_date}, {self.end_date}')
        if (self.is_valid()):
            if (self.from_address[0:2] == '0x'):
                self.from_address = self.from_address[2:]
            if (self.to_address[0:2] == '0x'):
                self.to_address = self.to_address[2:]
            if (len(self.from_address) == 0 and len(self.to_address) == 0):
                return
            self.parent.load_data(self.from_address, self.to_address, self.begin_date, self.end_date)
            self.parent.force_render = True
