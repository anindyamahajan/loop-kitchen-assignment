# loop-kitchen-assignment

This is a simple backend report generator application built using FastAPI and SQLite DB.

### Assumptions
We are only considering the data points that are within the business hours of the store. Based on the successive 
statuses, we are either incrementing the uptime (when both are 'active'), downtime (when both are 'inactive'), or both
equally. 

For stores which don't have business hours, we have given them an opening time of 00:00 and closing time of 
23:59:59.999999 (the last millisecond of the day) for all days. This is similar to stores which are 24x7 and have 
business hours in the DB.

For uptime and downtime in the last day, we are considering the business hours of the last working day from the 
current time. This could be the current day if it is a working day, or the last working day prior to today.

For uptime and downtime in the last hour, we are finding the last 1 hour of working hours which might be split over
multiple days also and then applying a similar logic for uptime and downtime as we have done above.
