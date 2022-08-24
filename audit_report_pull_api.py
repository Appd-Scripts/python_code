# Get data from the Audit API and stores data in raw form into a directory
# Files created by this script are used by the other audit scripts to create the different outputs
# Dependent scripts are: audit_report_sum_from_api_by_object.py, audit_report_sum_from_api_files.py
# audit_report_sum_from_api_of_object.py

import logging
import time

from auth_mgr import AuthMgr
from datetime import datetime
from datetime import timedelta


def get_data(base_url):
    getStartDate = input("Starting Date mm/dd/yyyy (not greater than 30 days ago): ")
    getEndDate = input("Ending Date mm/dd/yyyy: ")
    delta = timedelta(days=1)
    api_url = '/controller/ControllerAuditHistory?'
    # Convert to user input to timestamp
    start_date_time_obj = datetime.strptime(getStartDate, "%m/%d/%Y")
    end_date_time_obj = datetime.strptime(getEndDate, "%m/%d/%Y")

    while start_date_time_obj <= end_date_time_obj:
        timeframe = 'startTime=' + str(start_date_time_obj.date()) + 'T00:00:00.607-0700&endTime=' + str(start_date_time_obj.date()) + 'T23:59:59.607-0700&timeZoneId=America&Denver'
        include_crit = ''
        exclude_crit = '&exclude=accountName:system'
        url = base_url + api_url + timeframe + include_crit + exclude_crit
        response = s.get(url)
        time.sleep(1)
        if response:
            response.raise_for_status()  # ensure we notice bad responses
            filename = 'audit_file_' + str(start_date_time_obj.date()) + '.json'
            file = open(filename, "w", encoding="utf-8")
            file.write(response.text)
            file.close()
            log.info("Data for " + str(start_date_time_obj.date()) + "added to " + str(filename))
        else:
            log.warning("No Data for " + str(start_date_time_obj.date()))

        start_date_time_obj += delta


# Open a session with the controller
auth = AuthMgr()
auth.login_controller()
s = auth.session
baseUrl = auth.base_url

# Logging config
log = logging.getLogger("AppD_Util")
log.setLevel(logging.DEBUG)

# create formatter and add it to the handlers
formatter = logging.Formatter(
    fmt="%(asctime)s - %(name)s:%(lineno)d - %(levelname)s - %(message)s",
    datefmt="%m-%d-%Y %H:%M:%S",
)

# create file handler which logs even debug messages
fh = logging.FileHandler(
    "api_audit_pull" + str(datetime.now().strftime("%Y%m%d")) + ".log", mode="a+"
)
fh.setLevel(logging.DEBUG)
fh.setFormatter(formatter)
log.addHandler(fh)

# create console handler with a higher log level
ch = logging.StreamHandler()
ch.setLevel(logging.DEBUG)
ch.setFormatter(formatter)
log.addHandler(ch)

# Do the work
get_data(baseUrl)
