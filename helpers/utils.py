from datetime import datetime
import time


def get_formatted_time(timestamp):
    date_time = datetime.fromtimestamp(timestamp)
    return date_time