from bisect import bisect_left, bisect_right
from datetime import timedelta


# helper function to calculate uptime and downtime over a given time period
def calculate_uptime_downtime(poll_data, opening_time, closing_time):
    uptime = downtime = 0

    # finding the index of the first and last poll that fall within the business hours using binary search
    left_index = bisect_left(poll_data, (opening_time, ''))
    right_index = bisect_right(poll_data, (closing_time, ''))
    filtered_data = poll_data[left_index:right_index]

    # If there is no data for the business hours, assume the store is active and inactive equally over the
    # business hours
    if not filtered_data:
        uptime += (closing_time - opening_time).total_seconds() / 2
        downtime += (closing_time - opening_time).total_seconds() / 2
    else:
        prev_ts, prev_status = filtered_data[0]

        # add the time between the opening time and the first poll
        uptime += (prev_ts - opening_time).total_seconds() if prev_status == 'active' else 0
        downtime += (prev_ts - opening_time).total_seconds() if prev_status == 'inactive' else 0
        for ts, status in filtered_data[1:]:
            if status == 'active' and prev_status == 'active':
                uptime += (ts - prev_ts).total_seconds()
            elif status == 'active' and prev_status == 'inactive':
                uptime += (ts - prev_ts).total_seconds() / 2
                downtime += (ts - prev_ts).total_seconds() / 2
            elif status == 'inactive' and prev_status == 'active':
                uptime += (ts - prev_ts).total_seconds() / 2
                downtime += (ts - prev_ts).total_seconds() / 2
            elif status == 'inactive' and prev_status == 'inactive':
                downtime += (ts - prev_ts).total_seconds()
            prev_ts = ts
            prev_status = status

        # add the time between the last poll and the closing time
        if prev_status == 'active':
            uptime += (closing_time - prev_ts).total_seconds()
        else:
            downtime += (closing_time - prev_ts).total_seconds()

    return uptime, downtime


def calculate_uptime_downtime_last_week(business_hours, poll_data):
    uptime_last_week = downtime_last_week = 0

    # Iterate over the business hours of the store and only consider the status that fall within the business hours
    for date in business_hours:
        for opening_time, closing_time in business_hours[date]:
            uptime, downtime = calculate_uptime_downtime(poll_data, opening_time, closing_time)
            uptime_last_week += uptime
            downtime_last_week += downtime

    # return in hours
    return round(uptime_last_week / 3600, 2), round(downtime_last_week / 3600, 2)


def calculate_uptime_downtime_last_day(business_hours, poll_data):
    uptime_last_day = downtime_last_day = 0
    last_working_day = list(business_hours)[-1]

    for opening_time, closing_time in business_hours[last_working_day]:
        uptime, downtime = calculate_uptime_downtime(poll_data, opening_time, closing_time)
        uptime_last_day += uptime
        downtime_last_day += downtime

    # return in minutes
    return round(uptime_last_day / 60, 2), round(downtime_last_day / 60, 2)


def calculate_uptime_downtime_last_hour(business_hours, poll_data):
    uptime_last_hour = downtime_last_hour = time_iterated = 0
    last_business_hour = []
    last_business_hour_found = False

    # Iterate over the business hours in reverse order and find out the last 1 hour of business hours
    for date in reversed(business_hours):
        if last_business_hour_found:
            break
        for opening_time, closing_time in reversed(business_hours[date]):
            if closing_time - opening_time >= (timedelta(hours=1) - timedelta(seconds=time_iterated)):
                # If the range of business hours is greater than the remaining time out of 1 hour,
                # then this completes the last 1 hour of business hours
                last_business_hour.append(
                    (closing_time - (timedelta(hours=1) - timedelta(seconds=time_iterated)), closing_time))
                last_business_hour_found = True
                break
            else:
                # If the business hours are less than 1 hour, then append these business hours to the last business
                # hours
                time_iterated += (closing_time - opening_time).total_seconds()
                last_business_hour.append([opening_time, closing_time])
    # Reverse the list to get the last business hours in the correct order
    last_business_hour.reverse()

    for opening_time, closing_time in last_business_hour:
        uptime, downtime = calculate_uptime_downtime(poll_data, opening_time, closing_time)
        uptime_last_hour += uptime
        downtime_last_hour += downtime

    # return in minutes
    return round(uptime_last_hour / 60, 2), round(downtime_last_hour / 60, 2)
