from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import Select

from apps.core.models import AHAField

SETTINGS = {
    'username': 'jason.j.boudreault@gmail.com',
    'password': 'Thecpr1'
}


class AHAImporter():
    """
    Class for import information info from AHA site
    """
    URLS = {
        'login': 'https://sso.heart.org/account.html',
        'add_course': 'https://ahainstructornetwork.americanheart.org/AHAECC/ecc.jsp?pid=ahaecc.addClass&_requestid=535927',
    }

    def __init__(self, username, password):
        self.username = username
        self.password = password
        self.selenium_browser = webdriver.Chrome()

        self.group_data = []

    def login(self):
        self.selenium_browser.get(self.URLS['login'])
        self.selenium_browser.implicitly_wait(10)

        #TODO: add wait for login form, or redirect right now to "add class URL'

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

    def get_course(self):

        all_courses = self.selenium_browser.find_element_by_id('courseId')
        options = [x for x in all_courses.find_elements_by_tag_name('option')]
        course_list = []
        for element in options:
            course_list.append(element.get_attribute('text'))

        course_list.pop(0)
        print("Courses:", course_list)
        course_obj = AHAField(type='course', value=course_list)
        return self.group_data.append(course_obj)

    def get_language(self):

        all_languages = self.selenium_browser.find_element_by_id('languageId')
        options = [x for x in all_languages.find_elements_by_tag_name('option')]
        language_list = []
        for element in options:
            language_list.append(element.get_attribute('text'))

        language_list.pop(0)
        print("Languages:", language_list)
        language_obj = AHAField(type='language', value=language_list)
        return self.group_data.append(language_obj)

    def get_location(self):

        all_locations = self.selenium_browser.find_element_by_id('locationId')
        options = [x for x in all_locations.find_elements_by_tag_name('option')]
        location_list = []
        for element in options:
            location_list.append(element.get_attribute('text'))
        location_list.remove('Add New Location')
        location_list.pop(0)

        print("Locations:", location_list)
        location_obj = AHAField(type='location', value=location_list)
        return self.group_data.append(location_obj)

    def get_tc(self):

        #TODO: search TC for each Course
        self.selenium_browser.find_element_by_xpath(
            "//select[@id='courseId']/option[text()='Airway Management Course']").click()

        WebDriverWait(self.selenium_browser, 5).until(EC.presence_of_element_located((By.ID, 'tcNames')))
        all_tc = self.selenium_browser.find_element_by_id('tcId')
        options = [x for x in all_tc.find_elements_by_tag_name('option')]
        tc_list = []
        for element in options:
            tc_list.append(element.get_attribute('text'))

        tc_list.pop(0)
        print("Training Centers:", tc_list)
        tc_obj = AHAField(type='tc', value=tc_list)
        return self.group_data.append(tc_obj)

    def get_ts(self):
        self.selenium_browser.find_element_by_xpath(
            "//select[@id='tcId']/option[text()='HeartShare Training Services Inc.']").click()

        WebDriverWait(self.selenium_browser, 5).until(EC.presence_of_element_located((By.ID, 'tsNames')))
        all_ts = self.selenium_browser.find_element_by_id('tcSiteId')
        options = [x for x in all_ts.find_elements_by_tag_name('option')]
        ts_list = []
        for element in options:
            ts_list.append(element.get_attribute('text'))

        ts_list.pop(0)
        print("Training Sites:", ts_list)
        ts_obj = AHAField(type='ts', value=ts_list)
        return self.group_data.append(ts_obj)

    def get_instructors(self):
        #TODO: change "HeartShare Training Services Inc." to var
        self.selenium_browser.find_element_by_xpath(
            "//select[@id='tcId']/option[text()='HeartShare Training Services Inc.']").click()

        WebDriverWait(self.selenium_browser, 5).until(EC.presence_of_element_located((By.ID, 'instructorId')))
        all_instructor = self.selenium_browser.find_element_by_id('instrNames')
        options = [x for x in all_instructor.find_elements_by_tag_name('option')]
        instructor_list = []
        for element in options:
            instructor_list.append(element.get_attribute('text'))

        instructor_list.pop(0)
        print("Instructors:", instructor_list)
        instructor_obj = AHAField(type='instructor', value=instructor_list)

        return self.group_data.append(instructor_obj)

    def save_to_db(self):
        AHAField.objects.bulk_create(self.group_data)

    def run(self):
        self.login()
        self.jump_page()
        self.get_course()
        self.get_language()
        self.get_location()
        self.get_tc()
        self.get_ts()
        self.get_instructors()
        self.save_to_db()
        print(self.group_data)

if __name__ == '__main__':
    importer = AHAImporter(SETTINGS['username'], SETTINGS['password'])
    importer.run()