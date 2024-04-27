# if there are for instance [0, 2], [0, 2, 1] addresses from - we remove [0, 2]

def shorten_initial_from_trace_addresses(initial_traces_addresses_from):

    initial_traces_addresses_from.sort(key = lambda trace_addresses: len(trace_addresses))

    for i in range(len(initial_traces_addresses_from)):
        j = i + 1
        while (j < len(initial_traces_addresses_from)):
            if (initial_traces_addresses_from[j][0 : len(initial_traces_addresses_from[i])] == initial_traces_addresses_from[i]):
                del initial_traces_addresses_from[j]
            else:
                j += 1