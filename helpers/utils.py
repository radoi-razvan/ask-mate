from datetime import datetime
from helpers import constants as ct
import time


def get_formatted_time(timestamp):
    date_time = datetime.fromtimestamp(timestamp)
    return date_time

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ct.ALLOWED_EXTENSIONS