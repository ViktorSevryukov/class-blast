from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC


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

    def login(self):
        self.selenium_browser.get(self.URLS['login'])
        self.selenium_browser.implicitly_wait(10)
        login_form = self.selenium_browser.find_element_by_id('userScreDiv')
        username_form = login_form.find_element_by_class_name('gigya-input-text')
        password_form = login_form.find_element_by_class_name('gigya-input-password')

        username_form.send_keys("jason.j.boudreault@gmail.com")
        password_form.send_keys("Thecpr1")
        login_form.find_element_by_class_name("gigya-input-submit").click()

        print("LOGIN SUCCESS")

    def jump_page(self):

        WebDriverWait(self.selenium_browser, 5).until(EC.text_to_be_present_in_element((By.TAG_NAME, "strong"), "Welcome!"))
        self.selenium_browser.get(self.URLS['add_course'])

    def get_course(self):

        course_list = self.selenium_browser.find_element_by_id('courseId')
        options = [x for x in course_list.find_elements_by_tag_name('option')]
        for element in options:
            print(element.get_attribute('text'))

    def get_language(self):

        language_list = self.selenium_browser.find_element_by_id('languageId')
        options = [x for x in language_list.find_elements_by_tag_name('option')]
        for element in options:
            print(element.get_attribute('text'))

    def get_location(self):
        # exclude "add new location"
        location_list = self.selenium_browser.find_element_by_id('locationId')
        options = [x for x in location_list.find_elements_by_tag_name('option')]
        for element in options:
            print(element.get_attribute('text'))


    def get_tc(self):

        # self.selenium_browser.find_element_by_id('courseId').find_element_by_tag_name('option').click()
        self.selenium_browser.find_element_by_xpath("//select[@id='courseId']/option[text()='Airway Management Course']").click()
        WebDriverWait(self.selenium_browser, 5).until(EC.element_to_be_selected('tcId'))
        # WebDriverWait(self.selenium_browser, 5).until(self.selenium_browser.find_element_by_tag_name('tcId'))

        tc_list = self.selenium_browser.find_element_by_tag_name('tcId')
        options = [x for x in tc_list.find_elements_by_tag_name('option')]
        for element in options:
            print(element.get_attribute('text'))


    def get_instructors(self):
        # self.selenium_browser.implicitly_wait(10)
        # self.selenium_browser.get(self.URLS['add_course'])

        # self.selenium_browser.find_element_by_id('courseId').find_element_by_tag_name('option').click()
        # self.selenium_browser.find_element_by_id('centers').find_element_by_tag_name('option').click()
        # self.selenium_browser.find_element_by_id('tsNames').find_element_by_tag_name('option').click()
        #
        # instructor_list = self.selenium_browser.find_element_by_tag_name('instructors')
        # options = [x for x in instructor_list.find_elements_by_tag_name('option')]
        # for element in options:
        #     print(element.get_attribute('text'))
        pass




    # def logout(self):
    #     self.selenium_browser.find_element_by_class_name("username hidden-xs").find_element_by_class_name("fa fa-sign-out").click()
    #     print("Log Out")





if __name__ == '__main__':
    importer = AHAImporter(SETTINGS['username'], SETTINGS['password'])
    importer.login()
    importer.jump_page()
    importer.get_course()
    importer.get_language()
    importer.get_location()
    importer.get_tc()
    importer.get_instructors()
    # importer.logout()
    # importer.browser_close()