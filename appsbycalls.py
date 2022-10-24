#!/usr/bin/python
#
# Python script to output list of all applications on a controller along with the number of calls
# to each application over the last 24 hours (sorted by decreasing number of calls).
#
# Can be used as a starting point for any sort of metric retrieval of  metrics via REST w/Python.
import json
import sys
import logging
import csv

from datetime import date
from datetime import datetime
from auth_mgr import AuthMgr


def get_metrics(host):
    compare_type = int(input("Call applications by name (1) or ID (2) - default is ID:?\n" or 2))

    # The various controller URLs to retrieve particular pieces of data
    getAppsPath = "/controller/rest/applications?output=JSON"
    getCallsPath1 = "/controller/rest/applications/"
    getCallsPath2 = "/metric-data?metric-path=Overall%20Application%20Performance%7CCalls%20per%20Minute"
    getCallsPath3 = "&time-range-type=BEFORE_NOW&duration-in-mins=43800&output=JSON"

    # Get List of Applications
    response = s.get(host + getAppsPath)

    if response.ok:
        appList = json.loads(response.content)
    else:
        log.warning("Call to get apps failed")
        response.raise_for_status()
        sys.exit()

    today = date.today()
    str_start_dt = today.strftime('%m-%d-%Y-%H-%M')
    output_file = open('appsbycall' + str(str_start_dt) + '.csv', 'w', newline='')
    csv_writer = csv.writer(output_file)
    metric_head = ["AppName", "AppID", "Value", "Current", "Occurrences", "Max", "Min", "Sum"]
    csv_writer.writerow(metric_head)

    # For each application, retrieve the calls per minute metric for the last 30 days
    for app in appList:
        app_name = app['name']
        app_id = app['id']
        log.info("Retrieving metric for " + app_name)
        if compare_type == 1:
            resp = s.get(host + getCallsPath1 + app_name + getCallsPath2 + getCallsPath3)
        else:
            resp = s.get(host + getCallsPath1 + str(app_id) + getCallsPath2 + getCallsPath3)
        app_value = 'N/A'
        app_current = 'N/A'
        app_occurrences = 'N/A'
        app_min = 'N/A'
        app_max = 'N/A'
        app_sum = 'N/A'
        if resp.ok:
            metricList = json.loads(resp.content)
            # print(metricList)
            if len(metricList) > 0:
                valueList = metricList[0]['metricValues']
                # print(valueList)
                if len(valueList) > 0:
                    app_value = (valueList[0]['value'])
                    app_current = (valueList[0]['current'])
                    app_occurrences = (valueList[0]['occurrences'])
                    app_min = (valueList[0]['min'])
                    app_max = (valueList[0]['max'])
                    app_sum = (valueList[0]['sum'])
            else:
                app_value = 0
                app_current = 0
                app_occurrences = 0
                app_min = 0
                app_max = 0
                app_sum = 0
        else:
            log.error("Call to get metric for " + app_name + " failed.")
            resp.raise_for_status()
        metric_row = [app_name, app_id, app_value, app_current, app_occurrences, app_max, app_min, app_sum]
        csv_writer.writerow(metric_row)
    output_file.close()


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
    "app_by_calls" + str(datetime.now().strftime("%Y%m%d")) + ".log", mode="a+"
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
get_metrics(baseUrl)
