# -*- coding: utf-8 -*-
"""Module exports HTML page probe implementation :class:`ProbePage`.

:class:`ProbePage` measures the time in seconds it takes to successfully
load targeted HTML page.

Note
----
Since Selenium drives the actual user browser, there is no straightforward way
to check that page has been loaded successfully. So, the implementation assumes
``loaded successfully`` means being able to match the page title to the
expected text and also allows to check for destination URL (e.g. when
redirected away from the initial one).

Example
-------
Use the module and :class:`ProbePage` like this:

.. code-block:: python

    from selenium_probes.probes.probe_page import ProbePage

    probe_page = ProbePage(
        probe_name="probe_page_duckduckgo",
        url="http://duckduckgo.com",
        expected_url="https://duckduckgo.com",
        expected_title="DuckDuckGo — Privacy, simplified.",
        probe_timeout=5,
    )

    probe_page_result = probe_page.run(browser)

    assert probe_page_result, "ProbePage() failed"
"""
from logging import getLogger
from time import time

from selenium.common.exceptions import TimeoutException, WebDriverException

from .probe_abstract import ProbeAbstract


class ProbePage(ProbeAbstract):
    """Class for HTTP page probe through WebDriver on remote Selenium Grid.

    Accesses initial :attr:`_url`, verifies that :attr:`_expected_title` is in
    the page title and :attr:`_expected_url` is in the final URL.

    Attributes
    ----------
    _logger : :obj:`~logging.Logger`
        Channel to be used for log output specific to the module.

    _url : :obj:`str`
        URL to be probed.

    _expected_title : :obj:`str`
        Portion of the title expected after probing.

    _expected_url : :obj:`str`
        Portion of the final URL expected after probing (e.g. after redirect).

    """

    __logger = getLogger(__name__)

    def __init__(self, *args, url="", expected_title=None, expected_url=None, **kwargs):
        """Initialize class instance.

        Keyword Arguments
        -----------------
        url : :obj:`str`
            URL to be probed.

        expected_title : :obj:`str`, optional
            Portion of title expected after probing.
            (default :obj:`None`)

        expected_url : :obj:`str`, optional
            Portion of final URL expected after probing (e.g. after redirect).
            (default :obj:`None`)

        """
        super(ProbePage, self).__init__(self, *args, **kwargs)

        self._url = url
        self._expected_title = expected_title
        self._expected_url = expected_url

        self.__logger.debug(
            "Created instance from ProbePage(%s)",
            ", ".join("{}='{}'".format(key, value) for key, value in locals().items()),
        )

    def run(self, browser=None):
        """Run HTML page probe logic.

        Gets page from :attr:`_url`, verifies that :attr:`_expected_title` is present
        and :attr:`_expected_url` is the final URL, updates metrics and reports status.

        Parameters
        ----------
        browser : :class:`~selenium_probes.helpers.browser.Browser`
            Instance to run probe actions on remote Selenium Grid node.

        Returns
        -------
        :obj:`bool`
            Flag indicating if :meth:`run()` was successfully executed or not.

        """
        init_success = super().run(browser)

        action_tag = "page_load"

        page_success = False
        title_success = False
        url_success = False

        timer_start = time()
        self.__logger.info(
            "Timer started for probe '%s:%s'", self._probe_name, action_tag
        )

        # note current page title and url for debugging
        self.__logger.debug("current page title '%s'", browser.webdriver.title)
        self.__logger.debug("current page url '%s'", browser.webdriver.current_url)

        self.__logger.info("requesting '%s'", self._url)

        try:
            browser.webdriver.get(self._url)

        except (TimeoutException, WebDriverException):
            self.__logger.exception("Exception: requesting page")

        else:
            # Ensure page loaded successfully
            page_success = browser.wait_for_page_to_load()

            if page_success:
                title_success = browser.check_title(self._expected_title)
                url_success = browser.check_url(self._expected_url)

        # combine individual checks into overall probe success
        run_result = init_success and page_success and title_success and url_success

        timer_stop = time()
        self.__logger.info(
            "Timer stopped for probe '%s:%s'", self._probe_name, action_tag
        )

        self._update_metrics(
            tag=action_tag, start=timer_start, finish=timer_stop, success=run_result
        )

        return run_result
