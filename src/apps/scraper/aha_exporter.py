from datetime import date
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import Select


SETTINGS = {
    'username': 'jason.j.boudreault@gmail.com',
    'password': 'Thecpr1'
}


class AHAExporter():
    """
    Class for import information info from AHA site
    """
    URLS = {
        'login': 'https://sso.heart.org/account.html',
        'add_course': 'https://ahainstructornetwork.americanheart.org/AHAECC/ecc.jsp?pid=ahaecc.addClass&_requestid=535927',
    }
    def __init__(self, username, password, group_data):
    # def __init__(self, username, password):
        self.username = username
        self.password = password
        self.selenium_browser = webdriver.Chrome()
#TODO: get group_data from DB
        self.group_data = group_data
        # self.group_data = {'course': "Airway Management Course",
        #                    'language': "English",
        #                    'location': "Above Bar CPR Office ",
        #                    'tc': "HeartShare Training Services Inc.",
        #                    'ts': "HeartShare Training North Bay",
        #                    'instructor': "Jason Boudreault",
        #                    'date': "14/02/2018",
        #                    'from': "10:15 AM",
        #                    'to': "11:15 AM",
        #                    'class_description': "test",
        #                    'roster_limit': '15',
        #                    'roster_date': "14/02/2018"
        #                    }
#TODO: add schedule data items

    def login(self):
        self.selenium_browser.get(self.URLS['login'])
        self.selenium_browser.implicitly_wait(10)

        login_form = WebDriverWait(self.selenium_browser, 10).until(
                EC.presence_of_element_located((By.ID, "userScreDiv_content")))
        username_form = login_form.find_element_by_class_name('gigya-input-text')
        password_form = login_form.find_element_by_class_name('gigya-input-password')

        username_form.send_keys("jason.j.boudreault@gmail.com")
        password_form.send_keys("Thecpr1")
        login_form.find_element_by_class_name("gigya-input-submit").click()
        print("LOGIN SUCCESS")

    def jump_page(self):

        WebDriverWait(self.selenium_browser, 5).until(
            EC.text_to_be_present_in_element((By.TAG_NAME, "strong"), "Welcome!"))
        self.selenium_browser.get(self.URLS['add_course'])

    def paste_course(self):
        value = self.group_data['course']
        element = "//select[@id='courseId']/option[text()='{}']".format(value)
        self.selenium_browser.find_element_by_xpath(element).click()

    def paste_language(self):
        value = self.group_data['language']
        element = "//select[@id='languageId']/option[text()='{}']".format(value)
        self.selenium_browser.find_element_by_xpath(element).click()

    def paste_tc(self):
        value = self.group_data['tc']
        element = "//select[@id='tcId']/option[text()='{}']".format(value)
        self.selenium_browser.find_element_by_xpath(element).click()

    def paste_ts(self):
        value = self.group_data['ts']
        WebDriverWait(self.selenium_browser, 5).until(EC.presence_of_element_located((By.ID, 'tsNames')))
        all_ts = self.selenium_browser.find_element_by_id('tcSiteId')
        options = [x for x in all_ts.find_elements_by_tag_name('option')]
        for element in options:
            if element.get_attribute('text') == value:
                element.click()
                break

        # element = "//select[@id='tcSiteId']/option[text()='{}']".format(value)
        # self.selenium_browser.find_element_by_xpath(element).click()

    def paste_instructor(self):
        value = self.group_data['instructor']
        WebDriverWait(self.selenium_browser, 5).until(EC.presence_of_element_located((By.ID, 'instructorId')))
        all_instructor = self.selenium_browser.find_element_by_id('instrNames')
        options = [x for x in all_instructor.find_elements_by_tag_name('option')]
        for element in options:
            if element.get_attribute('text') == value:
                element.click()
                break

    def paste_location(self):
        value = self.group_data['location']
        element = "//select[@id='locationId']/option[text()='{}']".format(value)
        self.selenium_browser.find_element_by_xpath(element).click()

    def paste_date(self):
        value_date = self.group_data['date']
        element_date = "//input[@id='classStartDate']"
        element = self.selenium_browser.find_element_by_xpath(element_date)

        # self.selenium_browser.execute_script("console.log(arguments[0]); arguments[0].setAttribute('readonly', false); arguments[0].setAttribute('value', '" + value_date + "')", element)
        self.selenium_browser.execute_script("console.log(arguments[0]); arguments[0].setAttribute('readonly', false); arguments[0].value = '" + value_date + "'", element)
        self.selenium_browser.find_element_by_xpath(element_date).send_keys('1/03/2018')

        class_description = self.group_data['class_description']
        element_description = "//input[@id='classMeetingDescr']"
        self.selenium_browser.find_element_by_xpath(element_description).send_keys(class_description)

        value_start = self.group_data['from']
        element_start = "//select[@id='classMeetingStartTime']/option[text()='{}']".format(value_start)
        self.selenium_browser.find_element_by_xpath(element_start).click()

        value_end = self.group_data['to']
        element_end = "//select[@id='classMeetingEndTime']/option[text()='{}']".format(value_end)
        self.selenium_browser.find_element_by_xpath(element_end).click()

        time_button = "//a[@id='buttonSubmitClassTime']"
        self.selenium_browser.find_element_by_xpath(time_button).click()

    def paste_roster_settings(self):
        value_roster_limit = self.group_data['roster_limit']
        element_limit = "//input[@id='numberOfStudents']"
        self.selenium_browser.find_element_by_xpath(element_limit).send_keys(value_roster_limit)

        value_roster_date = self.group_data['roster_date']
        element_date = "//input[@id='enrollCutOffDate']"
        element = self.selenium_browser.find_element_by_xpath(element_date)
        self.selenium_browser.execute_script("console.log(arguments[0]); arguments[0].setAttribute('readonly', false); arguments[0].value = '" + value_roster_date + "'", element)

    def save_button(self):
        self.selenium_browser.execute_script("saveInfo('save','false')")

    def run(self):
        self.login()
        self.jump_page()
        self.paste_course()
        self.paste_language()
        self.paste_tc()
        self.paste_ts()
        self.paste_instructor()
        self.paste_location()
        self.paste_date()
        self.paste_roster_settings()
        self.save_button()
#
if __name__ == '__main__':
    importer = AHAExporter(SETTINGS['username'], SETTINGS['password'])
    importer.run()
