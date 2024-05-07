def compare_traces(trace1, trace2):
    if (len(trace1['trace_address']) != len(trace2['trace_address'])):
        if (len(trace1['trace_address']) < len(trace2['trace_address'])):
            return 1
        else:
            return -1
    else:
        for i in range(len(trace1['trace_address'])):
            if (trace1['trace_address'][i] < trace2['trace_address'][i]):
                return 1
            elif (trace1['trace_address'][i] > trace2['trace_address'][i]):
                return -1
    return 0