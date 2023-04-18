from datetime import timedelta


def calculate_uptime_downtime_last_week(business_hours, poll_data):
    uptime_last_week = 0
    downtime_last_week = 0

    # Iterate over the business hours of the store and only consider the status that fall within the business hours
    for date in business_hours:
        for opening_time, closing_time in business_hours[date]:
            filtered_data = [(ts, status) for ts, status in poll_data if
                             opening_time <= ts < closing_time]
            # If there is no data for the business hours, assume the store is active and inactive equally over the
            # business hours
            if not filtered_data:
                uptime_last_week += (closing_time - opening_time).total_seconds() / 2
                downtime_last_week += (closing_time - opening_time).total_seconds() / 2
            else:
                prev_ts, prev_status = filtered_data[0]
                uptime_last_week += (prev_ts - opening_time).total_seconds() if prev_status == 'active' else 0
                downtime_last_week += (prev_ts - opening_time).total_seconds() if prev_status == 'inactive' else 0
                for ts, status in filtered_data[1:]:
                    if status == 'active' and prev_status == 'active':
                        uptime_last_week += (ts - prev_ts).total_seconds()
                    elif status == 'active' and prev_status == 'inactive':
                        uptime_last_week += (ts - prev_ts).total_seconds() / 2
                        downtime_last_week += (ts - prev_ts).total_seconds() / 2
                    elif status == 'inactive' and prev_status == 'active':
                        uptime_last_week += (ts - prev_ts).total_seconds() / 2
                        downtime_last_week += (ts - prev_ts).total_seconds() / 2
                    elif status == 'inactive' and prev_status == 'inactive':
                        downtime_last_week += (ts - prev_ts).total_seconds()
                    prev_ts = ts
                    prev_status = status

                # add the time between the last poll and the closing time
                if prev_status == 'active':
                    uptime_last_week += (closing_time - prev_ts).total_seconds()
                else:
                    downtime_last_week += (closing_time - prev_ts).total_seconds()

    # return as hours
    return uptime_last_week / 3600, downtime_last_week / 3600


def calculate_uptime_downtime_last_day(business_hours, poll_data):
    uptime_last_day = 0
    downtime_last_day = 0
    last_working_day = list(business_hours)[-1]

    # Iterate over last day's business hours of the store and only consider the status between those hours
    for opening_time, closing_time in business_hours[last_working_day]:
        filtered_data = [(ts, status) for ts, status in poll_data if
                         opening_time <= ts < closing_time]
        # If there is no data for the business hours, assume the store was active and inactive equally over the
        # business hours
        if not filtered_data:
            uptime_last_day += (closing_time - opening_time).seconds / 2
            downtime_last_day += (closing_time - opening_time).seconds / 2
        else:
            prev_ts, prev_status = filtered_data[0]
            uptime_last_day += (prev_ts - opening_time).total_seconds() if prev_status == 'active' else 0
            downtime_last_day += (prev_ts - opening_time).total_seconds() if prev_status == 'inactive' else 0
            for ts, status in filtered_data[1:]:
                if status == 'active' and prev_status == 'active':
                    uptime_last_day += (ts - prev_ts).total_seconds()
                elif status == 'active' and prev_status == 'inactive':
                    uptime_last_day += (ts - prev_ts).total_seconds() / 2
                    downtime_last_day += (ts - prev_ts).total_seconds() / 2
                elif status == 'inactive' and prev_status == 'active':
                    uptime_last_day += (ts - prev_ts).total_seconds() / 2
                    downtime_last_day += (ts - prev_ts).total_seconds() / 2
                elif status == 'inactive' and prev_status == 'inactive':
                    downtime_last_day += (ts - prev_ts).total_seconds()
                prev_ts = ts
                prev_status = status

            # Add the time between the last poll and the closing time
            if prev_status == 'active':
                uptime_last_day += (closing_time - prev_ts).total_seconds()
            else:
                downtime_last_day += (closing_time - prev_ts).total_seconds()

    # return as minutes
    return uptime_last_day / 60, downtime_last_day / 60


def calculate_uptime_downtime_last_hour(business_hours, poll_data):
    uptime_last_hour = 0
    downtime_last_hour = 0

    time_iterated = 0
    last_business_hour = []
    flag = False
    # Iterate over the business hours in reverse order and find out the last 1 hour of business hours
    for date in reversed(business_hours):
        if flag:
            break
        for opening_time, closing_time in reversed(business_hours[date]):
            if closing_time - opening_time >= (timedelta(hours=1) - timedelta(seconds=time_iterated)):
                # If the range of business hours is greater than the remaining time out of 1 hour,
                # then this completes the last 1 hour of business hours
                last_business_hour.append(
                    (closing_time - (timedelta(hours=1) - timedelta(seconds=time_iterated)), closing_time))
                flag = True
                break
            else:
                # If the business hours are less than 1 hour, then append these business hours to the last business
                # hours
                time_iterated += (closing_time - opening_time).total_seconds()
                last_business_hour.append([opening_time, closing_time])
    # Reverse the list to get the last business hours in the correct order
    last_business_hour.reverse()
    # Iterate over the last business hours and only consider the status that fall within the business hours similar
    # to other methods above
    for opening_time, closing_time in last_business_hour:
        filtered_data = [(ts, status) for ts, status in poll_data if opening_time <= ts < closing_time]
        # If there is no data for the business hours, assume the store is active and inactive equally over the
        # business hours
        if not filtered_data:
            uptime_last_hour += (closing_time - opening_time).total_seconds() / 2
            downtime_last_hour += (closing_time - opening_time).total_seconds() / 2
        else:
            prev_ts, prev_status = filtered_data[0]
            uptime_last_hour += (prev_ts - opening_time).total_seconds() if prev_status == 'active' else 0
            downtime_last_hour += (prev_ts - opening_time).total_seconds() if prev_status == 'inactive' else 0
            for ts, status in filtered_data[1:]:
                if status == 'active' and prev_status == 'active':
                    uptime_last_hour += (ts - prev_ts).total_seconds()
                elif status == 'active' and prev_status == 'inactive':
                    uptime_last_hour += (ts - prev_ts).total_seconds() / 2
                    downtime_last_hour += (ts - prev_ts).total_seconds() / 2
                elif status == 'inactive' and prev_status == 'active':
                    uptime_last_hour += (ts - prev_ts).total_seconds() / 2
                    downtime_last_hour += (ts - prev_ts).total_seconds() / 2
                elif status == 'inactive' and prev_status == 'inactive':
                    downtime_last_hour += (ts - prev_ts).total_seconds()
                prev_ts = ts
                prev_status = status

            # add the time between the last poll and the closing time
            if prev_status == 'active':
                uptime_last_hour += (closing_time - prev_ts).total_seconds()
            else:
                downtime_last_hour += (closing_time - prev_ts).total_seconds()

    # return as minutes
    return uptime_last_hour / 60, downtime_last_hour / 60


def calculate_uptime_downtime(business_hours, poll_data):
    uptime_last_week, downtime_last_week = calculate_uptime_downtime_last_week(business_hours, poll_data)
    uptime_last_day, downtime_last_day = calculate_uptime_downtime_last_day(business_hours, poll_data)
    uptime_last_hour, downtime_last_hour = calculate_uptime_downtime_last_hour(business_hours, poll_data)

    return uptime_last_week, downtime_last_week, uptime_last_day, downtime_last_day, uptime_last_hour, \
        downtime_last_hour
