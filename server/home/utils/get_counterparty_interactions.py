import pandas

def get_counterparty_interactions(data, from_address, to_address, token_addresses):

    for token_addr in token_addresses:
        token_addr = token_addr.upper()

    def filter_address(address):
        return address.upper() != from_address.upper() and address.upper() != to_address.upper() and address.upper() not in token_addresses
    
    # спочатку беремо унікальні адреси контрактів, до яких звертались за транзакціями
    # потім об'єднуємо в один масив для агрегації та розрахунків

    trace_for_metrics_by_tx = {}
    addresses_for_metrics = []

    for block_number in data:
        block_data = data[block_number]
        for tx_hash in block_data['transactions']:
            tx_data = block_data['transactions'][tx_hash]
            trace_for_metrics_by_tx[tx_hash] = []
            for trace_data in tx_data['tx']['traces']:
                if (trace_data['after_from'] == True and trace_data['before_to'] == True):
                    trace_for_metrics_by_tx[tx_hash].extend([trace_data['trace']['from'], trace_data['trace']['to']])

    for tx_hash in trace_for_metrics_by_tx.keys():
        trace_for_metrics_by_tx[tx_hash] = list(set(trace_for_metrics_by_tx[tx_hash]))
        addresses_for_metrics.extend(trace_for_metrics_by_tx[tx_hash])

    addresses_for_metrics = list(filter(filter_address, addresses_for_metrics))

    transfers_df = pandas.DataFrame(data = addresses_for_metrics, columns = ['address'])
    if (transfers_df.size > 0):
        transfers_df = transfers_df.groupby('address').size()
    result_df = transfers_df.reset_index()
    result_list = result_df.values.tolist()
    result_list.sort(key = lambda addr_count_pair: addr_count_pair[1])

    return (
        [addr_count_pair[0] for addr_count_pair in result_list],
        [addr_count_pair[1] for addr_count_pair in result_list]
        )
