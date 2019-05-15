# -*- coding: utf-8 -*-
"""Module exports generic probe implementation :class:`ProbeAbstract`.

:class:`ProbeAbstract` is used as a base class for all other probe subclasses.
It's main purpose is to provide a common interface for metric gathering. It also
establishes common probe properties like ``_probe_name`` or ``_probe_timeout``.

Example
-------
Use the module and :class:`ProbeAbstract` like this for more specific probe
implementations.

.. code-block:: python

    from selenium_probes.probes.probe_abstract import ProbeAbstract


    class ProbeUrl(ProbeAbstract):
        __logger = getLogger(__name__)

        def __init__(self, *args, url="http://duckduckgo.com", **kwargs):
            super(ProbeUrl, self).__init__(self, *args, **kwargs)

            self._url = url

        def run(self, browser=None):
            parent_success = super().run(browser)

            action_tag = "access_url"

            # get probe start timestamp
            timer_start = time()

            # execute probe logic
            result = self._run_actual_probing()

            # combine individual checks into overall probe success
            run_result = parent_success and result

            # get probe finish timestamp
            timer_stop = time()

            self._update_metrics(
                tag=action_tag, start=timer_start, finish=timer_stop, success=run_result
            )

            return run_result
"""
from logging import getLogger
from time import time


class ProbeAbstract:
    """Class for generic probe maintaining metrics.

    Performs no specific probing actions, should be used as an abstract
    base class by subclasses implementing specific probing actions.

    Attributes
    ----------
    __logger : :obj:`~logging.Logger`
        Channel to be used for log output specific to the module.

    _probe_name : :obj:`str`, optional
        Name of the probe to be reflected in metrics and logs.

    _probe_timeout : :obj:`int`, optional
        Seconds to wait for a web element or page to appear.

    _probe_metrics : :obj:`dict`
        Dictionary to store probe metrics.

    """

    __logger = getLogger(__name__)

    def __init__(self, *args, probe_name="noname", probe_timeout=10, **kwargs):
        """Initialize class instance.

        Keyword Arguments
        -----------------
        probe_name : :obj:`str`, optional
            Name of the probe to be reflected in metrics and logs.

        probe_timeout : :obj:`int`, optional
            Seconds to wait for a web element or page to appear.
            (default 10)

        """
        self._probe_name = probe_name
        self._probe_timeout = probe_timeout

        self._probe_metrics = {}

        self.__logger.debug(
            "Created instance from ProbeAbstract(%s)",
            ", ".join("{}='{}'".format(key, value) for key, value in locals().items()),
        )

    def _update_metrics(self, tag="", start=0.0, finish=0.0, success=False, **kwargs):
        """Record latest metrics.

        Updates metrics with provided values for specific action ``tag``. It allows
        to separate metrics of nested subclasses that extend abstract probe.

        Note
        ----
        ``tag`` should reference specific probe's action/phase (unique within the
        inheritance tree) implemented by a subclass with inheritance or composition
        (e.g. "init", "page_load", "form_submit", etc).

        Keyword Arguments
        -----------------
        tag : :obj:`str`
            Action tag to report metrics under.

        start : :obj:`float`
            UNIX epoch timestamp when probe started.

        finish : :obj:`float`
            UNIX epoch timestamp when probe finished.

        success : :obj:`bool`
            Flag indicating if probe executed successfully (:obj:`True`)
            or not (:obj:`False`).

        """
        metrics_dict = {}

        metrics_dict["success"] = success

        metrics_dict["timestamp_start"] = start
        metrics_dict["timestamp_finish"] = finish

        metrics_dict["duration"] = finish - start

        self._probe_metrics.update({tag: metrics_dict})

    @property
    def metrics(self):
        """:obj:`dict` Probe metrics to be exposed.

        Returns a dictionary of metrics organized by probe's name and action tag.

        """
        return {self._probe_name: self._probe_metrics}

    def run(self, browser=None):
        """Run abstract probe logic.

        Updates probe metrics and always reports success.

        Parameters
        ----------
        browser : :class:`~selenium_probes.helpers.browser.Browser`
            Instance to run probe actions on remote Selenium Grid node.

        Returns
        -------
        :obj:`bool`
            Flag indicating if :meth:`run()` was successfully executed or not.

        """
        action_tag = "init"

        timer_start = time()
        self.__logger.info(
            "Timer started for probe '%s:%s'", self._probe_name, action_tag
        )

        # abstract probe always reports success
        run_result = True

        timer_stop = time()
        self.__logger.info(
            "Timer stopped for probe '%s:%s'", self._probe_name, action_tag
        )

        self._update_metrics(
            tag=action_tag, start=timer_start, finish=timer_stop, success=run_result
        )

        return run_result
