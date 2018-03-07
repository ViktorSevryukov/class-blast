from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

from apps.core.models import AHAField
from scraper.aha.base import AHABase

import logging

logger = logging.getLogger('aha_import')

SETTINGS = {
    'username': 'jason.j.boudreault@gmail.com',
    'password': 'Thecpr1'
}


class AHAImporter(AHABase):
    """
    Class for import information info from AHA site
    """

    ERROR_MESSAGE = "Getting {} failed"

    XPATH_FILTERS = {
        'not_empty': "string-length(translate(normalize-space(text()), ' ', ''))>0"
    }

    XPATH_TPLS = {
        'select': "//select[@id='{select_id}']/option[{filter}]"
    }

    def __init__(self, username, password, user, *args, **kwargs):
        super(AHAImporter, self).__init__(username, password, *args, **kwargs)
        self.user = user
        self.group_data = []

    def get_options_by_select_id(self, select_id, remove_first=False):
        # get non-empty options from select element
        xpath = self.XPATH_TPLS['select'].format(select_id=select_id, filter=self.XPATH_FILTERS['not_empty'])
        options = self.browser.find_elements_by_xpath(xpath)
        values_list = []
        if remove_first:
            options.pop(0)

        for element in options:
            element_dict = {
                'value': element.get_attribute('value'),
                'text': element.get_attribute('text')
            }
            values_list.append(element_dict)
        return values_list

    def click_on_first_option(self, select_id):
        xpath = self.XPATH_TPLS['select'].format(select_id=select_id, filter=self.XPATH_FILTERS['not_empty'])
        self.browser.find_element_by_xpath(xpath).click()

    def get_course(self):
        try:
            courses_list = self.get_options_by_select_id('courseId')
        except:
            return False, self.ERROR_MESSAGE.format("course list")

        course_obj = AHAField(type=AHAField.FIELD_TYPES.COURSE, value=courses_list, user=self.user)
        logging.info("Courses: {}".format(course_obj.value))
        self.group_data.append(course_obj)

        return True, ""

    def get_language(self):
        try:
            languages_list = self.get_options_by_select_id('languageId')
        except:
            return False, self.ERROR_MESSAGE.format("language")

        language_obj = AHAField(type=AHAField.FIELD_TYPES.LANGUAGE, value=languages_list, user=self.user)
        logging.info("Languages: {}".format(language_obj.value))
        self.group_data.append(language_obj)

        return True, ""

    def get_location(self):
        try:
            locations_list = self.get_options_by_select_id('locationId', remove_first=True)
        except:
            return False, self.ERROR_MESSAGE.format("location")
        location_obj = AHAField(type=AHAField.FIELD_TYPES.LOCATION, value=locations_list, user=self.user)
        logging.info("Locations: {}".format(location_obj.value))
        self.group_data.append(location_obj)

        return True, ""

    def get_tc(self):
        #TODO: search TC for each Course
        self.click_on_first_option(select_id='courseId')
        WebDriverWait(self.browser, 5).until(EC.presence_of_element_located((By.ID, 'tcNames')))
        try:
            tc_list = self.get_options_by_select_id('tcId')
        except:
            return False, self.ERROR_MESSAGE.format("tc list")

        tc_obj = AHAField(type=AHAField.FIELD_TYPES.TC, value=tc_list, user=self.user)
        logging.info("Training Centers: {}".format(tc_obj.value))
        self.group_data.append(tc_obj)

        return True, ""

    def get_ts(self):
        self.click_on_first_option(select_id='tcId')
        WebDriverWait(self.browser, 5).until(EC.presence_of_element_located((By.ID, 'tsNames')))
        try:
            ts_list = self.get_options_by_select_id('tcSiteId')
        except:
            return False, self.ERROR_MESSAGE.format("ts list")

        ts_obj = AHAField(type=AHAField.FIELD_TYPES.TS, value=ts_list, user=self.user)
        logging.info("Training Sites: {}".format(ts_obj.value))
        self.group_data.append(ts_obj)

        return True, ""

    def get_instructors(self):
        try:
            instructor_list = self.get_options_by_select_id('instructorId')
        except:
            return False, self.ERROR_MESSAGE.format("instructor list")

        instructor_obj = AHAField(type=AHAField.FIELD_TYPES.INSTRUCTOR, value=instructor_list, user=self.user)
        logging.info("Instructors: {}".format(len(instructor_list)))
        self.group_data.append(instructor_obj)

        return True, ""

    def get_fields(self):
        logger.info("AHA Importing fields running")
        success, message = self.get_course()
        if not success:
            return False, message

        success, message = self.get_language()
        if not success:
            return False, message

        success, message = self.get_location()
        if not success:
            return False, message

        success, message = self.get_tc()
        if not success:
            return False, message

        success, message = self.get_ts()
        if not success:
            return False, message

        success, message = self.get_instructors()
        if not success:
            return False, message

        return True, ""

    def save_to_db(self):
        logging.info("Finish AHA Importing, saving")
        AHAField.objects.filter(user=self.user).delete()
        AHAField.objects.bulk_create(self.group_data)
        return True, ""


    def run(self):
        success, message = self.login()

        if not success:
            return False, message

        success, message = self.go_to_add_class_page()

        if not success:
            return False, message

        success, message = self.get_fields()

        if not success:
            return False, message

        success, message = self.save_to_db()

        if not success:
            return False, message

        return True, ""

if __name__ == '__main__':
    importer = AHAImporter(SETTINGS['username'], SETTINGS['password'])
    importer.run()