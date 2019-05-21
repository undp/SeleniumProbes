# -*- coding: utf-8 -*-
"""Module exports HTML form probe implementation :class:`ProbeForm`.

:class:`ProbeForm` measures the time in seconds it takes to successfully
submit an HTML form. It relies on :class:`~probes.probe_page.ProbePage` to
load the target form page and collect corresponding metrics.

Note
----
Similar to the case with :class:`~selenium_probes.probes.probe_page.ProbePage`,
implementation assumes that ``success`` is when the resulting post-submit page
has a page title matching the expected text and post-submit URL matches the
expected one as well.

Example
-------
Use the module and :class:`ProbeForm` like this:

.. code-block:: python

    from selenium_probes.probes.probe_form import ProbeForm

    probe_form = ProbeForm(
        probe_name="probe_form_duckduckgo",
        url="http://duckduckgo.com",
        expected_url="https://duckduckgo.com",
        expected_title="DuckDuckGo — Privacy, simplified.",
        input_params={"q": "python testing"},
        submit_element="//input[@type='submit' and @value='S']",
        post_submit_title="real python testing at DuckDuckGo",
        post_submit_url="https://duckduckgo.com",
        probe_timeout=5,
    )

    probe_form_result = probe_form.run(browser)

    assert probe_form_result, "ProbeForm() failed"
"""
from logging import getLogger
from time import time

from selenium.common.exceptions import NoSuchElementException, TimeoutException
from selenium.webdriver.remote.webelement import WebElement

from .probe_page import ProbePage


class ProbeForm(ProbePage):
    """Class for HTTP form probe through WebDriver on remote Selenium Grid.

    Performs activity of the parent :class:`~probes.probe_page.ProbePage`, then goes
    through :attr:`_input_params` and enters values in corresponding input elements,
    then locates :attr:`_submit_element` and performs `WebElement.click()` on it. After
    post-submit page is loaded, verifies that :attr:`_post_submit_title` is in title
    and :attr:`_post_submit_url` is in the final URL.

    Attributes
    ----------
    _logger : :obj:`~logging.Logger`
        Channel to be used for log output specific to the module.

    _input_params : :obj:`dict`, optional
        Dictionary of input element names and values to submit.

    _submit_element : :obj:`str`
        String with XPATH to the form submitting element.

    _post_submit_title : :obj:`str`
        Portion of title expected after form is submitted.

    _post_submit_url : :obj:`str`
        Portion of final URL expected after form is submitted.

    """

    __logger = getLogger(__name__)

    def __init__(
        self,
        *args,
        input_params=None,
        submit_element="//input[@type='submit']",
        post_submit_title=None,
        post_submit_url=None,
        **kwargs
    ):
        """Initialize class instance.

        Keyword Arguments
        -----------------
        input_params : :obj:`dict`, optional
            Dictionary of input element names and values to submit.
            (default :obj:`None`)

        submit_element : :obj:`str`
            String with XPATH to the form submitting element.
            (default "//input[@type='submit'")

        post_submit_title : :obj:`str`
            Portion of title expected after form is submitted.
            (default :obj:`None`)

        post_submit_url : :obj:`str`
            Portion of final URL expected after form is submitted.
            (default :obj:`None`)

        """
        super(ProbeForm, self).__init__(self, *args, **kwargs)

        self._input_params = input_params
        self._submit_element = submit_element
        self._post_submit_title = post_submit_title
        self._post_submit_url = post_submit_url

        self.__logger.debug(
            "Created instance from ProbeForm(%s)",
            ", ".join("{}='{}'".format(key, value) for key, value in locals().items()),
        )

    def run(self, browser=None):
        """Run HTML form probe logic.

        Gets page, verifies title/url, finds present input elements matching
        :attr:`_input_params` dict keys, enters corresponding values, submits
        the form using located :attr:`_submit_element`, updates metrics and
        reports status.

        Parameters
        ----------
        browser : :class:`~selenium_probes.helpers.browser.Browser`
            Instance to run probe actions on remote Selenium Grid node.

        Returns
        -------
        :obj:`bool`
            Flag indicating if :meth:`run()` was successfully executed or not.

        """
        page_success = super().run(browser)

        action_tag = "form_submit"

        input_success = False
        submit_found = False
        submit_success = False
        title_success = False
        url_success = False

        timer_start = time()
        self.__logger.info(
            "Timer started for probe '%s:%s'", self._probe_name, action_tag
        )

        # proceed with form submission only if form was successfully loaded
        if page_success:
            input_success = True

            # iterate over input parameters
            for input_key, input_value in self._input_params.items():
                self.__logger.info(
                    "searching for input element with name '%s'", input_key
                )

                # find specific input element by name and enter corresponding value
                try:
                    input_element = browser.webdriver.find_element_by_name(input_key)
                except NoSuchElementException:
                    self.__logger.exception("Exception: find_element_by_name")

                    input_success = input_success and False

                else:
                    self.__logger.debug(
                        "found '%s', entering '%s'", input_key, input_value
                    )

                    input_element.send_keys(input_value)

                    input_success = input_success and True

            self.__logger.debug(
                "searching for element @XPATH '%s'", self._submit_element
            )

            # find form submitting element by XPATH
            try:
                input_element = browser.webdriver.find_element_by_xpath(
                    self._submit_element
                )

            except NoSuchElementException:
                self.__logger.exception("Exception: find_element_by_xpath")

            else:
                if isinstance(input_element, WebElement):
                    submit_found = True
                    self.__logger.info(
                        "found submit element @XPATH '%s', attempting to click()",
                        self._submit_element,
                    )

                    try:
                        input_element.click()

                    except TimeoutException:
                        self.__logger.exception("Exception: timeout submitting form")

                    else:
                        # Ensure page loaded successfully
                        submit_success = browser.wait_for_page_to_load()

                        if submit_success:
                            title_success = browser.check_title(self._post_submit_title)
                            url_success = browser.check_url(self._post_submit_url)

        # combine individual checks into overall probe success
        run_result = (
            page_success
            and input_success
            and submit_found
            and submit_success
            and title_success
            and url_success
        )

        timer_stop = time()
        self.__logger.info(
            "Timer stopped for probe '%s:%s'", self._probe_name, action_tag
        )

        self._update_metrics(
            tag=action_tag, start=timer_start, finish=timer_stop, success=run_result
        )

        return run_result
