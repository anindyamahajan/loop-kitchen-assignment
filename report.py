import csv
import os
import time

from db import get_store_poll_data, get_all_store_ids, get_store_business_hours, report_id_exists, store_report_id
from report_helpers import calculate_uptime_downtime_last_week, \
    calculate_uptime_downtime_last_day, calculate_uptime_downtime_last_hour


def generate_report(report_id: str, report_generation_semaphore):
    try:
        # Start timer
        start_time = time.perf_counter()

        # Store the report_id in the reports table
        store_report_id(report_id)

        # Get all store IDs
        store_ids = get_all_store_ids()

        # Iterate over each store and generate the report data
        report_data = []
        for store_id in store_ids:
            print(f"Processing data for store {store_id}...")

            # Get the business hours for the store
            business_hours = get_store_business_hours(store_id)

            # Get the poll data for the store
            poll_data = get_store_poll_data(store_id)

            # Calculate uptime and downtime for the store
            uptime_last_week, downtime_last_week = calculate_uptime_downtime_last_week(business_hours, poll_data)
            uptime_last_day, downtime_last_day = calculate_uptime_downtime_last_day(business_hours, poll_data)
            uptime_last_hour, downtime_last_hour = calculate_uptime_downtime_last_hour(business_hours, poll_data)

            # Add the report data to the list
            report_data.append({
                "store_id": store_id,
                "uptime_last_week": uptime_last_week,
                "downtime_last_week": downtime_last_week,
                "uptime_last_day": uptime_last_day,
                "downtime_last_day": downtime_last_day,
                "uptime_last_hour": uptime_last_hour,
                "downtime_last_hour": downtime_last_hour
            })

        # Specify the folder path
        folder_path = "reports"
        # Create the folder if it doesn't exist
        if not os.path.exists(folder_path):
            os.makedirs(folder_path)

        # Write the report data to a CSV file
        filename = os.path.join(folder_path, f"report_{report_id}.csv")
        with open(filename, "w", newline="") as csvfile:
            fieldnames = ["store_id", "uptime_last_week", "downtime_last_week", "uptime_last_day", "downtime_last_day",
                          "uptime_last_hour", "downtime_last_hour"]
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            writer.writeheader()
            for row in report_data:
                writer.writerow(row)

        # End timer
        end_time = time.perf_counter()
        print(f"Report generated in {end_time - start_time} seconds")

    except Exception as e:
        # Log the exception
        print(f"Exception occurred while generating report: {e}")

    finally:
        # Release the Semaphore after report generation is complete, even if an exception occurs
        report_generation_semaphore.release()


def report_id_valid(report_id: str):
    return report_id_exists(report_id)


def fetch_report(report_id: str):
    report_filename = os.path.join("reports", f"report_{report_id}.csv")
    if not os.path.exists(report_filename):
        return None
    return report_filename
