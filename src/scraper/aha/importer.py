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
        courses_list = self.get_options_by_select_id('courseId')
        course_obj = AHAField(type=AHAField.FIELD_TYPES.COURSE, value=courses_list, user=self.user)
        logging.info("Courses: {}".format(course_obj.value))
        return self.group_data.append(course_obj)

    def get_language(self):
        languages_list = self.get_options_by_select_id('languageId')
        language_obj = AHAField(type=AHAField.FIELD_TYPES.LANGUAGE, value=languages_list, user=self.user)
        logging.info("Languages: {}".format(language_obj.value))
        return self.group_data.append(language_obj)

    def get_location(self):
        locations_list = self.get_options_by_select_id('locationId', remove_first=True)
        location_obj = AHAField(type=AHAField.FIELD_TYPES.LOCATION, value=locations_list, user=self.user)
        logging.info("Locations: {}".format(location_obj.value))
        return self.group_data.append(location_obj)

    def get_tc(self):
        #TODO: search TC for each Course
        self.click_on_first_option(select_id='courseId')
        WebDriverWait(self.browser, 5).until(EC.presence_of_element_located((By.ID, 'tcNames')))
        tc_list = self.get_options_by_select_id('tcId')
        tc_obj = AHAField(type=AHAField.FIELD_TYPES.TC, value=tc_list, user=self.user)
        logging.info("Training Centers: {}".format(tc_obj.value))
        return self.group_data.append(tc_obj)

    def get_ts(self):
        self.click_on_first_option(select_id='tcId')
        WebDriverWait(self.browser, 5).until(EC.presence_of_element_located((By.ID, 'tsNames')))
        ts_list = self.get_options_by_select_id('tcSiteId')
        ts_obj = AHAField(type=AHAField.FIELD_TYPES.TS, value=ts_list, user=self.user)
        logging.info("Training Sites: {}".format(ts_obj.value))
        return self.group_data.append(ts_obj)

    def get_instructors(self):
        instructor_list = self.get_options_by_select_id('instructorId')
        instructor_obj = AHAField(type=AHAField.FIELD_TYPES.INSTRUCTOR, value=instructor_list, user=self.user)
        logging.info("Instructors: {}".format(len(instructor_list)))
        return self.group_data.append(instructor_obj)

    def get_fields(self):
        logger.info("AHA Importing fields running")
        self.get_course()
        self.get_language()
        self.get_location()
        self.get_tc()
        self.get_ts()
        self.get_instructors()

    def save_to_db(self):
        logging.info("Finish AHA Importing, saving")
        AHAField.objects.filter(user=self.user).delete()
        AHAField.objects.bulk_create(self.group_data)

    def run(self):
            self.login()
            self.go_to_add_class_page()
            self.get_fields()
            self.save_to_db()

if __name__ == '__main__':
    importer = AHAImporter(SETTINGS['username'], SETTINGS['password'])
    importer.run()