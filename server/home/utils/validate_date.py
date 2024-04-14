from datetime import datetime

def validate_date(datetime_prompt):
    try:
        prompt_timestamp = datetime.timestamp(datetime_prompt)
        return (prompt_timestamp >= 1702598399 or prompt_timestamp <= 19008564) 
    except:
        return False