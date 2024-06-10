import pandas
from statsmodels.tsa.seasonal import STL

def get_interval_key(timestamp, seasonal):
    return (timestamp // seasonal) * seasonal

def prioritize_counterparties(data, from_address, seasonal, period):

    traces_input = []

    for block_number in data:
        block_data = data[block_number]
        for tx_hash in block_data['transactions']:
            tx_data = block_data['transactions'][tx_hash]
            #додаємо лише ті трейси де перший виклик був від адреси відправника
            # оскільки відправник встановлює ціну на гас
            if ('from' in tx_data['tx']['traces'][0]['trace'].keys()
                and tx_data['tx']['traces'][0]['trace']['from'].upper() == from_address.upper()):
                for trace_data in tx_data['tx']['traces']:
                    if('gas_used' in trace_data['trace'].keys()
                        and 'to' in trace_data['trace'].keys()
                        and 'gas_price' in tx_data['tx'].keys()):
                        traces_input.append({
                            'address': trace_data['trace']['to'],
                            'price_of_gas_used': int((
                                trace_data['trace']['gas_used']
                                * (
                                    tx_data['tx']['gas_price']
                                + (
                                    tx_data['tx']['max_priority_fee_per_gas']
                                    if ('max_priority_fee_per_gas' in tx_data['tx'].keys())
                                    else 0)
                                    )
                                    / (10 ** 9))), # result in gwei
                            'timestamp': block_data['timestamp']
                        })
                        if (trace_data['trace']['to'].upper() == '0x844eb5c280f38c7462316aad3f338ef9bda62668'.upper()):
                            print(f"{traces_input[-1]['timestamp']}: {traces_input[-1]['price_of_gas_used']}")

    print([(el['timestamp'], el['price_of_gas_used']) for el in sorted(filter(lambda ti: ti['address'].upper() == '0x844eb5c280f38c7462316aad3f338ef9bda62668'.upper(), traces_input), key = lambda ti: ti['timestamp'])])

    counterparty_gas_usage = {}
    counterparty_interactions_count = {}

    for trace in traces_input:
        counterparty = trace['address']
        timestamp = trace['timestamp']
        season_key = get_interval_key(timestamp, seasonal)

        if (counterparty.upper() != from_address.upper()):

            if counterparty not in counterparty_gas_usage:
                counterparty_gas_usage[counterparty] = {}

            if season_key not in counterparty_gas_usage[counterparty]:
                counterparty_gas_usage[counterparty][season_key] = 0

            counterparty_gas_usage[counterparty][season_key] += trace['price_of_gas_used']

            if counterparty not in counterparty_interactions_count:
                counterparty_interactions_count[counterparty] = 0
            
            counterparty_interactions_count[counterparty] += 1
    # Сезонна декомпозиція та обчислення відхилень
    counterparty_deviations = {}
    for counterparty, usage in counterparty_gas_usage.items():
        sorted_usage = sorted(usage.items())
        time_series = pandas.Series([u[1] for u in sorted_usage], index=[u[0] for u in sorted_usage])

        # Виконання алгоритму сезонної декомпозиції
        stl = STL(time_series, period = period) # , seasonal = interval
        result = stl.fit()
        residual = result.resid
        deviations = residual.abs().tolist()
        counterparty_deviations[counterparty] = deviations
        if (counterparty.upper() == '0x844eb5c280f38c7462316aad3f338ef9bda62668'.upper()):
            print(f'time series for {counterparty}')
            print(sorted(time_series.items()))
            print(f'trend for {counterparty}')
            print(result.trend)
            print(f'seasonal for {counterparty}')
            print(result.seasonal)
            print(f'resid for {counterparty}')
            print(residual)
            print(f'deviations for {counterparty}')
            print(deviations)

    # Пріорітизація смарт-контрактів
    counterparty_priorities = []
    for counterparty, deviations in counterparty_deviations.items():
        total_gas_used = sum(counterparty_gas_usage[counterparty].values())
        max_deviation = sum(deviations)
        max_deviation_percent = round((max_deviation / total_gas_used) * 100, 2) if (total_gas_used != 0 and max_deviation != 0) else 0
        if (counterparty.upper() == '0x844eb5c280f38c7462316aad3f338ef9bda62668'.upper()):
            print(f'total gas price: {total_gas_used}')
            print(f'deviations sum: {max_deviation}')
            print(f'deviations percent: {max_deviation_percent}')
        counterparty_priorities.append({
            'address': counterparty,
            'total_gas_used_price': total_gas_used,
            'interactions_count': counterparty_interactions_count[counterparty],
            'max_deviation': max_deviation_percent})

    # Сортування за критеріями
    prioritized_counterparties = sorted(counterparty_priorities, key = lambda cp: (
        -cp['total_gas_used_price'],
        -cp['interactions_count'],
        -cp['max_deviation']))

    return prioritized_counterparties