import requests
import selenium
from selenium import webdriver

import mechanicalsoup
from bs4 import BeautifulSoup

SETTINGS = {
    'username': 'jason.j.boudreault@gmail.com',
    'password': 'Thecpr1'
}


class AHAImporter:
    """
    """

    URLS = {
        'login': 'https://ahainstructornetwork.americanheart.org/AHAECC/ecc.jsp?pid=ahaecc.classconnector',
        'login2': 'https://sso.heart.org/account.html',

        'add_class': 'https://ahainstructornetwork.americanheart.org/AHAECC/ecc.jsp?pid=ahaecc.addClass'
        # 'classes_page': ADMIN_URL_TPL.format('class-list.aspx')
    }

    def __init__(self, username, password):
        self.username = username
        self.password = password
        self.browser = mechanicalsoup.StatefulBrowser(
            soup_config={'features': 'lxml'},
            raise_on_404=True,
            user_agent='MyBot/0.1: mysite.example.com/bot_info',
        )
        self.browser.set_verbose(2)

    def run(self):
        self.login()

    def login(self):
        # import requests
        # s = requests.Session()
        #
        # s.post(self.URLS['login2'], data={'username': self.username, 'password': self.password})
        #
        # r = s.get(self.URLS['add_class'])
        # soup = BeautifulSoup(r.text)
        # print(soup)

        self.browser.open(self.URLS['login2'])
        self.browser.set_user_agent('Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/63.0.3239.132 Safari/537.36')
        self.browser.session.headers.update(
            {'user-agent':'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/63.0.3239.132 Safari/537.36'}
            )
        response = requests.get(self.URLS['login2'], headers=self.browser.session.headers)
        print("OLOLO")
        print(response.content)

        self.browser.launch_browser()
        print(self.browser.session.headers)
        print("COOOOOOOOOKIE")
        print(self.browser.get_cookiejar())
        # self.browser.open(self.URLS['login2'])
        # self.browser.select_form('#login form')
        # self.browser['username'] = self.username
        # self.browser['password'] = self.password
        # self.browser.submit_selected()

    # TODO: remove method, just for test
    def print_current_page(self):
        page = self.browser.get_current_page()
        # print(self.browser.get_cookiejar())
        # print(page)
        print(page.find_all('div', {'class': 'page-content'}))



    #
    # def get_fields(self):
    #     return {
    #         'course': self.get_course(),
    #         'location': self.get_location(),
    #         'instructor': self.get_instructor(),
    #         'class_times': self.get_class_times(),
    #         'max_students': self.get_max_students()
    #     }


if __name__ == '__main__':
    importer = AHAImporter(SETTINGS['username'], SETTINGS['password'])
    importer.run()
    importer.print_current_page()