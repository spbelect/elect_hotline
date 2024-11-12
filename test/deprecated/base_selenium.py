try:
    from selenium import webdriver
    from selenium.webdriver.support.wait import WebDriverWait
    from selenium.webdriver.remote.webelement import WebElement
    from selenium.common.exceptions import TimeoutException

    from pyvirtualdisplay import Display
except ImportError:
    pass
else:
    if getattr(settings, 'SELENIUM_XVFB_ENABLED', False):
        # Run all selenium tests in xvfb (browser window will be invisible)
        display = Display(visible=0, size=(800, 600))
        display.start()


TIMEOUT = getattr(settings, 'SELENIUM_TEST_TIMEOUT', 6)


def method_url_body(rcall):
    return (rcall.request.method, rcall.request.url, parse_qs(rcall.request.body))


def _find(self, selector):
    try:
        return self.find_element_by_css_selector(selector)
    except Exception:
        return None


def _findall(self, selector):
    return self.find_elements_by_css_selector(selector)


# # Monkey-patch selenium WebElement to have convenient find and findall methods to search children.
# WebElement.find = _find
# WebElement.findall = _findall


class BaseSeleniumTestCase(StaticLiveServerTestCase):
    """
    Base class for all selenium tests
    To configure default webdriver used, set SELENIUM_WEBDRIVER in your settings.py
    possible values: FALLBACK PhantomJS Firefox Chrome Opera
    default: FALLBACK - will try to find first working webdriver

    """

    @classmethod
    def setUpClass(cls):
        if not getattr(cls, '__unittest_skip__', False):
            webdriver_type = getattr(settings, 'SELENIUM_WEBDRIVER', 'FALLBACK')
            if webdriver_type == 'FALLBACK':
                for webdriver_type in 'Firefox PhantomJS Chrome Opera'.split():
                    try:
                        cls.webdrv = getattr(webdriver, webdriver_type)()
                    except Exception:
                        continue
                    break
                else:
                    raise Exception("Can't find any webdriver. Make sure that it is installed and in $PATH")
            else:
                cls.webdrv = getattr(webdriver, webdriver_type)()
        translation.activate(settings.LANGUAGE_CODE)

        super(BaseSeleniumTestCase, cls).setUpClass()
        cls.requestfactory = RequestFactory(SERVER_NAME=cls.server_thread.host, SERVER_PORT=cls.server_thread.port)

    @classmethod
    def tearDownClass(cls):
        translation.deactivate()
        if not getattr(cls, '__unittest_skip__', False):
            cls.webdrv.quit()
        super(BaseSeleniumTestCase, cls).tearDownClass()

    def find(self, selector):
        try:
            return self.webdrv.find_element_by_css_selector(selector)
        except Exception:
            return None

    def findall(self, selector):
        return self.webdrv.find_elements_by_css_selector(selector)

    def _assertWebElementMethod(self, selector, method, expected_result, wait_timeout=TIMEOUT):
        def condition(*args):
            elements = self.findall(selector)
            if elements:
                return all(item == expected_result for item in map(method, elements))
        WebDriverWait(self.webdrv, wait_timeout).until(condition)

    def assertVisible(self, selector, wait_timeout=TIMEOUT):
        try:
            self._assertWebElementMethod(selector, WebElement.is_displayed, True, wait_timeout)
        except TimeoutException:
            raise AssertionError('Element is missing or not visible: %s' % selector)

    def assertHidden(self, selector, wait_timeout=TIMEOUT):
        try:
            self._assertWebElementMethod(selector, WebElement.is_displayed, False, wait_timeout)
        except TimeoutException:
            raise AssertionError('Element is missing or not hidden: %s' % selector)

    def assertEnabled(self, selector, wait_timeout=TIMEOUT):
        try:
            self._assertWebElementMethod(selector, WebElement.is_enabled, True, wait_timeout)
        except TimeoutException:
            raise AssertionError('Element is missing or not enabled: %s' % selector)

    def assertDisabled(self, selector, wait_timeout=TIMEOUT):
        try:
            self._assertWebElementMethod(selector, WebElement.is_enabled, False, wait_timeout)
        except TimeoutException:
            raise AssertionError('Element is missing or not disabled: %s' % selector)

    def get(self, url):
        self.webdrv.get(self.live_server_url + str(url))

    def login(self, username, password):
        #self.get(settings.LOGIN_URL)
        self.find('#user-link').click()
        self.assertVisible('#user-email')
        self.find("#user-email").send_keys(username)
        self.assertEnabled('#user-pass')
        self.find("#user-pass").click()
        self.find('#user-pass-h').send_keys(password)
        self.assertEnabled('#sigin')
        self.find('#sigin').click()
        #self.assertEqual(self.webdrv.current_url, self.live_server_url + str(settings.LOGIN_REDIRECT_URL))

    @method_decorator(contextmanager)
    def frame(self, iframe_selector):
        """
        Contextmanager to switch webdriver inside iframe and back
        Usage:
        >>> with self.frame('iframe'):
        ...    # manipulate DOM inside iframe
        ...    self.find('#element_inside_iframe')
        ...
        """
        self.webdrv.switch_to.frame(self.find(iframe_selector))
        yield
        self.webdrv.switch_to.default_content()
