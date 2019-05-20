# -*- coding: utf-8 -*-
"""Module defines a fixture for :class:`~selenium_probes.helpers.browser.Browser`."""
import time
from os import getenv

import pytest

from selenium.webdriver.common.desired_capabilities import DesiredCapabilities

from selenium_probes.helpers.browser import Browser


@pytest.fixture(scope="session")
def selenium_grid(request, dockerc, logger, service_name="hub"):
    """Wait for Selenium Hub service `service_name` to become available."""
    containers = dockerc.get_service(service_name).containers()
    if containers:
        hub_container = containers[0]

        if hub_container.is_running is True:
            logger.info("Selenium Grid Hub container '%s' started", hub_container.name)

            logger.info("Waiting 3 sec for service to converge...")
            time.sleep(3)

    else:
        logger.info("Docker service '%s' not running", service_name)


@pytest.fixture(
    scope="function", params=[DesiredCapabilities.CHROME, DesiredCapabilities.FIREFOX]
)
def test_browser(request, selenium_grid, logger):
    """Provide browser instance."""
    logger.info("Initialize Browser() instance...")

    with Browser(
        se_endpoint=getenv("SE_ENDPOINT", "http://localhost:4444/wd/hub"),
        page_load_timeout=int(getenv("PAGE_LOAD_TIMEOUT", 10)),
        se_capabilities=request.param,
    ) as browser:
        logger.info("Browser() initialized as '%s'", browser.webdriver.name)

        yield browser

    logger.info("Destroy Browser() instance of '%s'", browser.webdriver.name)
