import logging

from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

from apps.core.models import AHAField
from scraper.aha.base import AHABase


logger = logging.getLogger('aha_import')


class AHAImporter(AHABase):
    """
    Class for import information info from AHA site
    """

    ERROR_MESSAGE = "Getting {} failed"

    # filter to get non-empty values from element
    XPATH_FILTERS = {
        'not_empty': "string-length(translate(normalize-space(text()), ' ', ''))>0"
    }

    # template using when trying to get options from 'select' tag
    XPATH_TPLS = {
        'select': "//select[@id='{select_id}']/option[{filter}]"
    }

    def __init__(self, username, password, user, *args, **kwargs):
        """
        Init
        :param username: AHA account username 
        :param password: AHA account password
        :param user: current user 
        """
        super(AHAImporter, self).__init__(username, password, *args, **kwargs)
        self.user = user
        self.group_data = []

    def _get_options_by_select_id(self, select_id, remove_first=False):
        """
        Get non-empty options from select element
        :param select_id: id of 'select' tag
        :param remove_first: True, if need to remove first option in select
        (ex. '--select something--' option)
        :return: 
        """
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

    def _click_on_first_option(self, select_id):
        """
        Need to click on any option to show hidden elements
        :param select_id: id of 'select' element to click on it
        :return: 
        """
        xpath = self.XPATH_TPLS['select'].format(select_id=select_id, filter=self.XPATH_FILTERS['not_empty'])
        self.browser.find_element_by_xpath(xpath).click()

    def _get_course(self):
        """
        Get list of available courses
        :return: 
        """
        courses_list = self._get_options_by_select_id('courseId')
        course_obj = AHAField(type=AHAField.FIELD_TYPES.COURSE, value=courses_list, user=self.user)
        logging.info("Courses: {}".format(course_obj.value))
        self.group_data.append(course_obj)

    def _get_language(self):
        """
        Get list of available languages
        :return: 
        """
        languages_list = self._get_options_by_select_id('languageId')
        language_obj = AHAField(type=AHAField.FIELD_TYPES.LANGUAGE, value=languages_list, user=self.user)
        logging.info("Languages: {}".format(language_obj.value))
        self.group_data.append(language_obj)

    def _get_location(self):
        """
        Get list of available locations
        :return: 
        """
        locations_list = self._get_options_by_select_id('locationId', remove_first=True)
        location_obj = AHAField(type=AHAField.FIELD_TYPES.LOCATION, value=locations_list, user=self.user)
        logging.info("Locations: {}".format(location_obj.value))
        self.group_data.append(location_obj)

    def _get_tc(self):
        """
        Get list of available training centers
        :return: 
        """
        self._click_on_first_option(select_id='courseId')
        WebDriverWait(self.browser, 5).until(EC.presence_of_element_located((By.ID, 'tcNames')))
        tc_list = self._get_options_by_select_id('tcId')
        tc_obj = AHAField(type=AHAField.FIELD_TYPES.TC, value=tc_list, user=self.user)
        logging.info("Training Centers: {}".format(tc_obj.value))
        self.group_data.append(tc_obj)

    def _get_ts(self):
        """
        Get list of available training sites
        :return: 
        """
        self._click_on_first_option(select_id='tcId')
        WebDriverWait(self.browser, 5).until(EC.presence_of_element_located((By.ID, 'tsNames')))
        ts_list = self._get_options_by_select_id('tcSiteId')
        ts_obj = AHAField(type=AHAField.FIELD_TYPES.TS, value=ts_list, user=self.user)
        logging.info("Training Sites: {}".format(ts_obj.value))
        self.group_data.append(ts_obj)

    def _get_instructors(self):
        """
        Get list of available instructors
        :return: 
        """
        instructor_list = self._get_options_by_select_id('instructorId')
        instructor_obj = AHAField(type=AHAField.FIELD_TYPES.INSTRUCTOR, value=instructor_list, user=self.user)
        logging.info("Instructors: {}".format(len(instructor_list)))
        self.group_data.append(instructor_obj)

    def _get_fields(self):
        """
        Method to get all needed values 
        :return: 
        """
        logger.info("AHA Importing fields running")
        self._get_course()
        self._get_language()
        self._get_location()
        self._get_tc()
        self._get_ts()
        self._get_instructors()

    def _save_to_db(self):
        """
        Save received values to database
        :return: 
        """
        logging.info("Finish AHA Importing, saving")
        AHAField.objects.filter(user=self.user).delete()

        description_field = AHAField(type=AHAField.FIELD_TYPES.CLASS_DESCRIPTION, value=[], user=self.user)
        notes_field = AHAField(type=AHAField.FIELD_TYPES.CLASS_NOTES, value=[], user=self.user)

        other_fields = [description_field, notes_field]
        self.group_data.extend(other_fields)

        AHAField.objects.bulk_create(self.group_data)

    def run(self):
        """
        Start import process
        :return: 
        """
        # try to login and go to 'add class' page
        try:
            self._login()
            self._go_to_add_class_page()
        except:
            raise Exception("Sorry, your login data wrong, please try again")

        # try to get needed values from AHA and save it to databaase
        try:
            self._get_fields()
            self._save_to_db()
        except Exception as msg:
            logger.info("Error: {}".format(msg))
            raise Exception("Sorry, some trouble with data import")
