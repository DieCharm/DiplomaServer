import requests
import json

def get_token_transfers(min_block_number, max_block_number, from_address, to_address):
    etherscan_key = '4W9AKX112W48T91UMKIADBM73VKMKG1CPI'
    transfers_of_from_address = []
    transfres_of_to_address = []
    if (len(from_address) > 0):
        url_from = f'https://api.etherscan.io/api?module=account&action=tokentx&address={from_address}&startblock={min_block_number}&endblock={max_block_number}&sort=asc&apikey={etherscan_key}'
        abi_response = requests.get(url_from)
        response_data = json.loads(abi_response.text)['result'][0]