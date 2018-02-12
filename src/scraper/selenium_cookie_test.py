import cookiejar
from http import cookies




self.mbrowser = mechanicalsoup.StatefulBrowser(
            soup_config={'features': 'lxml'},
            raise_on_404=True,
            user_agent='MyBot/0.1: mysite.example.com/bot_info',
        )





def cookie_transit(self):
    self.mbrowser.set_cookiejar(self.catch_cookie())
    self.mbrowser.open(self.URLS['add_course'])
    self.mbrowser.launch_browser()
    print(self.mbrowser.get_current_page())
    # print(self.mbrowser.get_cookiejar())
    print("OPEN AHA")


def catch_cookie(self):
    cj = self.mbrowser.get_cookiejar()
    print("OLOLO TYPE", type(cj))
    # cj = CookieJar()
    cookas = self.browser.get_cookies()
    for c in cookas:
        new_cooka = Cookie(
            version=None,
            name=c['name'],
            value=c['value'],
            port=None,
            port_specified=None,
            domain=c['domain'],
            domain_specified=None,
            domain_initial_dot=None,
            path=c['path'],
            path_specified=None,
            secure=c['secure'],
            expires=c['expiry'],
            discard=None,
            comment=None,
            comment_url=None,
            rest=None
        )
        cj.set_cookie(new_cooka)

    print(cj)
    return cj