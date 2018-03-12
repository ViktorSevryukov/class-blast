from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

from scraper.aha.base import AHABase

import logging

logger = logging.getLogger('aha_export')

SETTINGS = {
    'username': 'jason.j.boudreault@gmail.com',
    'password': 'Thecpr1'
}

TEST_DATA = {
    'course': "Airway Management Course",
    'language': "English",
    'location': "Above Bar CPR Office ",
    'tc': "HeartShare Training Services Inc.",
    'ts': "HeartShare Training North Bay",
    'instructor': "Jason Boudreault",
    'date': "14/02/2018",
    'from': "10:15 AM",
    'to': "11:15 AM",
    'class_description': "test",
    'roster_limit': '15',
    'roster_date': "14/02/2018"
}


class AHAExporter(AHABase):
    """
    Class for import information info from AHA site
    """

    ERROR_MESSAGE = "Pasting {} failed"

    def __init__(self, username, password, group_data, *args, **kwargs):
        super(AHAExporter, self).__init__(username, password, *args, **kwargs)
        self.group_data = group_data

    def paste_fields(self):
        self.paste_course()
        self.paste_language()
        self.paste_tc()
        self.paste_ts()
        self.paste_instructor()
        self.paste_location()
        self.paste_date()
        self.paste_roster_settings()
        self.paste_notes()

    def paste_course(self):
        logger.info("Pasting course: {}".format(self.group_data['course']))
        value = self.group_data['course']
        element = "//select[@id='courseId']/option[@value='{}']".format(value)
        self.browser.find_element_by_xpath(element).click()

    def paste_language(self):
        logger.info("Pasting language: {}".format(self.group_data['language']))
        value = self.group_data['language']
        element = "//select[@id='languageId']/option[text()='{}']".format(
            value)
        self.browser.find_element_by_xpath(element).click()

    def paste_tc(self):
        logger.info(
            "Pasting Training Center: {}".format(self.group_data['tc']))
        value = self.group_data['tc']
        # element = "//select[@id='tcId']/option[text()='{}']".format(value)
        element = "//select[@id='tcId']/option[@value='{}']".format(value)
        self.browser.find_element_by_xpath(element).click()

    def paste_ts(self):
        logger.info("Pasting Training Site: {}".format(self.group_data['ts']))
        value = self.group_data['ts']
        WebDriverWait(self.browser, 5).until(
            EC.presence_of_element_located((By.ID, 'tsNames')))
        all_ts = self.browser.find_element_by_id('tcSiteId')
        options = [x for x in all_ts.find_elements_by_tag_name('option')]
        for element in options:
            if element.get_attribute('value') == value:
                element.click()
                break

                # element = "//select[@id='tcSiteId']/option[text()='{}']".format(value)
                # self.browser.find_element_by_xpath(element).click()

    def paste_instructor(self):
        logger.info(
            "Pasting instructor: {}".format(self.group_data['instructor']))
        value = self.group_data['instructor']
        WebDriverWait(self.browser, 5).until(
            EC.presence_of_element_located((By.ID, 'instructorId')))
        all_instructor = self.browser.find_element_by_id('instrNames')
        options = [x for x in
                   all_instructor.find_elements_by_tag_name('option')]
        for element in options:
            if element.get_attribute('value') == value:
                element.click()
                break

    def paste_location(self):
        logger.info("Pasting location: {}".format(self.group_data['location']))
        value = self.group_data['location']
        element = "//select[@id='locationId']/option[@value={}]".format(value)
        self.browser.find_element_by_xpath(element).click()

    def paste_date(self):
        logger.info("Pasting date: {}".format(self.group_data['date']))
        value_date = self.group_data['date']
        element_date = "//input[@id='classStartDate']"
        element = self.browser.find_element_by_xpath(element_date)
        self.browser.execute_script(
            "arguments[0].value = '" + value_date + "'", element)
        self.browser.find_element_by_xpath(element_date).send_keys('date')

        logger.info("Pasting description: {}".format(
            self.group_data['class_description']))
        class_description = self.group_data['class_description']
        element_description = "//input[@id='classMeetingDescr']"
        self.browser.find_element_by_xpath(element_description).send_keys(
            class_description)

        logger.info("Pasting roster dated: {}".format(self.group_data['from'],
                                                      self.group_data['to']))
        value_start = self.group_data['from']
        element_start = "//select[@id='classMeetingStartTime']/option[text()='{}']".format(
            value_start)
        self.browser.find_element_by_xpath(element_start).click()

        value_end = self.group_data['to']
        element_end = "//select[@id='classMeetingEndTime']/option[text()='{}']".format(
            value_end)
        self.browser.find_element_by_xpath(element_end).click()

        time_button = "//a[@id='buttonSubmitClassTime']"
        self.browser.find_element_by_xpath(time_button).click()

    def paste_roster_settings(self):
        logger.info("Pasting roster setting:")
        logger.info("Roster limit: {}".format(self.group_data['roster_limit']))
        value_roster_limit = self.group_data['roster_limit']
        element_limit = "//input[@id='numberOfStudents']"
        self.browser.find_element_by_xpath(element_limit).send_keys(
            value_roster_limit)

        logger.info(("Cutoff Date: {}".format(self.group_data['cutoff_date'])))
        value_roster_date = self.group_data['cutoff_date']
        element_date = "//input[@id='enrollCutOffDate']"
        element = self.browser.find_element_by_xpath(element_date)
        self.browser.execute_script(
            "arguments[0].value = '" + value_roster_date + "'", element)

    def paste_notes(self):
        logger.info("Pasting notes: {}".format(self.group_data['class_notes']))
        class_notes = self.group_data['class_notes']
        element_notes = "//textarea[@id='notes']"
        self.browser.find_element_by_xpath(element_notes).send_keys(
            class_notes)

    def save_button(self):
        logger.info(
            "Finish, click 'save': {}".format(self.group_data['course']))
        self.browser.execute_script("saveInfo('save','false')")

    def run(self):
        try:
            self.login()
            self.go_to_add_class_page()
        except:
            raise Exception(
                'login failed (username/password incorrect or AHA service unavailable)')

        try:
            self.paste_fields()
            self.save_button()
        except:
            raise Exception('error while exporting')

        logger.info("Export ended")
