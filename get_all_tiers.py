# Get All tiers for a controller aggregate to a csv file
# auth: Paul Gorrell (PS AppDynamics)

import csv
import json
import logging
import os.path
import sys
import time

from datetime import datetime
from datetime import date
from auth_mgr import AuthMgr


def user_inputs():
    # get user input for files of applications for review
    file_choice = str(input("Use curated application list? ('Y' for yes and 'N' to fetch new application list)?\n"
                            or 'Y'))
    return file_choice


def get_app_list(new_app_list):
    print(new_app_list)
    # Get Applications
    url = baseUrl + '/controller/rest/applications?output=JSON'
    response = s.get(url)
    if response.status_code == 200:
        with open(new_app_list, "w") as app_file:
            app_file.write(response.text)
            log.info("List of applications fetched successfully")
    else:
        log.warning("List of application not fetched")


def get_tier_details(app_file):
    if os.path.exists(app_file):
        log.info("Yeah we have file:")
    else:
        log.warning("No file found.")
        sys.exit()

    with open(app_file) as data_file:
        data = json.load(data_file)
        today = date.today()
        str_start_dt = today.strftime('%m-%d-%Y-%H-%M')
        output_file = open('tier_list_' + str(str_start_dt) + '.csv', 'w', newline='')
        csv_writer = csv.writer(output_file)
        metric_head = ["AppName", "AppID", "Agent_Type", "Tier_Name", "Description", "Tier_Id",
                       "Number_Nodes", "Tier_Type"]
        csv_writer.writerow(metric_head)
        if app_file != curated_list:
            root_json = data
        else:
            root_json = data['applications']

        # for each loop get Application Name:
        for row in root_json:
            app_name = row['name']
            app_id = row['id']
            api_url = '/controller/rest/applications/'
            url = baseUrl + api_url + str(app_id) + '/tiers?output=JSON'
            rule_response = s.get(url)
            time.sleep(1)
            log.info("Fetching Data for " + app_name)
            if rule_response.ok:
                # Write JSON to CSV file
                rule_data = json.loads(rule_response.text)
                for rule in rule_data:
                    print(rule)
                    agent_type = rule['agentType']
                    tier_name = rule['name']
                    description = rule['description']
                    tier_id = rule['id']
                    num_nodes = rule['numberOfNodes']
                    tier_type = rule['type']
                    metric_row = [app_name, app_id, agent_type, tier_name, description, tier_id, num_nodes, tier_type]
                    csv_writer.writerow(metric_row)
            else:
                log.warning("No tier data for " + app_name)

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
    "tier_harvester" + str(datetime.now().strftime("%Y%m%d")) + ".log", mode="a+"
)
fh.setLevel(logging.DEBUG)
fh.setFormatter(formatter)
log.addHandler(fh)

# create console handler with a higher log level
ch = logging.StreamHandler()
ch.setLevel(logging.DEBUG)
ch.setFormatter(formatter)
log.addHandler(ch)

# Set variables

# Do the work
# Set variables
new_list = 'app_file.json'
curated_list = 'cur_app_file.json'

# Do the work
file = user_inputs()
if file.upper() == 'N':
    get_app_list(new_list)
    file_name = new_list
else:
    file_name = curated_list
get_tier_details(file_name)
