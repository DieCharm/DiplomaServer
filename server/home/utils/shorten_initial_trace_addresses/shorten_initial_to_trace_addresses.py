# if there are for instance [0, 2], [0, 2, 1] addresses from - we remove [0, 2, 1]

def shorten_initial_to_trace_addresses(initial_traces_addresses_to):

    initial_traces_addresses_to.sort(key = lambda trace_addresses: -len(trace_addresses))

    for i in range(len(initial_traces_addresses_to)):
        j = i + 1
        while (j < len(initial_traces_addresses_to)):
            if (initial_traces_addresses_to[i][0 : len(initial_traces_addresses_to[j])] == initial_traces_addresses_to[j]):
                del initial_traces_addresses_to[j]
            else:
                j += 1