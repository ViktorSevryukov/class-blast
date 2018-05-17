import logging

from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

from apps.core.models import AHAGroup, EnrollWareGroup
from scraper.aha.base import AHABase


logger = logging.getLogger('aha_export')

"""
EXAMPLE_DATA_TO_EXPORT = {
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
    'roster_date': "14/02/2018",
    'class_notes': "string"
}
"""


class AHAExporter(AHABase):
    """
    Class for export information info from AHA site
    """

    ERROR_MESSAGE = "Pasting {} failed"

    def __init__(self, username, password, group_data, *args, **kwargs):
        """
        Init
        :param username: AHA account username 
        :param password: AHA account password
        :param group_data: group data to export 
        """
        super(AHAExporter, self).__init__(username, password, *args, **kwargs)
        self.group_data = group_data

    def _paste_fields(self):
        """
        Paste all fields to create new class
        :return: 
        """
        self._paste_course()
        self._paste_language()
        self._paste_tc()
        self._paste_ts()
        self._paste_instructor()
        self._paste_location()
        self._paste_date()
        self._paste_roster_settings()
        self._paste_notes()

    def _paste_course(self):
        """
        Paste 'course' value
        :return: 
        """
        logger.info("Pasting course: {}".format(self.group_data['course']))
        value = self.group_data['course']
        element = "//select[@id='courseId']/option[@value='{}']".format(value)
        self.browser.find_element_by_xpath(element).click()

    def _paste_language(self):
        """
        Paste 'language' value
        :return: 
        """
        logger.info("Pasting language: {}".format(self.group_data['language']))
        value = self.group_data['language']
        element = "//select[@id='languageId']/option[text()='{}']".format(
            value)
        self.browser.find_element_by_xpath(element).click()

    def _paste_tc(self):
        """
        Paste 'training center' value
        :return: 
        """
        logger.info(
            "Pasting Training Center: {}".format(self.group_data['tc']))
        value = self.group_data['tc']
        # element = "//select[@id='tcId']/option[text()='{}']".format(value)
        element = "//select[@id='tcId']/option[@value='{}']".format(value)
        self.browser.find_element_by_xpath(element).click()

    def _paste_ts(self):
        """
        Paste 'training site' value
        :return: 
        """
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

    def _paste_instructor(self):
        """
        Paste 'instructor' value
        :return: 
        """
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

    def _paste_location(self):
        """
        Paste 'location' value
        :return: 
        """
        logger.info("Pasting location: {}".format(self.group_data['location']))
        value = self.group_data['location']
        element = "//select[@id='locationId']/option[@value={}]".format(value)
        self.browser.find_element_by_xpath(element).click()

    def _paste_date(self):
        """
        Paste 'date' value (class start date)
        :return: 
        """
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

    def _paste_roster_settings(self):
        """
        Paste roster stiings
        :return: 
        """
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

    def _paste_notes(self):
        """
        Paste 'notes' value
        :return: 
        """
        logger.info("Pasting notes: {}".format(self.group_data['class_notes']))
        class_notes = self.group_data['class_notes']
        element_notes = "//textarea[@id='notes']"
        self.browser.find_element_by_xpath(element_notes).send_keys(
            class_notes)

    def _save_button(self):
        """
        Click on 'save' to save class
        :return: 
        """
        logger.info(
            "Finish, click 'save': {}".format(self.group_data['course']))
        self.browser.execute_script("saveInfo('save','false')")

    def _check_success_export(self):
        """
        Check if class successfully created
        :return: 
        """
        try:
            alert_div = WebDriverWait(self.browser, 10).until(
                EC.presence_of_element_located((By.CLASS_NAME,
                                                "alert-success")))
        except:
            alert_div = self.browser.find_element(By.CLASS_NAME,
                                                  "alert-danger")
            ul = alert_div.find_element(By.TAG_NAME, 'ul')
            li_elements = ul.find_elements(By.TAG_NAME, 'li')

            errors = [li.text for li in li_elements]

            raise Exception('\n'.join(errors))

    def _save_aha_group_to_db(self):
        """
        Create exported AHA group in database
        :return: 
        """
        try:
            ew_group = EnrollWareGroup.objects.get(
                id=self.group_data['enroll_id'])
        except:
            logger.info("enrollware group with id = {} not found ".format(
                self.group_data['enroll_id']))
        else:
            AHAGroup.objects.create(
                enrollware_group=ew_group,
                course=self.group_data['course'],
                location=self.group_data['location'],
                instructor=self.group_data['instructor'],
                training_center=self.group_data['tc'],
                training_site=self.group_data['ts'],
                cutoff_date=self.group_data['cutoff_date'],
                roster_limit=self.group_data['roster_limit'],
                description=self.group_data['class_description'],
                notes=self.group_data['class_notes']
            )

    def run(self):
        """
        Run process of export groups to AHA
        :return: 
        """

        # try to login and redirect to add class page
        try:
            self._login()
            self._go_to_add_class_page()
        except:
            raise Exception(
                'login failed (username/password incorrect or AHA service unavailable)')

        # try to paste all fields
        try:
            self._paste_fields()
        except:
            raise Exception('can not paste fields, try again')

        # try to save class on AHA and save info in database
        try:
            self._save_button()
            self._check_success_export()
            self._save_aha_group_to_db()
        except Exception as msg:
            raise Exception('error while exporting group {}'.format(msg))
