import os
import sys

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.wait import WebDriverWait


LINUX_PLATFORM = 'linux'
MAC_PLATFORM = 'darwin'

WEB_DRIVERS = {
    LINUX_PLATFORM: 'chromedriver_linux_x64',
    MAC_PLATFORM: 'chromedriver_darwin'
}

CURRENT_PATH = os.path.abspath(os.path.dirname(__file__))
try:
    DRIVER_PATH = os.path.join(CURRENT_PATH, '../drivers', WEB_DRIVERS[sys.platform])
except:
    raise Exception


class AHABase():
    """
    Base class for export and import data from AHA
    """

    URLS = {
        'login': 'https://sso.heart.org/account.html',
        'add_class': 'https://ahainstructornetwork.americanheart.org/AHAECC/ecc.jsp?pid=ahaecc.addClass',
    }

    def __init__(self, username, password, *args, **kwargs):
        self.username = username
        self.password = password
        self.browser = self.setup_browser()

    @staticmethod
    def setup_browser():
        # options = webdriver.ChromeOptions()
        # options.add_argument('headless')
        # return webdriver.Chrome(executable_path=DRIVER_PATH, options=options)
        #TODO: try to use Chrome, need to install Chrome binary on server
        return webdriver.PhantomJS()

    def login(self):
        self.browser.get(self.URLS['login'])
        self.browser.implicitly_wait(10)

        #TODO: add wait for login form, or redirect right now to "add class URL'
        login_form = WebDriverWait(self.browser, 10).until(
                EC.presence_of_element_located((By.ID, "userScreDiv_content")))

        username_form = login_form.find_element_by_class_name('gigya-input-text')
        password_form = login_form.find_element_by_class_name('gigya-input-password')

        username_form.send_keys(self.username)
        password_form.send_keys(self.password)
        login_form.find_element_by_class_name("gigya-input-submit").click()

    def go_to_add_class_page(self):
        WebDriverWait(self.browser, 5).until(
            EC.text_to_be_present_in_element((By.TAG_NAME, "strong"), "Welcome!"))
        self.browser.get(self.URLS['add_class'])
