from datetime import datetime

def validate_date(timestamp_prompt):
    return (timestamp_prompt >= 1702598340 and timestamp_prompt <= 1705276799)