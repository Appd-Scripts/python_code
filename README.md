# AIG
Temp Repo of python automation scripts for AIG. 

The script here are for the automation of processes in the build, deploy and synchronization of AppDynamics configurations. 

## Scripts: 

1. Credentials environmental file 

* .env --> This file hold the credentials that will be used to run the python scripts against the controller

2. Authorization and Session Builder 

* auth_mgr.py --> This script is the base of all other scripts it request the token and sets up a session with a JSESSION_ID to run all the scripts under 

3. List of Applications 

* appsbycalls --> This script get a list of all applications on the controller and the current metric measurement for the last 30 days. This script is helpful in finding dead applications

4. Get Audit information 

* audit_report_pull_api.py --> This scripts create a day by day pull of the audit information from the controller. If you want to be able to report on data about user actions and logins for greater than 30 days this is how you pull the data to a local drive for analysis

5. Sample Python Audit Report based on pulled files

* audit_report_sum_from_api_files.py --> This is a sample of what can be done with the harvested files from the audit API  

6. Harvest list of tiers

* get_all_tiers.py --> this script get a list of all tiers from all applications in a currated json file or across the entire controller. 
