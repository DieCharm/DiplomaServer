def validate_address(address_input):
    print(address_input)
    return (
        len(address_input) == 0
        or (address_input[0:2] == '0x' and len(address_input) == 42)
        or (address_input[0:2] != '0x' and len(address_input) == 40))