# -*- coding: utf-8 -*-
"""Test suite for :mod:`probes`."""
from os import getenv

import pytest

from selenium.webdriver import Remote

from selenium_probes.probes.probe_abstract import ProbeAbstract
from selenium_probes.probes.probe_form import ProbeForm
from selenium_probes.probes.probe_page import ProbePage

pytest_plugins = ["tests.fixtures.test_browser"]


@pytest.fixture(
    scope="module",
    params=[
        {"probe": ProbeAbstract, "probe_name": "probe_abstract", "probe_success": True},
        {
            "probe": ProbePage,
            "probe_name": "probe_page_no_check",
            "probe_url": "http://duckduckgo.com",
            "probe_success": True,
        },
        {
            "probe": ProbePage,
            "probe_name": "probe_page_fail_check",
            "probe_url": "http://duckduckgo.com",
            "probe_expected_url": "http://does-not-match.org",
            "probe_expected_title": "Does not match",
            "probe_success": False,
        },
        {
            "probe": ProbePage,
            "probe_name": "probe_page_check",
            "probe_url": "http://duckduckgo.com",
            "probe_expected_url": "https://duckduckgo.com",
            "probe_expected_title": "DuckDuckGo — Privacy, simplified.",
            "probe_success": True,
        },
        {
            "probe": ProbePage,
            "probe_name": "probe_page_timeout",
            "probe_url": "http://httpbin.org/delay/10",
            "probe_success": False,
        },
        {
            "probe": ProbeForm,
            "probe_name": "probe_form_no_check",
            "probe_url": "http://duckduckgo.com",
            "probe_input_params": {"q": "real python testing"},
            "probe_submit_element": "//input[@type='submit' and @value='S']",
            "probe_post_submit_title": "real python testing at DuckDuckGo",
            "probe_post_submit_url": "https://duckduckgo.com",
            "probe_success": True,
        },
        {
            "probe": ProbeForm,
            "probe_name": "probe_form_fail_pre_check",
            "probe_url": "http://duckduckgo.com",
            "probe_expected_url": "http://does-not-match.org",
            "probe_expected_title": "Does not match",
            "probe_input_params": {"q": "real python testing"},
            "probe_submit_element": "//input[@type='submit' and @value='S']",
            "probe_post_submit_title": "real python testing at DuckDuckGo",
            "probe_post_submit_url": "https://duckduckgo.com",
            "probe_success": False,
        },
        {
            "probe": ProbeForm,
            "probe_name": "probe_form_check",
            "probe_url": "http://duckduckgo.com",
            "probe_expected_url": "https://duckduckgo.com",
            "probe_expected_title": "DuckDuckGo — Privacy, simplified.",
            "probe_input_params": {"q": "real python testing"},
            "probe_submit_element": "//input[@type='submit' and @value='S']",
            "probe_post_submit_title": "real python testing at DuckDuckGo",
            "probe_post_submit_url": "https://duckduckgo.com",
            "probe_success": True,
        },
        {
            "probe": ProbeForm,
            "probe_name": "probe_form_fail_post_check",
            "probe_url": "http://duckduckgo.com",
            "probe_expected_url": "https://duckduckgo.com",
            "probe_expected_title": "DuckDuckGo — Privacy, simplified.",
            "probe_input_params": {"q": "real python testing"},
            "probe_submit_element": "//input[@type='submit' and @value='S']",
            "probe_post_submit_title": "Does not match",
            "probe_post_submit_url": "http://does-not-match.org",
            "probe_success": False,
        },
        {
            "probe": ProbeForm,
            "probe_name": "probe_form_fail_input",
            "probe_url": "https://duckduckgo.com",
            "probe_input_params": {
                "q": "real python testing",
                "nonexistent": "does not matter",
            },
            "probe_submit_element": "//input[@type='submit' and @value='S']",
            "probe_success": False,
        },
        {
            "probe": ProbeForm,
            "probe_name": "probe_form_fail_submit",
            "probe_url": "https://duckduckgo.com",
            "probe_input_params": {"q": "real python testing"},
            "probe_submit_element": "//input[@type='submit' and @value='nonexistent']",
            "probe_success": False,
        },
    ],
)
def test_probe(request):
    """Provide probe instance."""
    probe = request.param["probe"](
        probe_timeout=int(getenv("PROBE_TIMEOUT", 5)),
        probe_name=request.param.get("probe_name", "noname"),
        url=request.param.get("probe_url", None),
        expected_url=request.param.get("probe_expected_url", None),
        expected_title=request.param.get("probe_expected_title", None),
        input_params=request.param.get("probe_input_params", None),
        submit_element=request.param.get("probe_submit_element", None),
        post_submit_title=request.param.get("probe_post_submit_title", None),
        post_submit_url=request.param.get("probe_post_submit_url", None),
    )

    probe_success = request.param.get("probe_success", True)

    return probe, probe_success


@pytest.mark.usefixtures("logger")
@pytest.mark.usefixtures("test_browser")
class TestProbe:
    """Implements tests for probes."""

    @pytest.mark.usefixtures("test_probe")
    def test_probe_run(self, caplog, logger, test_probe, test_browser):
        """Test probe execution."""
        (probe, expected_result) = test_probe

        logger.info("Using '%s' probe", probe.__class__.__name__)
        logger.info("Using '%s' browser", test_browser.webdriver.name)

        if isinstance(test_browser.webdriver, Remote):
            logger.info("Invoke `probe.run()`")
            test_result = probe.run(test_browser)
            logger.info("Metrics received: %s", probe.metrics)

            assert test_result is expected_result, "Unexpected probe result"  # noqa

        else:
            logger.exception("Exception: Remote WebDriver not properly initialized")

            pytest.skip("Skipping 'test_probe_run'")
