import bson
from decimal import Decimal, getcontext

def parse_data(data):
    #getcontext().prec = 1
    if ('_id' in data):
        if (isinstance(data['_id'], (int, bytes))):
            data['id'] = data['_id']
        del data['_id']
    for key in data:
        if (isinstance(data[key], bytes)):
            data[key] = f'0x{data[key].hex()}'
        if (isinstance(data[key], bson.decimal128.Decimal128)):
            data[key] = Decimal(str(data[key]))