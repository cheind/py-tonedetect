
from datetime import datetime

def pretty_size(num, suffix='Bytes'):
    """Pretty print sizes using human readable units.
    http://stackoverflow.com/questions/1094841/reusable-library-to-get-human-readable-version-of-file-size
    """
    for unit in ['','Ki','Mi','Gi','Ti','Pi','Ei','Zi']:
        if abs(num) < 1024.0:
            return "%3.1f%s%s" % (num, unit, suffix)
        num /= 1024.0
    return "%.1f%s%s" % (num, 'Yi', suffix)

def pretty_date(time=False, suffix="ago"):
    """Pretty print time and dates.
    http://stackoverflow.com/questions/1551382/user-friendly-time-format-in-python
    """
    
    now = datetime.now()
    if type(time) is int:
        diff = now - datetime.fromtimestamp(time)
    elif isinstance(time,datetime):
        diff = now - time
    elif not time:
        diff = now - now
    second_diff = diff.seconds
    day_diff = diff.days

    if day_diff < 0:
        return ''

    if day_diff == 0:
        if second_diff < 10:
            return "just now"
        if second_diff < 60:
            return str(second_diff) + " seconds" + suffix
        if second_diff < 120:
            return "a minute"
        if second_diff < 3600:
            return "{:.2f} minutes".format(second_diff / 60) + suffix
        if second_diff < 7200:
            return "an hour"
        if second_diff < 86400:
            return "{:.2f} hours".format(second_diff / 3600) + suffix
    if day_diff == 1:
        return "Yesterday"
    if day_diff < 7:
        return str(day_diff) + " days" + suffix
    if day_diff < 31:
        return str(day_diff / 7) + " weeks" + suffix
    if day_diff < 365:
        return str(day_diff / 30) + " months" + suffix
    return str(day_diff / 365) + " years" + suffix