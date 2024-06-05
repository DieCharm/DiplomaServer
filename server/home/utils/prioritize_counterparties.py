import pandas
from statsmodels.tsa.seasonal import STL

def get_interval_key(timestamp, interval):
    return (timestamp // interval) * interval

def prioritize_counterparties(data, from_address, interval, period):

    traces_input = []

    for block_number in data:
        block_data = data[block_number]
        for tx_hash in block_data['transactions']:
            tx_data = block_data['transactions'][tx_hash]
            #додаємо лише ті трейси де перший виклик був від адреси відправника
            # оскільки відправник встановлює ціну на гас
            if (tx_data['tx']['traces'][0]['trace']['from'].upper() == from_address.upper()):
                for trace_data in tx_data['tx']['traces']:
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


    counterparty_gas_usage = {}
    counterparty_interactions_count = {}

    for trace in traces_input:
        counterparty = trace['address']
        timestamp = trace['timestamp']
        interval_key = get_interval_key(timestamp, interval)

        if (counterparty.upper() != from_address.upper()):

            if counterparty not in counterparty_gas_usage:
                counterparty_gas_usage[counterparty] = {}

            if interval_key not in counterparty_gas_usage[counterparty]:
                counterparty_gas_usage[counterparty][interval_key] = 0

            counterparty_gas_usage[counterparty][interval_key] += trace['price_of_gas_used']

            if counterparty not in counterparty_interactions_count:
                counterparty_interactions_count[counterparty] = 0
            
            counterparty_interactions_count[counterparty] += 1

    # Сезонна декомпозиція та обчислення відхилень
    counterparty_deviations = {}
    for counterparty, usage in counterparty_gas_usage.items():
        sorted_usage = sorted(usage.items())
        time_series = pandas.Series([u[1] for u in sorted_usage], index=[u[0] for u in sorted_usage])

        # Виконання алгоритму сезонної декомпозиції
        stl = STL(time_series, period = period, seasonal = interval)
        result = stl.fit()
        residual = result.resid
        deviations = residual.abs().tolist()
        counterparty_deviations[counterparty] = deviations

    # Пріорітизація смарт-контрактів
    counterparty_priorities = []
    for counterparty, deviations in counterparty_deviations.items():
        total_gas_used = sum(counterparty_gas_usage[counterparty].values())
        avg_deviation = sum(deviations) / len(deviations)
        counterparty_priorities.append({
            'address': counterparty,
            'total_gas_used_price': total_gas_used,
            'interactions_count': counterparty_interactions_count[counterparty],
            'avg_deviation': avg_deviation})

    # Сортування за критеріями
    prioritized_counterparties = sorted(counterparty_priorities, key = lambda cp: (
        -cp['total_gas_used_price'],
        -cp['interactions_count'],
        -cp['avg_deviation']))

    return prioritized_counterparties