# -*- coding: utf-8 -*-
"""Module implements tests of :class:`~selenium_probes.helpers.browser.Browser`."""
from os import getenv

import pytest

from selenium.common.exceptions import WebDriverException
from selenium.webdriver import Remote
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities

from selenium_probes.helpers.browser import Browser


pytest_plugins = ["tests.fixtures.test_browser"]


@pytest.mark.usefixtures("logger")
class TestBrowser:
    """Test case for :class:`~selenium_probes.helpers.browser.Browser`."""

    test_url = "http://duckduckgo.com"
    test_title = "DuckDuckGo — Privacy, simplified."
    test_url_notitle = "http://httpbin.org/status/200"
    se_endpoint_not_avail = "http://127.0.0.1:1111/wd/hub"

    @pytest.mark.usefixtures("test_browser")
    @pytest.mark.parametrize(
        "test_params",
        [
            {"url": test_url, "title": test_title},
            {"url": test_url_notitle, "title": None},
        ],
    )
    def test_browser_wait(self, caplog, logger, test_browser, test_params):
        """Test waiting for element and getting corresponding attribute."""
        logger.info("Using '%s' browser", test_browser.webdriver.name)

        if isinstance(test_browser.webdriver, Remote):
            logger.info("Request '%s'", test_params["url"])
            test_browser.webdriver.get(test_params["url"])

            logger.info("Invoke 'wait_for_element_get_attribute()'")
            (success, title) = test_browser.wait_for_element_get_attribute(
                wait_timeout=1
            )

            if test_params["title"] is not None:
                assert success  # noqa
                assert title == test_params["title"]  # noqa
            else:
                assert not success  # noqa
                assert title is None  # noqa
                assert (  # noqa
                    "Exception: waiting for element @XPATH '/html/head/title'"
                    in caplog.text
                )
        else:
            logger.exception("Exception: Remote WebDriver not properly initialized")

            pytest.skip("Skipping 'test_browser_wait'")

    @pytest.mark.parametrize(
        "browser_capabilities",
        [DesiredCapabilities.CHROME, DesiredCapabilities.FIREFOX],
    )
    def test_connection_failure(self, caplog, logger, browser_capabilities):
        """Tests failure to connect to remote Selenium Grid instance."""
        logger.info("Initialize Browser() instance with non-existent endpoint")

        b = Browser(
            se_endpoint=self.se_endpoint_not_avail,
            se_capabilities=browser_capabilities,
            page_load_timeout=30,
        )

        assert b.webdriver is None  # noqa
        assert (  # noqa
            "Exception: failed to connect to remote Selenium instance" in caplog.text
        )

    @pytest.mark.parametrize(
        "browser_capabilities",
        [DesiredCapabilities.CHROME, DesiredCapabilities.FIREFOX],
    )
    def test_graceful_closure(self, logger, browser_capabilities):
        """Tests graceful disconnect from Selenium when instance destroyed."""
        with Browser(
            se_endpoint=getenv("SE_ENDPOINT", "http://localhost:4444/wd/hub"),
            se_capabilities=browser_capabilities,
            page_load_timeout=int(getenv("PAGE_LOAD_TIMEOUT", 30)),
        ) as browser:
            if isinstance(browser.webdriver, Remote):
                logger.info("Browser() instance initialized")
                logger.info("Accessing test URL '%s' to get page title", self.test_url)

                browser.webdriver.get(self.test_url)

                assert browser.webdriver.title == self.test_title  # noqa

                logger.info("Resulting browser title: '%s'", browser.webdriver.title)

            else:
                logger.exception("Exception: Remote WebDriver not properly initialized")

                pytest.skip("Skipping: Remote WebDriver not properly initialized")

        logger.info("Browser() instance destroyed")

        logger.info(
            "Accessing test URL '%s' to raise WebDriverException", self.test_url
        )

        with pytest.raises(
            WebDriverException,
            match="was terminated due to CLIENT_STOPPED_SESSION|No active session",
        ):
            browser.webdriver.get(self.test_url)
