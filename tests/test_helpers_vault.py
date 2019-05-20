# -*- coding: utf-8 -*-
"""Module implements tests of :class:`~selenium_probes.helpers.vault.AzureKeyVault`."""
import re

import pytest

from requests.exceptions import ConnectionError

from selenium_probes.helpers.vault import AzureKeyVault


@pytest.fixture(
    scope="module",
    params=[
        {
            "description": "Service Principal credentials",
            "get_vars": {
                "vault_name": "VAULT_NAME",
                "app_id": "SP_APPID",
                "password": "SP_PWD",
                "tenant": "SP_TENANT",
            },
        },
        # {
        #     "description": "Managed Identity credentials",
        #     "get_vars": {"vault_name": "VAULT_NAME"},
        # },
    ],
)
def azure_vault(request, variables, logger):
    """Provide AzureKeyVault instance."""
    desc = request.param.get("description", None)
    init_kwargs = request.param.get("get_vars", None)

    for key, var in init_kwargs.items():
        init_kwargs.update({key: variables.get(var, None)})

    try:
        keyvault = AzureKeyVault(**init_kwargs)

    except Exception:
        logger.exception("AzureKeyVault() not properly initialized")
        yield None

    else:
        logger.info("AzureKeyVault() initialized with %s", desc)
        yield keyvault

    finally:
        logger.info("Destroy AzureKeyVault() instance with %s", desc)


@pytest.mark.filterwarnings(
    "ignore:inspect.getargspec.* is deprecated:DeprecationWarning"
)
@pytest.mark.usefixtures("logger")
class TestAzureKeyVault:
    """Test implementation of :class:`~selenium_probes.helpers.vault.AzureKeyVault`."""

    @pytest.mark.parametrize(
        "init_params",
        [
            pytest.param(
                {
                    "description": "Service Principal credentials",
                    "log_result": r"access Key Vault '\w+' with Service Principal",
                    "get_vars": {
                        "vault_name": "VAULT_NAME",
                        "app_id": "SP_APPID",
                        "password": "SP_PWD",
                        "tenant": "SP_TENANT",
                    },
                }
            ),
            pytest.param(
                {
                    "description": "Managed Identity credentials",
                    "log_result": r"access Key Vault '\w+' with Managed Identity",
                    "get_vars": {"vault_name": "VAULT_NAME"},
                },
                marks=pytest.mark.xfail(
                    raises=ConnectionError,
                    reason="Managed Identity only works within Azure environment",
                ),
            ),
            pytest.param(
                {
                    "description": "EMPTY vault_name",
                    "log_result": "Exception: must provide 'vault_name'",
                    "get_vars": {},
                },
                marks=pytest.mark.xfail(raises=ValueError, reason="Testing exception"),
            ),
        ],
    )
    def test_init_vault(self, caplog, variables, logger, init_params):
        """Test initialization with different types of credentials."""
        desc = init_params.get("description", None)
        log_result = init_params.get("log_result", None)
        init_kwargs = init_params.get("get_vars", None)

        for key, var in init_kwargs.items():
            init_kwargs.update({key: variables.get(var, None)})

        logger.info("Initialize AzureKeyVault with %s", desc)
        AzureKeyVault(**init_kwargs)

        assert bool(re.search(log_result, caplog.text))  # noqa

    @pytest.mark.usefixtures("azure_vault")
    @pytest.mark.parametrize(
        "secrets",
        [
            pytest.param(
                {
                    "secret_name": "probe-atlas-login-dev",
                    "secret_version": "e964ee19447c4bc581e68d7e76d8d0ae",
                    "expected_value": '{"USER":"test.avail","PASSWORD":"bus~octAg8"}',
                }
            ),
            pytest.param(
                {
                    "secret_name": "NONEXISTENT",
                    "secret_version": "",
                    "expected_value": "",
                }
            ),
            pytest.param(
                {"secret_name": None, "secret_version": "", "expected_value": ""},
                marks=pytest.mark.xfail(raises=ValueError, reason="Testing exception"),
            ),
        ],
    )
    def test_get_secret(self, caplog, logger, azure_vault, secrets):
        """Test getting a secret."""
        if isinstance(azure_vault, AzureKeyVault):
            secret_name = secrets.get("secret_name", None)
            secret_version = secrets.get("secret_version", None)
            expected_value = secrets.get("expected_value", None)

            logger.info(
                "Attempt to retrive secret '%s' of version '%s'",
                secret_name,
                secret_version,
            )

            secret = azure_vault.get_secret(
                secret_name=secret_name, secret_version=secret_version
            )
            if secret:
                logger.info("AzureKeyVault value returned: '%s'", secret.value)
                logger.info("AzureKeyVault value expected: '%s'", expected_value)
                assert secret.value == expected_value  # noqa
            else:
                assert "Secret not found" in caplog.text  # noqa
                logger.info(
                    "Secret '%s' of version '%s' NOT FOUND", secret_name, secret_version
                )
        else:
            logger.exception("Exception: no valid AzureKeyVault() supplied")
            pytest.skip("Skipping... no valid AzureKeyVault() supplied")

    @pytest.mark.usefixtures("azure_vault")
    @pytest.mark.parametrize(
        "secrets",
        [
            pytest.param(
                {
                    "secret_name": "probe-atlas-login-dev",
                    "secret_value": None,
                    "expected_value": None,
                },
                marks=pytest.mark.xfail(raises=ValueError, reason="Testing exception"),
            ),
            pytest.param(
                {"secret_name": None, "secret_value": "", "expected_value": ""},
                marks=pytest.mark.xfail(raises=ValueError, reason="Testing exception"),
            ),
            pytest.param(
                {
                    "secret_name": "probe-atlas-login-dev",
                    "secret_value": '{"USER":"test.avail","PASSWORD":"bus~octAg8"}',
                    "expected_value": '{"USER":"test.avail","PASSWORD":"bus~octAg8"}',
                }
            ),
        ],
    )
    def test_set_secret(self, caplog, logger, azure_vault, secrets):
        """Test setting a secret."""
        if isinstance(azure_vault, AzureKeyVault):
            secret_name = secrets.get("secret_name", None)
            secret_value = secrets.get("secret_value", None)
            expected_value = secrets.get("expected_value", None)

            logger.info(
                "Attempt to set secret '%s' to value '%s'", secret_name, secret_value
            )

            secret = azure_vault.set_secret(
                secret_name=secret_name, secret_value=secret_value
            )

            logger.debug("New secret value: '%s'", secret.value)

            assert secret.value == expected_value  # noqa

        else:
            logger.exception("Exception: no valid AzureKeyVault() supplied")
            pytest.skip("Skipping... no valid AzureKeyVault() supplied")
