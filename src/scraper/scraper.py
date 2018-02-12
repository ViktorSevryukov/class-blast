import time
import mechanicalsoup

from concurrent import futures
from datetime import datetime, timedelta

# SETTINGS = {
#     'username': 'gentrain',
#     'password': 'enrollware'
# }


SETTINGS = {
    'username': 'v.akins',
    'password': 'password1234'
}

def get_select_value_by_id(page, select_id):
    """
    Get selected option value from tag <select> with specific id attribute
    :param page: soup object. Page to search on
    :param select_id: id of searching <select> tag
    :return: string
    """
    select = page.find('select', {'id': select_id})
    option = select.find('option', selected=True)
    return option.text


def get_input_value_by_id(page, input_id):
    """
    Get value from tag <input> with specific id attribute
    :param page: soup object. Page to search on
    :param input_id: id of searching <select> tag
    :return: string
    """
    input_el = page.find('input', {'id': input_id})
    return input_el['value']


class ClassImporter:
    """
    Class for import groups info from Enrollware site
    """
    ADMIN_URL_TPL = 'https://www.enrollware.com/admin/{}'

    URLS = {
        'login': ADMIN_URL_TPL.format('login.aspx'),
        'classes_page': ADMIN_URL_TPL.format('class-list.aspx')
    }

    MAX_WORKERS = 20

    def __init__(self, username, password):
        self.username = username
        self.password = password
        self.browser = mechanicalsoup.StatefulBrowser(
            soup_config={'features': 'lxml'},
            raise_on_404=True,
            user_agent='MyBot/0.1: mysite.example.com/bot_info',
        )
        self.class_page = None
        self.classes_data = []

    def run(self):
        self.login()
        self.handle_classes()
        return self.classes_data

    def login(self):
        self.browser.open(self.URLS['login'])
        self.browser.select_form('#login form')
        self.browser['username'] = self.username
        self.browser['password'] = self.password
        self.browser.submit_selected()

    def get_classes_urls(self):
        self.browser.open(self.URLS['classes_page'])
        classes_page = self.browser.get_current_page()
        classes_rows = classes_page.find('table', {'id': 'upcmgclstbl'}).find('tbody').find_all('tr')
        classes_urls = []

        for row in classes_rows:
            #TODO: refactor table rows (in case of table structure be changed)
            date_str = row.find('td').text
            date_str += 'm'
            datetime_object = datetime.strptime(date_str, '%a %m/%d/%y %I:%M%p')

            #TODO: correct time interval
            # if (datetime.now() - datetime_object).days >= 0:
                # print(datetime_object)
            url = self.ADMIN_URL_TPL.format(row.find('a').get('href'))
            classes_urls.append(url)
        print(len(classes_urls))
        return classes_urls

    def handle_class(self, url):
        self.browser.open(url)
        self.class_page = self.browser.get_current_page()
        self.classes_data.append(self.get_fields())

    def handle_classes(self):
        classes_urls = self.get_classes_urls()
        workers = min(self.MAX_WORKERS, len(classes_urls))
        with futures.ThreadPoolExecutor(workers) as executor:
            res = executor.map(self.handle_class, classes_urls)
        return len(list(res))

        # TODO: uncomment when ready to work, now just parse one group
        # Without threads begin
        # for class_url in classes_urls:
        #     # class_url = classes_urls[0]  # just for test
        #     self.browser.open(class_url)
        #     self.class_page = self.browser.get_current_page()
        #     self.classes_data.append(self.get_fields())
        # return self.classes_data
        # Without threads end

    def get_fields(self):
        return {
            'course': self.get_course(),
            'location': self.get_location(),
            'instructor': self.get_instructor(),
            'class_times': self.get_class_times(),
            'max_students': self.get_max_students()
        }

    def get_course(self):
        select_id = 'mainContent_Course'
        return get_select_value_by_id(self.class_page, select_id)

    def get_location(self):
        select_id = 'mainContent_Location'
        return get_select_value_by_id(self.class_page, select_id)

    def get_instructor(self):
        select_id = 'mainContent_instructorId'
        return get_select_value_by_id(self.class_page, select_id)

    def get_class_times(self):

        # TODO: see below
        """
        TODO: Need to parse list of several class times, now we get only first record.
        Maybe we can use '_cts{x}_' where 'x' == position of the row with 
        class time. Anyway, need to create group with several class times and 
        analyze its HTML  
        """
        class_date = get_input_value_by_id(
            self.class_page, 'mainContent_startDate'
        )
        class_time = {
            'from': {
                'hour': get_select_value_by_id(
                    self.class_page, 'mainContent_startHour'
                ),
                'minute': get_select_value_by_id(
                    self.class_page, 'mainContent_startMinute'
                ),
                'am_pm': get_select_value_by_id(
                    self.class_page, 'mainContent_startAMPM'
                )
            },
            'to': {
                'hour': get_select_value_by_id(
                    self.class_page, 'mainContent_endHour'
                ),
                'minute': get_select_value_by_id(
                    self.class_page, 'mainContent_endMinute'
                ),
                'am_pm': get_select_value_by_id(
                    self.class_page, 'mainContent_endAMPM'
                )
            }
        }

        class_times = {'date': class_date, 'time': class_time}

        return class_times

    #TODO: fix invalid group.max_students
    def get_max_students(self):

        input_id = 'mainContent_maxEnrollment'
        try:
            return get_input_value_by_id(self.class_page, input_id)
        except:
            return 0  # print("Links", self.browser.get_url())


if __name__ == '__main__':
    importer = ClassImporter(SETTINGS['username'], SETTINGS['password'])
    t0 = time.time()
    importer.run()

    print(time.time() - t0, ' seconds')
