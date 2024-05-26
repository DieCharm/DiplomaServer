def before_to(ta, init, max_ta_len):
    if (len(init) == 0 or [] in init):
        return True
    if (len(ta) <= max_ta_len):
        for init_ta in init:
            if (len(init_ta) >= len(ta) and init_ta[0 : len(ta)] == ta):
                return True
    return False