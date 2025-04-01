from datetime import datetime, timedelta, time
import pytz


def get_current_time(timezone='UTC'):
    """Get current time in specified timezone"""
    try:
        tz = pytz.timezone(timezone)
        return datetime.now(tz)
    except pytz.exceptions.UnknownTimeZoneError:
        # Fallback to UTC if timezone is invalid
        return datetime.now(pytz.UTC)


def format_datetime(dt, format_str='%Y-%m-%d %H:%M:%S'):
    """Format a datetime object as string"""
    return dt.strftime(format_str)


def parse_datetime(datetime_str, format_str='%Y-%m-%d %H:%M:%S'):
    """Parse a datetime string into a datetime object"""
    try:
        return datetime.strptime(datetime_str, format_str)
    except ValueError:
        return None


def get_day_of_week(dt=None):
    """Get day of week from datetime object or current date"""
    if dt is None:
        dt = datetime.now()
    return dt.strftime('%A')  # Monday, Tuesday, etc.


def time_in_range(start_time_str, end_time_str, check_time_str=None):
    """Check if the current time is within a specified range"""
    try:
        # Parse time strings in HH:MM format
        start_time = datetime.strptime(start_time_str, '%H:%M').time()
        end_time = datetime.strptime(end_time_str, '%H:%M').time()
        
        # Use current time if not provided
        if check_time_str is None:
            check_time = datetime.now().time()
        else:
            check_time = datetime.strptime(check_time_str, '%H:%M').time()
        
        # Handle overnight ranges (e.g., 22:00 to 06:00)
        if start_time <= end_time:
            return start_time <= check_time <= end_time
        else:
            return check_time >= start_time or check_time <= end_time
    except ValueError:
        return False