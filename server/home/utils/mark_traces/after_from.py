def after_from(ta, init, min_ta_len, max_ta_len):
    if (len(init) == 0 or [] in init):
        return True
    if (len(ta) >= min_ta_len):
        for i in range(min_ta_len, max_ta_len + 1):
            if (ta[0 : i] in init):
                return True
    return False