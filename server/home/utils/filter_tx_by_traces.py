from home.utils.filter_traces_by import FilterTracesBy

def filter_tx_by_traces(tx_traces, filter_traces_by, from_binary, to_binary):
    if (filter_traces_by != FilterTracesBy.NONE):
        for trace in tx_traces:
            if (filter_traces_by == FilterTracesBy.FROM and trace['from'].hex() == from_binary.hex()):
                return True
            if (filter_traces_by == FilterTracesBy.TO and trace['to'].hex() == to_binary.hex()):
                return True
        return False
    else:
        return True