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

    # TODO: add schedule data items

    def paste_fields(self):
        success, message = self.paste_course()
        if not success:
            return False, message

        success, message = self.paste_language()
        if not success:
            return False, message

        success, message = self.paste_tc()
        if not success:
            return False, message

        success, message = self.paste_ts()
        if not success:
            return False, message

        success, message = self.paste_instructor()
        if not success:
            return False, message

        success, message = self.paste_location()
        if not success:
            return False, message

        success, message = self.paste_date()
        if not success:
            return False, message

        success, message = self.paste_roster_settings()
        if not success:
            return False, message

        success, message = self.paste_notes()
        if not success:
            return False, message

        return True, ""

    def paste_course(self):
        logger.info("Pasting course: {}".format(self.group_data['course']))
        value = self.group_data['course']
        element = "//select[@id='courseId']/option[@value='{}']".format(value)
        try:
            self.browser.find_element_by_xpath(element).click()
        except:
            return False, self.ERROR_MESSAGE.format("course")
        return True, ""

    def paste_language(self):
        logger.info("Pasting language: {}".format(self.group_data['language']))
        value = self.group_data['language']
        element = "//select[@id='languageId']/option[text()='{}']".format(value)
        try:
            self.browser.find_element_by_xpath(element).click()
        except:
            return False, self.ERROR_MESSAGE.format("language")
        return True, ""

    def paste_tc(self):
        logger.info("Pasting Training Center: {}".format(self.group_data['tc']))
        value = self.group_data['tc']
        # element = "//select[@id='tcId']/option[text()='{}']".format(value)
        element = "//select[@id='tcId']/option[@value='{}']".format(value)
        try:
            self.browser.find_element_by_xpath(element).click()
        except:
            return False, self.ERROR_MESSAGE.format("tc")
        return True, ""

    def paste_ts(self):
        logger.info("Pasting Training Site: {}".format(self.group_data['ts']))
        value = self.group_data['ts']
        WebDriverWait(self.browser, 5).until(EC.presence_of_element_located((By.ID, 'tsNames')))
        all_ts = self.browser.find_element_by_id('tcSiteId')
        options = [x for x in all_ts.find_elements_by_tag_name('option')]
        try:
            for element in options:
                if element.get_attribute('value') == value:
                    element.click()
                    break
        except:
            return False, self.ERROR_MESSAGE.format("ts")
        return True, ""

        # element = "//select[@id='tcSiteId']/option[text()='{}']".format(value)
        # self.browser.find_element_by_xpath(element).click()

    def paste_instructor(self):
        logger.info("Pasting instructor: {}".format(self.group_data['instructor']))
        value = self.group_data['instructor']
        WebDriverWait(self.browser, 5).until(EC.presence_of_element_located((By.ID, 'instructorId')))
        all_instructor = self.browser.find_element_by_id('instrNames')
        options = [x for x in all_instructor.find_elements_by_tag_name('option')]
        try:
            for element in options:
                if element.get_attribute('value') == value:
                    element.click()
                    break
        except:
            return False, self.ERROR_MESSAGE.format("instructor")
        return True, ""

    def paste_location(self):
        logger.info("Pasting location: {}".format(self.group_data['location']))
        value = self.group_data['location']
        element = "//select[@id='locationId']/option[@value={}]".format(value)
        try:
            self.browser.find_element_by_xpath(element).click()
        except:
            return False, self.ERROR_MESSAGE.format("location")
        return True, ""

    def paste_date(self):
        logger.info("Pasting date: {}".format(self.group_data['date']))
        value_date = self.group_data['date']
        element_date = "//input[@id='classStartDate']"
        element = self.browser.find_element_by_xpath(element_date)
        try:
            self.browser.execute_script("arguments[0].value = '" + value_date + "'", element)
            self.browser.find_element_by_xpath(element_date).send_keys('date')
        except:
            return False, self.ERROR_MESSAGE.format("date")

        logger.info("Pasting description: {}".format(self.group_data['class_description']))
        class_description = self.group_data['class_description']
        element_description = "//input[@id='classMeetingDescr']"
        try:
            self.browser.find_element_by_xpath(element_description).send_keys(class_description)
        except:
            return False, self.ERROR_MESSAGE.format("description")

        logger.info("Pasting roster dated: {}".format(self.group_data['from'], self.group_data['to']))
        value_start = self.group_data['from']
        element_start = "//select[@id='classMeetingStartTime']/option[text()='{}']".format(value_start)
        try:
            self.browser.find_element_by_xpath(element_start).click()
        except:
            return False, self.ERROR_MESSAGE.format("date from")

        value_end = self.group_data['to']
        element_end = "//select[@id='classMeetingEndTime']/option[text()='{}']".format(value_end)
        try:
            self.browser.find_element_by_xpath(element_end).click()
        except:
            return False, self.ERROR_MESSAGE.format("date end")

        time_button = "//a[@id='buttonSubmitClassTime']"
        try:
            self.browser.find_element_by_xpath(time_button).click()
        except:
            return False, self.ERROR_MESSAGE.format("date finish")

        return True, ""

    def paste_roster_settings(self):
        logger.info("Pasting roster setting:")
        logger.info("Roster limit: {}".format(self.group_data['roster_limit']))
        value_roster_limit = self.group_data['roster_limit']
        element_limit = "//input[@id='numberOfStudents']"
        try:
            self.browser.find_element_by_xpath(element_limit).send_keys(value_roster_limit)
        except:
            return False, self.ERROR_MESSAGE.format("roster limit")

        logger.info(("Cutoff Date: {}".format(self.group_data['cutoff_date'])))
        value_roster_date = self.group_data['cutoff_date']
        element_date = "//input[@id='enrollCutOffDate']"
        element = self.browser.find_element_by_xpath(element_date)
        try:
            self.browser.execute_script("arguments[0].value = '" + value_roster_date + "'", element)
        except:
            return False, self.ERROR_MESSAGE.format("cutoff date")

        return True, ""

    def paste_notes(self):
        logger.info("Pasting notes: {}".format(self.group_data['class_notes']))
        class_notes = self.group_data['class_notes']
        element_notes = "//textarea[@id='notes']"
        try:
            self.browser.find_element_by_xpath(element_notes).send_keys(class_notes)
        except:
            return False, self.ERROR_MESSAGE.format("notes")
        return True, ""

    def save_button(self):
        logger.info("Finish, click 'save': {}".format(self.group_data['course']))
        try:
            self.browser.execute_script("saveInfo('save','false')")
        except:
            return False, self.ERROR_MESSAGE.format("saving")
        return True, ""

    def run(self):
        success, message = self.login()

        if not success:
            return False, message

        success, message = self.go_to_add_class_page()
        if not success:
            return False, message

        success, message = self.paste_fields()
        if not success:
            return False, message

        success, message = self.save_button()
        if not success:
            return False, message

        logger.info("Process ended")
        return True, ""
#
# if __name__ == '__main__':
#     importer = AHAExporter(SETTINGS['username'], SETTINGS['password'], TEST_DATA)
#     importer.run()
