import logging
import mechanicalsoup

from urllib import parse
from concurrent import futures

from apps.core.models import *


logger = logging.getLogger('enroll')


class ClassImporter:
    """
    Class for import groups info from Enrollware site
    """
    ADMIN_URL_TPL = 'https://www.enrollware.com/admin/{}'

    # pages to parse
    URLS = {
        'login': ADMIN_URL_TPL.format('login.aspx'),
        'classes_page': ADMIN_URL_TPL.format('class-list.aspx')
    }

    MAX_WORKERS = 20

    ERROR_MESSAGE = "{} failed"

    def __init__(self, username, password, user):
        """
        Init importer class
        :param username: Enrollware account username
        :param password: Enrollware account password
        :param user: current user
        """
        self.username = username
        self.password = password
        self.user = user
        self.browser = mechanicalsoup.StatefulBrowser(
            soup_config={'features': 'lxml'},
            raise_on_404=True,
            user_agent='MyBot/0.1: mysite.example.com/bot_info',
        )
        self.class_page = None
        self.classes_data = []
        self.existing_groups = list(EnrollWareGroup.objects.filter(user=user).values_list('group_id', flat=True))

    @staticmethod
    def _get_select_value_by_id(page, select_id):
        """
        Get selected option value from tag <select> with specific id attribute
        :param page: soup object. Page to search on
        :param select_id: id of searching <select> tag
        :return: string
        """
        select = page.find('select', {'id': select_id})
        option = select.find('option', selected=True)

        if not option:
            return ""

        return option.text

    @staticmethod
    def _get_input_value_by_id(page, input_id):
        """
        Get value from tag <input> with specific id attribute
        :param page: soup object. Page to search on
        :param input_id: id of searching <select> tag
        :return: string
        """
        input_el = page.find('input', {'id': input_id})
        return input_el['value']

    def run(self):
        """
        Start import process from Enrollware
        :return: 
        """
        logger.info("EnrollWare Scraper starting")
        # try to login
        try:
            self._login()
            self._check_logged_in()
        except:
            raise Exception("Sorry, your login data wrong, please try again")

        # try to get info from classes
        try:
            self._handle_classes()
            self._save_groups_to_db()
        except:
            raise Exception("Sorry, there is some trouble with import groups")

    def _login(self):
        """
        Login to site
        :return: 
        """
        logger.info("Try to LogIn with username {}".format(self.username))
        self.browser.open(self.URLS['login'])
        self.browser.select_form('#login form')
        self.browser['username'] = self.username
        self.browser['password'] = self.password
        self.browser.submit_selected()

    @staticmethod
    def _get_group_id_from_url(url):
        """
        Get group id from url
        :param url: current url
        :return: 
        """
        group_id = int(parse.parse_qs(parse.urlparse(url).query)['id'][0])
        return group_id

    def _get_classes_urls(self):
        """
        Get classes urls to parse groups info
        :return: 
        """
        self.browser.open(self.URLS['classes_page'])
        classes_page = self.browser.get_current_page()
        classes_rows = classes_page.find('table', {'id': 'upcmgclstbl'})\
            .find('tbody').find_all('tr')
        classes_urls = []

        for row in classes_rows:
            url = self.ADMIN_URL_TPL.format(row.find('a').get('href'))
            group_id = self._get_group_id_from_url(url)

            if group_id in self.existing_groups:
                continue

            date_str = row.find('td').text
            date_str += 'm'
            datetime_object = datetime.strptime(date_str, '%a %m/%d/%y %I:%M%p')

            if (datetime_object - datetime.now()).days >= 3:
                classes_urls.append(url)
        return classes_urls

    def _check_logged_in(self):
        """
        Check is user logged in
        :return: 
        """
        current_url = self.browser.get_url()
        logger.info(" check is logged in")

        if self.URLS['classes_page'] != current_url:
            logger.info("invalid credentials")
            raise Exception('Sorry, it seems username or password not corrected')

    def _handle_class(self, url):
        """
        Get all needed data from class page
        :param url: url of current parsing class 
        :return: 
        """
        self.browser.open(url)
        self.class_page = self.browser.get_current_page()
        fields = self._get_fields()
        self.classes_data.append(self._prepare_group(fields))

    def _handle_classes(self):
        """
        Get all needed data from all classes
        :return: 
        """
        classes_urls = self._get_classes_urls()
        logger.info("Founded list urls count {}".format(len(classes_urls)))
        if len(classes_urls) == 0:
            logger.info('new groups not found')
            return 0
        workers = min(self.MAX_WORKERS, len(classes_urls))
        with futures.ThreadPoolExecutor(workers) as executor:
            res = executor.map(self._handle_class, classes_urls)
        handled_count = len(list(res))
        logger.info("Handled classes count: {}".format(handled_count))
        return handled_count

    def _prepare_group(self, group_fields):
        """
        Prepare group data to save in database (EnrollwareGroup)
        :param group_fields: 
        :return: 
        """
        start_time, end_time = self._prepare_class_time(group_fields['class_times'])
        return EnrollWareGroup(
            user=self.user,
            group_id=group_fields['group_id'],
            course=group_fields['course'],
            location=group_fields['location'],
            instructor=group_fields['instructor'],
            max_students=group_fields['max_students'],
            status=EnrollWareGroup.STATUS_CHOICES.UNSYNCED,
            available_to_export=self.user.version == self.user.VERSIONS.PRO,
            start_time=start_time,
            end_time=end_time
        )

    def _prepare_class_time(self, class_time):
        """
        Prepare class time from class page
        :param class_time: class time in enrollware format
        :return:
        """
        start_time = "{} {}:{} {}".format(
            class_time['date'],
            class_time['from']['hour'],
            class_time['from']['minute'],
            class_time['from']['am_pm']
        )
        end_time = "{} {}:{} {}".format(
            class_time['date'],
            class_time['to']['hour'],
            class_time['to']['minute'],
            class_time['to']['am_pm']
        )

        start_time = datetime.strptime(start_time, "%m/%d/%Y %I:%M %p")
        end_time = datetime.strptime(end_time, "%m/%d/%Y %I:%M %p")

        return start_time, end_time

    def _save_groups_to_db(self):
        """
        Create objects in database (EnrollWareGroups)
        :return: 
        """
        logger.info('try to save groups')

        if self.classes_data:
            EnrollWareGroup.objects.bulk_create(self.classes_data)

    def _get_fields(self):
        """
        Get all needed values from class page 
        :return: 
        """
        return {
            'group_id': self._get_group_id(),
            'course': self._get_course(),
            'location': self._get_location(),
            'instructor': self._get_instructor(),
            'class_times': self._get_class_times(),
            'max_students': self._get_max_students(),
        }

    def _get_group_id(self):
        """
        Get group id
        :return: 
        """
        url = self.browser.get_url()
        logging.info("Group id:{}".format(self._get_group_id_from_url(url)))
        return self._get_group_id_from_url(url)

    def _get_course(self):
        """
        Get course value
        :return: 
        """
        select_id = 'mainContent_Course'
        logging.info("Course: {}".format(self._get_select_value_by_id(self.class_page, select_id)))
        return self._get_select_value_by_id(self.class_page, select_id)

    def _get_location(self):
        """
        Get location value
        :return: 
        """
        select_id = 'mainContent_Location'
        logging.info("Location: {}".format(self._get_select_value_by_id(self.class_page, select_id)))
        return self._get_select_value_by_id(self.class_page, select_id)

    def _get_instructor(self):
        """
        Get instructor value
        :return: 
        """
        select_id = 'mainContent_instructorId'
        instructor = self._get_select_value_by_id(self.class_page, select_id)
        if instructor == "--Choose--":
            logger.info("No instructor, {}, {}".format(self._get_course(), self._get_group_id()))
            return "No instructor"

        logging.info("Instructor: {}".format(instructor))
        return instructor

    def _get_class_times(self):
        """
        TODO: Need to parse list of several class times, now we get only first record.
        Maybe we can use '_cts{x}_' where 'x' == position of the row with 
        class time. Anyway, need to create group with several class times and 
        analyze its HTML  
        """

        class_time = {
            'date': self._get_input_value_by_id(
                self.class_page, 'mainContent_startDate'
            ),
            'from': {
                'hour': self._get_select_value_by_id(
                    self.class_page, 'mainContent_startHour'
                ),
                'minute': self._get_select_value_by_id(
                    self.class_page, 'mainContent_startMinute'
                ),
                'am_pm': self._get_select_value_by_id(
                    self.class_page, 'mainContent_startAMPM'
                )
            },
            'to': {
                'hour': self._get_select_value_by_id(
                    self.class_page, 'mainContent_endHour'
                ),
                'minute': self._get_select_value_by_id(
                    self.class_page, 'mainContent_endMinute'
                ),
                'am_pm': self._get_select_value_by_id(
                    self.class_page, 'mainContent_endAMPM'
                )
            }
        }

        logging.info("Class time: {}".format(class_time))
        return class_time

    def _get_max_students(self):
        """
        Get 'max students' value
        :return: 
        """
        input_id = 'mainContent_maxEnrollment'
        try:
            logging.info("Student limit: {}".format(self._get_input_value_by_id(self.class_page, input_id)))
            return self._get_input_value_by_id(self.class_page, input_id)
        except:
            logging.info("Student limit: 0")
            return 0
