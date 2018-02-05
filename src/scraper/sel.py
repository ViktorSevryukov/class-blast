from selenium import webdriver
import mechanicalsoup
import cookiejar
from http import cookies
from http.cookiejar import Cookie, CookieJar

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
        self.browser = webdriver.Firefox()

    def run(self):
        self.login()

    def login(self):
        self.browser.get(self.URLS['login'])
        self.browser.implicitly_wait(10)
        login_form = self.browser.find_element_by_id('userScreDiv')
        username_form = login_form.find_element_by_class_name('gigya-input-text')
        password_form = login_form.find_element_by_class_name('gigya-input-password')

        username_form.send_keys("jason.j.boudreault@gmail.com")
        password_form.send_keys("Thecpr1")
        login_form.find_element_by_class_name("gigya-input-submit").click()
        print("LOGIN SUCCESS")

    def get_course(self):
        self.browser.get(self.URLS['add_course'])
        fields_form = self.browser.find_element_by_id('courseId')
        courses = fields_form.find_element_by_class_name('/org/heart/ecc/handler/CCClassFormHandler.courseId')
        courses_list = {}
        for cours in courses:
            self.course_list.append(course)
        return courses

    def get_fields(self):
        return {
            'course': self.get_course(),
        }

if __name__ == '__main__':
    importer = AHAImporter(SETTINGS['username'], SETTINGS['password'])
    importer.run()



