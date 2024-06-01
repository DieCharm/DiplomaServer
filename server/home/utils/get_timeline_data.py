from datetime import datetime, timedelta
import pandas

def get_timeline_data(data):

    value_sum_by_timestamps = {}

    for block_number in data:
        block_data = data[block_number]
        value_sum_by_timestamps[block_data['timestamp']] = 0
        for tx_hash in block_data['transactions']:
            tx_data = block_data['transactions'][tx_hash]
            for trace_data in tx_data['tx']['traces']:
                if (trace_data['after_from'] == True and trace_data['before_to'] == True):
                    value_sum_by_timestamps[block_data['timestamp']] += float(trace_data['trace']['value'])

    value_sum_by_dates = []

    for timestamp in value_sum_by_timestamps.keys():
        value_sum_by_dates.append([
            datetime.fromtimestamp(timestamp).date(),
            value_sum_by_timestamps[timestamp]])
        
    if (len(value_sum_by_dates) > 0):
            
        value_sum_by_dates_df = pandas.DataFrame(value_sum_by_dates, columns = ['date', 'amount'])

        dates_of_txs_df = value_sum_by_dates_df.groupby(['date']).sum()
        dates_of_txs_dict = dates_of_txs_df.to_dict()['amount']

        print(dates_of_txs_dict)

        min_date = min(dates_of_txs_dict.keys())
        max_date = max(dates_of_txs_dict.keys())

        days_count = (max_date - min_date).days + 1
        print(f'{min_date}, {max_date}, {days_count}')

        result_list = []

        for curr_date in (min_date + timedelta(days = i) for i in range(days_count)):
            result_list.append([curr_date, (dates_of_txs_dict[curr_date] / pow(10, 18)) if (curr_date in dates_of_txs_dict.keys()) else 0])

        return (
            [date_amount_pair[0] for date_amount_pair in result_list],
            [date_amount_pair[1] for date_amount_pair in result_list]
            )
    else:
        return ([],[])
    