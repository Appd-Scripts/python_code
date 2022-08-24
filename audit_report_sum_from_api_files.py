import json
import csv
import logging
import sys
from datetime import datetime
from datetime import timedelta


def check(string, sub_str):
    if string.find(sub_str) == -1:
        return string
    else:
        new_string = string.removesuffix(sub_str)
        return new_string


def calculate_counts(audit_dir, StartDate, EndDate):
    # Convert to user input to timestamp
    start_date_time_obj = datetime.strptime(StartDate, "%m/%d/%Y")
    end_date_time_obj = datetime.strptime(EndDate, "%m/%d/%Y")

    # initialize variables
    total_logins = 0
    # unique_logins = 0
    week_logins = 0
    unique_week_logins = 0
    all_resets = 0
    days = 0
    weeks = 0
    columnLoginName = "Logins Week 0"
    filename = ""

    # Set up dictionaries and list
    username_store = []
    week_username_store = []
    users = {}
    weekly = []
    weekly_unique = []

    # Process Files
    while start_date_time_obj <= end_date_time_obj:
        # Make sure to put the appropriate path here
        filename = audit_dir + '/audit_file_' + str(start_date_time_obj.date()) + '.json'
        days += 1
        if days > 7:
            log.info('Logins Week ' + str(weeks) + ': ' + str(week_logins))
            log.info('Unique Logins Week ' + str(weeks) + ': ' + str(unique_week_logins))
            weekly.append(week_logins)
            weekly_unique.append(unique_week_logins)
            days = 1
            weeks += 1
            week_logins = 0
            unique_week_logins = 0
            columnLoginName = "Logins Week " + str(weeks)
            week_username_store.clear()

        try:
            with open(filename) as json_file:
                # Read Data from file
                data = json_file.read()
                if not data:
                    log.warning('No data in file: ' + str(filename))
                else:
                    log.info('Processing data from file: ' + str(filename))
                    obj = json.loads(data)

                # Process data in file one entry at a time
                for s in range(len(obj)):
                    if 'userName' in obj[s]:
                        temp_username = obj[s]['userName']
                        username = check(temp_username, '@nostradamus')
                        if username in username_store:
                            if obj[s]["action"] == "LOGIN":
                                if username not in week_username_store:
                                    week_username_store.append(username)
                                    unique_week_logins += 1
                                if columnLoginName not in users[username]:
                                    users[username][columnLoginName] = 1
                                else:
                                    users[username][columnLoginName] += 1
                                week_logins += 1
                                total_logins += 1
                            if obj[s]["action"] == "USER_PASSWORD_CHANGED":
                                all_resets += 1
                                if 'passchangecnt' not in users[username]:
                                    users[username]['passchangecnt'] = 1
                                else:
                                    users[username]['passchangecnt'] += 1
                        else:
                            if obj[s]["action"] == "LOGIN":
                                username_store.append(username)
                                users[username] = {}
                                if columnLoginName not in users[username]:
                                    users[username][columnLoginName] = 1
                                else:
                                    users[username][columnLoginName] += 1
                                if username not in week_username_store:
                                    week_username_store.append(username)
                                    unique_week_logins += 1
                            if obj[s]["action"] == "USER_PASSWORD_CHANGED":
                                all_resets += 1
                                if 'passchangecnt' not in users[username]:
                                    users[username]['passchangecnt'] = 1
                                else:
                                    users[username]['passchangecnt'] += 1
        except IOError as e:
            log.warning(filename + ' - I/O error({0}): {1}'.format(e.errno, e.strerror))
        except:  # handle other exceptions such as attribute errors
            log.warning(filename + ' - Unexpected error:', sys.exc_info()[0])

        # Go to next days files
        start_date_time_obj += delta

    # add weeks stats to list
    weekly.append(week_logins)
    weekly_unique.append(unique_week_logins)

    # Debug lines - can be deleted
    # print('Logins Week ' + str(weeks) + ': ' + str(week_logins))
    # print('Unique Logins Week ' + str(weeks) + ': ' + str(unique_week_logins))

    create_report(StartDate, EndDate, users, username_store, weekly, weekly_unique, total_logins, all_resets)


def create_report(start_date, end_date, users, username_store, weekly, weekly_unique, total_logins, all_resets):
    # Create output file of report
    startDate = start_date.replace('/', '')
    endDate = end_date.replace('/', '')
    outputFileName = 'audit_report' + startDate + '-' + endDate + '.csv'
    try:
        with open(outputFileName, 'w', newline='') as output_file:
            csv_writer = csv.writer(output_file)
            csv_writer.writerow(['UserName', 'Week1 Logins', 'Week2 Logins', 'Week3 Logins', 'Week4 Logins', 'Week 5 Logins', 'Password Resets'])
            unique_logins = len(username_store)
            for key, value in users.items():
                uName = key
                # print(key, value)  debug line can be deleted
                cnt1 = cnt2 = cnt3 = cnt4 = cnt5 = cnt6 = 0
                for act, act_cnt in value.items():
                    if act == 'Logins Week 0':
                        cnt1 = act_cnt
                    elif act == 'Logins Week 1':
                        cnt2 = act_cnt
                    elif act == 'Logins Week 2':
                        cnt3 = act_cnt
                    elif act == 'Logins Week 3':
                        cnt4 = act_cnt
                    elif act == 'Logins Week 4':
                        cnt5 = act_cnt
                    elif act == 'passchangecnt':
                        cnt6 = act_cnt
                csv_writer.writerow([uName, cnt1, cnt2, cnt3, cnt4, cnt5, cnt6])

            # write a blank row
            csv_writer.writerow([])

            # format totals for weekly logins
            i = 0
            cnt1 = cnt2 = cnt3 = cnt4 = cnt5 = 0
            for week_item in weekly:
                if i == 0:
                    cnt1 = week_item
                elif i == 1:
                    cnt2 = week_item
                elif i == 2:
                    cnt3 = week_item
                elif i == 3:
                    cnt4 = week_item
                else:
                    cnt5 = week_item
                i += 1
            csv_writer.writerow(['Weekly Logins', cnt1, cnt2, cnt3, cnt4, cnt5])

            # format totals for weekly unique logins
            i = 0
            cnt1 = cnt2 = cnt3 = cnt4 = cnt5 = 0
            for week_item in weekly_unique:
                if i == 0:
                    cnt1 = week_item
                elif i == 1:
                    cnt2 = week_item
                elif i == 2:
                    cnt3 = week_item
                elif i == 3:
                    cnt4 = week_item
                else:
                    cnt5 = week_item
                i += 1
            csv_writer.writerow(['Weekly Unique Logins', cnt1, cnt2, cnt3, cnt4, cnt5])
            csv_writer.writerow(['Overall Totals', 'Unique Logins:', unique_logins, 'All Logins:', total_logins, 'All Resets:', all_resets])
    except IOError as e:
        log.warning(outputFileName + ' - I/O error({0}): {1}'.format(e.errno, e.strerror))
        exit()


# Get input of Date Range for the report
getStartDate = (input("Starting Date mm/dd/yyyy (not greater than 30 days ago): ") or '08/01/2021')
getEndDate = (input("Ending Date mm/dd/yyyy: ") or '08/07/2021')
delta = timedelta(days=1)
auditDir = 'audit_files'

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
    "customLoginReport" + str(datetime.now().strftime("%Y%m%d")) + ".log", mode="a+"
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
calculate_counts(auditDir, getStartDate, getEndDate)
