from datetime import datetime, timedelta

def next_sunday():
    today = datetime.today()
    days_ahead = (6 - today.weekday() + 7) % 7  # Sunday is 6 (Monday is 0)
    if days_ahead == 0:  # If today is Sunday, get the next one
        days_ahead = 7
    return today + timedelta(days=days_ahead)

def sunday_in_two_weeks():
    today = datetime.today()
    days_ahead = (6 - today.weekday() + 7) % 7  # Next Sunday
    next_sunday = today + timedelta(days=days_ahead)
    return next_sunday + timedelta(weeks=2)  # Add 2 weeks