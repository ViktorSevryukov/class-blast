"""Example app to login to Enrollware using the StatefulBrowser class."""

import mechanicalsoup

LOGIN_URL = "https://www.enrollware.com/admin/login.aspx"
USERNAME = "gentrain"
PASSWORD = "enrollware"

browser = mechanicalsoup.StatefulBrowser(
    soup_config={'features': 'lxml'},
    raise_on_404=True,
    user_agent='MyBot/0.1: mysite.example.com/bot_info',
)
# Uncomment for a more verbose output:
# browser.set_verbose(2)

browser.open(LOGIN_URL)
browser.select_form('#login form')
browser["username"] = USERNAME
browser["password"] = PASSWORD
resp = browser.submit_selected()


page = browser.get_current_page()


HIDDEN_PAGE = 'https://www.enrollware.com/admin/class-edit.aspx?ret=class-list.aspx&id=2019614'


class_page = browser.open(HIDDEN_PAGE)
class_page = browser.get_current_page()

select_el = class_page.find("select", {'id':'mainContent_Course'})

option = select_el.find('option', selected=True)

print(option.text)

# print(class_page.text)
