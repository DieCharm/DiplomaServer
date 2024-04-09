from djongo import models

class Trace(models.Model):
    subtraces        = models.IntegerField()
    # trace_address    = models.ArrayField(model_container = number) # models.IntegerField())
    transaction_hash = models.BinaryField()
    call_type        = models.CharField(db_column = 'type', max_length = 20)
    from_addr        = models.BinaryField(db_column = 'from', null = True)
    gas              = models.IntegerField(null = True)
    value            = models.DecimalField(null = True, max_digits = 36, decimal_places = 18)
    to_addr          = models.BinaryField(db_column = 'to', null = True)
    binary_input     = models.BinaryField(db_column = 'input', null = True)
    is_delegatecall  = models.BooleanField(null = True)
    is_statiscall    = models.BooleanField(null = True)
    gas_used         = models.IntegerField(null = True)
    output           = models.BinaryField(null = True)

    error            = models.CharField(null = True, max_length = 100)

    # suicide
    address          = models.BinaryField(null = True)
    refundAddress    = models.BinaryField(null = True)
    balance          = models.DecimalField(null = True, max_digits = 36, decimal_places = 18)

    # create
    result               = models.BinaryField(null = True)
    new_contract_address = models.BinaryField(null = True)


class Transaction(models.Model):
    block_number             = models.IntegerField()
    transaction_index        = models.IntegerField()
    gas                      = models.IntegerField()
    gas_price                = models.IntegerField()
    max_fee_per_gas          = models.IntegerField(null = True)
    max_priority_fee_per_gas = models.IntegerField(null = True)
    # traces              = models.ArrayField(model_container = Trace)
    