import requests
import json
import pandas

def get_token_transfers(min_block_number, max_block_number, from_address, to_address):
    etherscan_key = '4W9AKX112W48T91UMKIADBM73VKMKG1CPI'
    from_response_data = []
    to_response_data = []
    result_data = []
    if (len(from_address) > 0):
        url_from = f'https://api.etherscan.io/api?module=account&action=tokentx&address={from_address}&startblock={min_block_number}&endblock={max_block_number}&sort=asc&apikey={etherscan_key}'
        abi_response = requests.get(url_from)
        from_response_data = json.loads(abi_response.text)['result']
        print(f'len(from_response_data): {len(from_response_data)}')
    if (len(to_address) > 0):
        url_from = f'https://api.etherscan.io/api?module=account&action=tokentx&address={to_address}&startblock={min_block_number}&endblock={max_block_number}&sort=asc&apikey={etherscan_key}'
        abi_response = requests.get(url_from)
        to_response_data = json.loads(abi_response.text)['result']
        print(f'len(to_response_data): {len(to_response_data)}')
    if (len(from_response_data) > 0 and len(to_response_data) > 0):
        # якщо у нас зазначена початкова та кінцева адреса взаємодії - нам потрібно вивести перелік токенів, що приймали участь
        # у взаємодії цих двох адрес, тобто нас цікавлять лише ті транзакції, де приймають  участь обидві адреси
        # щоб досягти цього ми фільтруватимемо масив трансферів з адреси ініціатора за критерієм того чи містить масив
        # трансферів з адреси "отримувача" хеш поточної транзакції
        to_response_hashes = [transfer['hash'] for transfer in to_response_data]
        result_data = list(filter(lambda transfer: transfer['hash'] in to_response_hashes, from_response_data))
        print(f'filtered token interactions: {len(from_response_data)}')
    else:
        # об'єднуємо ненульовий масив із нульовим
        result_data = from_response_data + to_response_data
        
    transfers_df = pandas.DataFrame([
        {
            'token_symbol': transfer['tokenSymbol'],
            'token_name': transfer['tokenName'],
            'token_address': transfer['contractAddress']
        } for transfer in result_data])
    if (transfers_df.size > 0):
        transfers_df = transfers_df.groupby(['token_symbol', 'token_name', 'token_address']).size()
    result_df = transfers_df.reset_index()
    # [['BYTES', 'BYTES', 1], ['GSWIFT', 'GameSwift', 1], ['WILD', 'Wilder', 1], ['imgnAI', 'Image Generation AI | imgnAI.com', 2]]
    result_list = result_df.values.tolist()
    result_list.sort(reverse = True, key = lambda token_array: token_array[3])
    if (len(result_list) > 10):
        result_list = result_list[:10]
    return (
        [token_array[0] for token_array in result_list],
        [token_array[1] for token_array in result_list],
        [token_array[2] for token_array in result_list],
        [token_array[3] for token_array in result_list]
        )

