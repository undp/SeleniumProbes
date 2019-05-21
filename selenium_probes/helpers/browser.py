# -*- coding: utf-8 -*-
r"""Module implements :class:`Browser` class to interact with Selenium WebDriver.

:class:`Browser` allows to manage interactions with Remote Selenium Grid
infrastructure using `Selenium WebDriver bindings for python`_. Its main
purpose is to ensure that upon destruction or error condition WebDriver is sent
a command to clear cookies and close the session.

Example
-------
Use the module and :class:`Browser` class like this to ensure resources are
deallocated when no longer required.
::

    from selenium_probes.helpers.browser import Browser
    from selenium.webdriver.common.desired_capabilities import DesiredCapabilities


    # Create a desired capabilities object as a starting point
    capabilities = DesiredCapabilities.CHROME.copy()
    capabilities['platform'] = "WINDOWS"
    capabilities['version'] = "10"

    # Browser object is properly destroyed at the exit from the `with` statement
    with Browser(
        se_endpoint="http://localhost:4444/wd/hub",
        se_capabilities=capabilities,
        page_load_timeout=30
    ) as b:
        # get URL
        b.webdriver.get("https://duckduckgo.com")

        # wait for HTML element `title` to appear and get it's attribute `innerHTML`
        (wait_success, attribute) = b.wait_for_element_get_attribute(
            element_xpath="/html/head/title",
            element_attribute="innerHTML",
            wait_timeout=5,
        )

        assert (b.webdriver.current_url == "https://duckduckgo.com"),\
            "Unexpected URL"

        assert (wait_success == true),\
            "Unexpected result waiting for HTML element '/html/head/title'"

        assert (attribute == "DuckDuckGo — Privacy, simplified."),\
            "Unexpected HTML element value"

        assert (b.webdriver.title == "DuckDuckGo — Privacy, simplified."),\
            "Unexpected title"

.. _Selenium WebDriver bindings for python:
   https://seleniumhq.github.io/selenium/docs/api/py/api.html

"""
from logging import getLogger

from selenium.common.exceptions import TimeoutException, WebDriverException
from selenium.webdriver import ChromeOptions, FirefoxOptions, Remote
from selenium.webdriver.common.by import By
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
from selenium.webdriver.support import expected_conditions
from selenium.webdriver.support.ui import WebDriverWait


class Browser:
    """Class for housekeeping of remote Selenium interactions.

    Initializes the session with the remote Selenium Grid node
    and properly closes it on instance destruction. Also allows
    to wait for specific HTML element and get its attribute.

    Attributes
    ----------
    _logger : :class:`~logging.Logger`
        Channel to be used for log output specific to the module.

    _browser : :obj:`WebDriver <selenium:selenium.webdriver.remote.webdriver>`
        Handle to operate remote Selenium Grid node (web browser).

    """

    def __init__(
        self,
        se_endpoint="http://localhost:4444/wd/hub",
        se_capabilities=DesiredCapabilities.CHROME,
        page_load_timeout=10,
    ):
        """Initialize connection to remote Selenium node with right capabilities.

        Parameters
        ----------
        se_endpoint : :obj:`str`, optional
            URL for Selenium Grid hub.
            (default 'http://localhost:4444/wd/hub')

        se_capabilities : :obj:`~selenium:selenium.webdriver.common.desired_capabilities.DesiredCapabilities`, optional  # noqa
            Capabilities of Selenium node indicating necessary browser type
            and configuration.
            (default ``DesiredCapabilities.CHROME``)

        page_load_timeout : :obj:`int`, optional
            Seconds to wait for page to load.
            (default 10)

        """
        self._logger = getLogger(__name__)
        self._browser = None

        # prepare to request headless WebDriver from Selenium
        if se_capabilities["browserName"] == "chrome":
            opts = ChromeOptions()
        elif se_capabilities["browserName"] == "firefox":
            opts = FirefoxOptions()

        opts.headless = True

        # connect to available Selenium node with correct capabilities
        try:
            self._browser = Remote(
                options=opts,
                command_executor=se_endpoint,
                desired_capabilities=se_capabilities,
            )
        except Exception:
            self._logger.exception(
                "Exception: failed to connect to remote Selenium instance"
            )
        else:
            # set page load timeout once for the whole session duration
            self._browser.set_page_load_timeout(page_load_timeout)

            self._logger.debug(
                "Created instance from %s(%s)",
                self.__class__.__name__,
                ", ".join(
                    "{}='{}'".format(key, value) for key, value in locals().items()
                ),
            )

    def __enter__(self):
        """Return class instance."""
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        """Gracefully close connection to Selenium on instance destruction."""
        if isinstance(self._browser, Remote):
            self._logger.debug("Delete all cookies and close Selenium session")

            self._browser.delete_all_cookies()
            self._browser.quit()

    @property
    def webdriver(self):
        """Return handler for remote Selenium WebDriver."""
        return self._browser

    def check_title(self, expected_title=None):
        """Check current browser title.

        Returns :obj:`True`, if `expected_title` string is in the browser's page title.
        If `expected_title` is not defined, just logs the title and returns :obj:`True`.

        Parameters
        ----------
        expected_title : :obj:`str`, optional
            String or sub-strng expected to be in the page title.
            (default :obj:`None`)

        Returns
        -------
        :obj:`bool`
            Check result (:obj:`True`, if match is found)

        """
        self._logger.info("page title: '%s'", self._browser.title)

        if expected_title is None:
            return True

        elif expected_title in self._browser.title:
            self._logger.info("page title match: '%s'", expected_title)
            return True

        else:
            self._logger.warning("page title DOES NOT match: '%s'", expected_title)
            return False

    def check_url(self, expected_url=None):
        """Check current browser URL.

        Returns :obj:`True`, if `expected_url` string is in the browser's current URL.
        If `expected_url` is not defined, just logs the URL and returns :obj:`True`.

        Parameters
        ----------
        expected_url : :obj:`str`, optional
            String or sub-strng expected to be in the current browser's URL.
            (default :obj:`None`)

        Returns
        -------
        :obj:`bool`
            Check result (:obj:`True`, if match is found)

        """
        self._logger.info("page url: '%s'", self._browser.current_url)

        if expected_url is None:
            return True

        elif expected_url in self._browser.current_url:
            self._logger.info("page url match: '%s'", expected_url)
            return True

        else:
            self._logger.warning("page url DOES NOT match: '%s'", expected_url)
            return False

    def wait_for_element_get_attribute(
        self,
        element_xpath="/html/head/title",
        element_attribute="innerHTML",
        wait_timeout=10,
    ):
        """Find element in browser DOM and get specified attribute/property from it.

        Waits for ``element_xpath`` to appear in DOM (i.e. after page load
        or some JavaScript action) in ``wait_timeout`` seconds, then returns
        ``element_attribute`` if element exists.

        Note
        ----
        With default parameters waits 10 sec for ``/html/head/title`` element to be
        present before capturing its property ``innerHTML``.

        In effect, waiting 10 sec for page to load and getting current title

        Parameters
        ----------
        element_xpath : :obj:`str`, optional
            XPATH of element to be located
            (default ``/html/head/title``)

        element_attribute : :obj:`str`, optional
            Name of attribute or property of located element to be returned
            (default ``innerHTML``)

        wait_timeout : :obj:`int`, optional
            Seconds to wait for element to appear.
            (default 10)

        Returns
        -------
        :obj:`bool`
            success flag (:obj:`True`, if element found)
        :obj:`str`
            content of attribute, or :obj:`None` if no attribute with that name

        """
        success = False
        attribute = None

        self._logger.debug("waiting for element @XPATH '%s'", element_xpath)

        # wait for element to be located at ``element_xpath``, then get
        # specified attribute ``element_attribute``
        try:
            element = WebDriverWait(self._browser, wait_timeout).until(
                expected_conditions.presence_of_element_located(
                    (By.XPATH, element_xpath)
                )
            )

        except (TimeoutException, WebDriverException):
            self._logger.exception(
                "Exception: waiting for element @XPATH '%s'", element_xpath
            )

        else:
            self._logger.debug(
                "found element @XPATH '%s', getting attribute '%s'",
                element_xpath,
                element_attribute,
            )

            success = True
            attribute = element.get_attribute(element_attribute)

        return success, attribute

    def wait_for_page_to_load(self):
        """Wait for page to load.

        Waiting the default timeout of :meth:`wait_for_element_get_attribute` for page
        to make the HTML title element available.

        Returns
        -------
        :obj:`bool`
            success flag (:obj:`True`, if page is loaded;
            :obj:`False`, if timeout occured)

        """
        (page_title_success, page_title) = self.wait_for_element_get_attribute()

        return page_title_success
