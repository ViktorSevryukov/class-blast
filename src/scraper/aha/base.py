import os
import sys
import logging

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.wait import WebDriverWait

"""Settings for local testing on Linux/Mac with Chrome driver"""

LINUX_PLATFORM = 'linux'
MAC_PLATFORM = 'darwin'

WEB_DRIVERS = {
    LINUX_PLATFORM: 'chromedriver_linux_x64',
    MAC_PLATFORM: 'chromedriver_darwin'
}

CURRENT_PATH = os.path.abspath(os.path.dirname(__file__))
try:
    DRIVER_PATH = os.path.join(CURRENT_PATH, '../drivers',
                               WEB_DRIVERS[sys.platform])
except:
    raise Exception


class AHABase():
    """
    Base class for export and import data from AHA
    """

    # Pages to scrap
    URLS = {
        'login': 'https://ahasso.heart.org/Login/',
        'add_class': 'https://ahainstructornetwork.americanheart.org/AHAECC/ecc.jsp?pid=ahaecc.addClass',
    }

    def __init__(self, username, password, logger_name, *args, **kwargs):
        """
        Init
        :param username: AHA account username 
        :param password: AHA account password
        :param logger_name: logger name to use
        """
        self.username = username
        self.password = password
        self.browser = self._setup_browser()
        self.browser.set_window_size("1920", "2560")
        self.logger = logging.getLogger(logger_name)

    @staticmethod
    def _setup_browser():
        """
        Prepare webdriver
        Usually use headless Chrome or PhantomJS
        :return: 
        """
        # Can uncomment code below for local testing
        options = webdriver.ChromeOptions()
        options.add_argument('headless')
        return webdriver.Chrome(executable_path=DRIVER_PATH, options=options)
        # TODO: try to use headless Chrome on server, need to install binary
        # return webdriver.PhantomJS()

    def _login(self):
        """
        Try to login to AHA site
        :return: 
        """
        self.logger.info(
            "Try to AHA LogIn with username {}".format(self.username))
        self.browser.get(self.URLS['login'])

        # wait until JS and DOM elements are loaded
        self.browser.implicitly_wait(10)

        login_form = WebDriverWait(self.browser, 10).until(
            EC.presence_of_element_located(
                (By.XPATH, "//form[starts-with(@action, '/Login')]")))

        username_form = login_form.find_element_by_id('Email')
        password_form = login_form.find_element_by_id('Password')
        username_form.send_keys(self.username)
        password_form.send_keys(self.password)
        self.logger.info("LogIn click, username: {}".format(self.username))
        # click on 'login' button
        login_form.submit()

    def _go_to_add_class_page(self):
        """
        Redirect to class page to add new class
        :return: 
        """
        self.logger.info("Go to class page")
        self.browser.implicitly_wait(10)  # wait for JS and DOM elements
        WebDriverWait(self.browser, 10).until(
            EC.presence_of_element_located((By.ID, "main")))
        self.browser.get(self.URLS['add_class'])
        self.logger.info("Current URL: {}".format(self.browser.current_url))
