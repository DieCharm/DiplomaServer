from django_unicorn.components import UnicornView
from django import forms
from django.core.exceptions import ValidationError

def validate_address(address_input):
    if (not (address_input[0:2] == '0x' and len(address_input) == 42)
        and not (address_input[0:2] != '0x' and len(address_input) == 40)):
            raise ValidationError('Invalid address. Please input account address that begins with "0x" and contains 42 symbols')

class SearchForm(forms.Form):
    from_address = forms.CharField(max_length=42, required=False, validators = [validate_address])
    to_address = forms.CharField(max_length=42, required=False, validators = [validate_address])
    only_direct = forms.BooleanField()
    begin_date = forms.DateField()
    end_date = forms.DateField()
    publish_date = forms.DateField(required=True)

class SearchFormView(UnicornView):

    form_class = SearchForm
    
    from_address = ''
    to_address = ''
    only_direct = True
    begin_date = ''
    end_date = ''
    invalid = False

    def updated_address(self, query):
        if ((query[0:2] == '0x' and len(query) == 42)
            or (query[0:2] != '0x' and len(query) == 40)):

            self.invalid = False
            if (query[0:2] == '0x'):
                query = query[2:]
            self.parent.load_data(query)
            self.parent.force_render = True

        else:
            self.invalid = True