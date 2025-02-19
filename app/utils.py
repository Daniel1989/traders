import datetime

def is_trade_time() -> bool:
    """Check if current time is trading time for futures market"""
    current_time = datetime.datetime.now().time()
    
    # Morning session: 9:00-11:30
    morning_start = datetime.time(9, 0)
    morning_end = datetime.time(11, 30)
    
    # Afternoon session: 13:30-15:00
    afternoon_start = datetime.time(13, 30)
    afternoon_end = datetime.time(15, 0)
    
    # Night session: 21:00-2:30(next day)
    night_start = datetime.time(21, 0)
    night_end = datetime.time(2, 30)
    
    is_morning = morning_start <= current_time <= morning_end
    is_afternoon = afternoon_start <= current_time <= afternoon_end
    is_night = night_start <= current_time or current_time <= night_end
    
    return is_morning or is_afternoon or is_night

def is_same_trading_day(start_time: datetime.datetime) -> bool:
    """
    Check if we're still in the same trading day
    A trading day includes the night session that extends to early next morning
    """
    current_time = datetime.datetime.now()
    
    # If we started in night session (21:00-23:59)
    if start_time.hour >= 21:
        # Continue until 2:30 next day
        if current_time.date() == start_time.date():
            return True
        if (current_time.date() - start_time.date()).days == 1 and current_time.hour < 3:
            return True
        return False
    
    # If we started in early morning session (0:00-2:30)
    if start_time.hour < 3:
        # Continue until 2:30 same day
        return current_time.date() == start_time.date() and current_time.hour < 3
    
    # If we started during regular day session
    # Continue until end of afternoon session (15:00)
    return (current_time.date() == start_time.date() and 
            (current_time.hour < 15 or 
             (current_time.hour == 15 and current_time.minute == 0))) 