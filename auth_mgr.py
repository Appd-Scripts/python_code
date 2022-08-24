
import logging
import requests
import getpass
# requires the package python-decouple
from decouple import config

# Logging config
log = logging.getLogger("AppdynamicsAuthMgr")
log.setLevel(logging.INFO)

# create formatter and add it to the handlers
formatter = logging.Formatter(
    fmt="%(asctime)s - %(name)s:%(lineno)d - %(levelname)s - %(message)s",
    datefmt="%m-%d-%Y %H:%M:%S",
)

# create file handler which logs even debug messages
ch = logging.StreamHandler()
ch.setLevel(logging.DEBUG)
ch.setFormatter(formatter)
log.addHandler(ch)


class AuthMgr:
    def __init__(
        self, username="", password="", account="", session=requests.Session()
    ):
        self.username = username
        self.password = password
        self.account = account
        self.instance_type = "SaaS"  # options are 'SaaS' or 'on-Prem'
        self.enviro = "live"
        self.isAuthenticated = False
        self.session = session
        self.base_url = "https://" + self.account + ".saas.appdynamics.com"
        self.token = ""
        self.session.headers.update(
            {
                "Content-Type": "application/json",
                "Accept": "application/json, text/plain, */*",
            }
        )

    def login_controller(self):
        if not self.username:
            # default to environment variable
            self.username = config("APPD_USERNAME")

        # if that fails, request username manually
        if not self.username:
            self.username = input("\tAppD Account Username: ")

        # default to environment variable
        if not self.password:
            self.password = config("APPD_PASSWORD")

        if not self.password:
            self.password = getpass.getpass("\tAppD Account Password: ")

        if not self.account:
            if self.enviro == "test":
                self.account = config("DEV_ACCOUNT")
            else:
                self.account = config("PRD_ACCOUNT")

        if not self.account:
            if self.enviro == "test":
                # Add account name for test system
                self.account = "aig-test"
            else:
                # Add account name for production system
                self.account == "aig-prod"

        if self.instance_type == "SaaS":
            # This line is for use with a SaaS controller
            self.base_url = "https://" + self.account + ".saas.appdynamics.com"
        else:
            # This is where you enter the url for the on-prem controller
            self.base_url = "https://mycontoller.company.com"

        # Retrieve csrf token
        login_url = self.base_url + "/controller/auth?action=login"

        r = self.session.get(
            login_url, auth=(str(self.username + "@" + self.account), self.password), params={"action": "login"}
        )

        if r.status_code == 200:
            try:
                x_csrf_token = self.session.cookies.get_dict()["X-CSRF-TOKEN"]
                # shortcut version
                cookie_line = f"JSESSIONID={r.cookies['JSESSIONID']};X-CSRF-TOKEN={r.cookies['X-CSRF-TOKEN']};"
                # cookie_line = 'JSESSIONID=' + r.cookies['JSESSIONID'] + ';X-CSRF-TOKEN='+ r.cookies['X-CSRF-TOKEN''] + ';'
                log.info("Login was successful.")
                self.isAuthenticated = True
                self.session.headers.update({"X-CSRF-TOKEN": x_csrf_token})
                self.session.headers.update({"Cookie": cookie_line})
                self.token = x_csrf_token
            except KeyError:
                log.warning("Login was unsuccessful - CSRF Token missing.")
                raise SystemExit
        else:
            log.warning("Login was unsuccessful, please verify your credentials.")
            raise SystemExit
