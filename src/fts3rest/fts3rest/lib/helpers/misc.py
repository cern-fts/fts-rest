
def timedelta_to_seconds(td):
    """
    Returns timedelta td total number of seconds
    """
    return (td.microseconds + (td.seconds + td.days * 24 * 3600) * 10**6) / 10**6


def average(iterable, start=None, transform=None):
    """
    Returns the average, or None if there are no elements
    """
    if len(iterable):
        if start is not None:
            addition = sum(iterable, start)
        else:
            addition = sum(iterable)
        if transform:
            addition = transform(addition)
        return addition / float(len(iterable))
    else:
        return None
