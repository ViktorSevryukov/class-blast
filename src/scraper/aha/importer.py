from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

from apps.core.models import AHAField
from scraper.aha.base import AHABase

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

    def __init__(self, username, password, *args, **kwargs):
        super(AHAImporter, self).__init__(username, password, *args, **kwargs)
        self.group_data = []

    def get_options_by_select_id(self, select_id, remove_first=False):
        # get non-empty options from select element
        xpath = self.XPATH_TPLS['select'].format(select_id=select_id, filter=self.XPATH_FILTERS['not_empty'])
        options = self.browser.find_elements_by_xpath(xpath)
        if remove_first:
            options.pop(0)
        values_list = [element.get_attribute('text') for element in options]
        return values_list

    def click_on_first_option(self, select_id):
        xpath = self.XPATH_TPLS['select'].format(select_id=select_id, filter=self.XPATH_FILTERS['not_empty'])
        self.browser.find_element_by_xpath(xpath).click()

    def get_course(self):
        courses_list = self.get_options_by_select_id('courseId')
        print("Courses:", courses_list)
        course_obj = AHAField(type='course', value=courses_list)
        return self.group_data.append(course_obj)

    def get_language(self):
        languages_list = self.get_options_by_select_id('languageId')
        print("Languages:", languages_list)
        language_obj = AHAField(type='language', value=languages_list)
        return self.group_data.append(language_obj)

    def get_location(self):
        locations_list = self.get_options_by_select_id('locationId', remove_first=True)
        print("Locations:", locations_list)
        location_obj = AHAField(type='location', value=locations_list)
        return self.group_data.append(location_obj)

    def get_tc(self):
        #TODO: search TC for each Course
        self.click_on_first_option(select_id='courseId')
        WebDriverWait(self.browser, 5).until(EC.presence_of_element_located((By.ID, 'tcNames')))
        tc_list = self.get_options_by_select_id('tcId')
        print("Training Centers:", tc_list)
        tc_obj = AHAField(type='tc', value=tc_list)
        return self.group_data.append(tc_obj)

    def get_ts(self):
        self.click_on_first_option(select_id='tcId')
        WebDriverWait(self.browser, 5).until(EC.presence_of_element_located((By.ID, 'tsNames')))
        ts_list = self.get_options_by_select_id('tcSiteId')
        print("Training Sites:", ts_list)
        ts_obj = AHAField(type='ts', value=ts_list)
        return self.group_data.append(ts_obj)

    def get_instructors(self):
        instructor_list = self.get_options_by_select_id('instructorId')
        print("Instructors:", instructor_list)
        instructor_obj = AHAField(type='instructor', value=instructor_list)
        return self.group_data.append(instructor_obj)

    def get_fields(self):
        self.get_course()
        self.get_language()
        self.get_location()
        self.get_tc()
        self.get_ts()
        self.get_instructors()

    def save_to_db(self):
        AHAField.objects.bulk_create(self.group_data)

    def run(self):
            self.login()
            self.go_to_add_class_page()
            self.get_fields()
            self.save_to_db()

if __name__ == '__main__':
    importer = AHAImporter(SETTINGS['username'], SETTINGS['password'])
    importer.run()