import datetime


def is_time_in_range(start, end, now=None):
    # If now is not specified, use current time
    now = now or datetime.datetime.now().time()
    if start <= end:
        return start <= now <= end
    else:  # crosses midnight
        return start <= now or now <= end


def is_time_in_day_range(start, end, now=None):
    # If now is not specified, use current time
    now = now or datetime.datetime.now().time()

    # Convert start and end times to datetime objects for comparison
    start_dt = datetime.datetime.combine(datetime.date.today(), start)
    end_dt = datetime.datetime.combine(datetime.date.today(), end)
    now_dt = datetime.datetime.combine(datetime.date.today(), now)

    if start <= end:
        return start_dt <= now_dt <= end_dt
    else:  # crosses midnight
        return start_dt <= now_dt or now_dt <= end_dt


def is_trade_time():
    start_morning = datetime.time(9, 0)
    end_morning = datetime.time(11, 30)

    start_afternoon = datetime.time(13, 30)
    end_afternoon = datetime.time(15, 00)

    start_time = datetime.time(21, 0)  # 10:00 PM
    end_time = datetime.time(2, 0)

    return (is_time_in_range(start_morning, end_morning) or
            is_time_in_range(start_afternoon, end_afternoon) or
            is_time_in_day_range(start_time, end_time)
            )