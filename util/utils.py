import datetime

import matplotlib.pyplot as plt
import pandas as pd

from models import DailyAccount


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
    start_day = datetime.time(9, 0)
    end_day = datetime.time(10, 15)

    start_morning = datetime.time(10, 30)
    end_morning = datetime.time(11, 30)

    start_afternoon = datetime.time(13, 30)
    end_afternoon = datetime.time(15, 00)

    start_time = datetime.time(21, 0)
    end_time = datetime.time(2, 30)

    return (is_time_in_range(start_day, end_day) or
            is_time_in_range(start_morning, end_morning) or
            is_time_in_range(start_afternoon, end_afternoon) or
            is_time_in_day_range(start_time, end_time)
            )


def is_sync_time():
    start_day = datetime.time(15, 0)
    end_day = datetime.time(15, 30)

    return is_time_in_range(start_day, end_day)


def save_img(data):
    last_date = data[-1]['date'].strftime('%Y-%m-%d')
    df = pd.DataFrame(data)
    df['date'] = pd.to_datetime(df['date'])
    plt.figure(figsize=(20, 6))
    for key in df.columns:
        if key != 'date':
            plt.plot(df['date'], df[key], marker='o', label=key)

    plt.xlabel('Date')
    plt.ylabel('Values')
    plt.title('account trend')
    plt.legend()
    plt.grid(True)
    plt.savefig(last_date + '.png')
    plt.close()


def merge_lists(lists, key='date'):
    merged_dict = {}

    for lst in lists:
        for item in lst:
            item_id = item[key]
            if item_id not in merged_dict:
                merged_dict[item_id] = item
            else:
                # If the same ID exists, merge the dictionaries, prioritizing the existing fields
                for k, v in item.items():
                    if k not in merged_dict[item_id]:
                        merged_dict[item_id][k] = v

    # Convert merged_dict back to a list of dictionaries
    merged_list = list(merged_dict.values())
    return merged_list


def draw_daily_account():
    data = DailyAccount.select().order_by(DailyAccount.date)
    df = []
    current_date = None
    current_date_list = []
    for item in data:
        if current_date is None:
            current_date = item.date
        if current_date != item.date:
            df.append([item for item in current_date_list])
            current_date_list = []
            current_date = item.date
        current_date_list.append({"date": item.date, item.account_name: item.value})
    df.append([item for item in current_date_list])
    df = merge_lists(df)
    print(df)
    save_img(df)
