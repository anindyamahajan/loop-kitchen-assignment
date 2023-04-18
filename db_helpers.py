from datetime import time, timedelta, datetime

from pytz import timezone as pytz_timezone


def process_store_poll_data(query_result, store_timezone):
    # Process the query result and store the data in a list of tuples with timestamp and status
    store_poll_data = []
    for row in query_result:
        store_poll_data.append(
            (pytz_timezone(store_timezone).fromutc(row.timestamp_utc).replace(tzinfo=None), row.status))
    return store_poll_data


def process_business_hours(store_business_hours, store_timezone, curr_time):
    # Get the current date and time in the store's timezone
    local_curr_time = pytz_timezone(store_timezone).fromutc(curr_time).replace(tzinfo=None)

    business_hours = {}

    if store_business_hours:
        # Loop in reverse so that the dates are in ascending order
        for day in range(7, -1, -1):
            # Filter store_business_hours for the current day
            current_day = local_curr_time.date() - timedelta(days=day)
            store_business_hours_current_day = [entry for entry in store_business_hours if
                                                entry.day_of_week == current_day.weekday()]

            if store_business_hours_current_day:
                # Get the business hours for the current day of the week
                opening_closing_pairs = []
                for entry in store_business_hours_current_day:
                    opening_time = pytz_timezone(store_timezone).localize(
                        datetime.combine(current_day, time.fromisoformat(entry.start_time_local))).replace(
                        tzinfo=None)
                    closing_time = pytz_timezone(store_timezone).localize(
                        datetime.combine(current_day, time.fromisoformat(entry.end_time_local))).replace(
                        tzinfo=None)
                    opening_closing_pairs.append([opening_time, closing_time])
                business_hours[current_day] = opening_closing_pairs

    else:
        # If store_business_hours is empty, assume the store is open 24/7
        for day in range(7, -1, -1):
            current_day = local_curr_time.date() - timedelta(days=day)
            business_hours[current_day] = [[datetime.combine(current_day, time.min).replace(tzinfo=None),
                                            datetime.combine(current_day, time.max).replace(tzinfo=None)]]

    # should only have business hours up until the current time
    if local_curr_time.date() in business_hours:
        for i in reversed(range(len(business_hours[local_curr_time.date()]))):
            opening_closing_pair = business_hours[local_curr_time.date()][i]
            if opening_closing_pair[1] > local_curr_time:
                opening_closing_pair[1] = local_curr_time
            if opening_closing_pair[0] > local_curr_time:
                business_hours[local_curr_time.date()].remove(opening_closing_pair)

    # similar to above, should only have business hours at most 7 days ago
    if (local_curr_time.date() - timedelta(days=7)) in business_hours:
        for i in reversed(range(len(business_hours[local_curr_time.date() - timedelta(days=7)]))):
            opening_closing_pair = business_hours[local_curr_time.date() - timedelta(days=7)][i]
            if opening_closing_pair[0] < (local_curr_time - timedelta(days=7)):
                opening_closing_pair[0] = (local_curr_time - timedelta(days=7))
            if opening_closing_pair[1] < (local_curr_time - timedelta(days=7)):
                business_hours[local_curr_time.date() - timedelta(days=7)].remove(opening_closing_pair)

    return business_hours
