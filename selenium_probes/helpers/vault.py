# -*- coding: utf-8 -*-
r"""Module exports :class:`AzureKeyVault` to interact with Azure Key Vault.

:class:`AzureKeyVault` allows to retrieve and update Azure Key Vault secrets.
It uses two authentication methods for access:

    * Service Principal
    * Managed Identity

Warning
-------
Service Principal (SP) is the equivalent of login/password credentials. So,
hard-coding SP in the code or configuration to facilitate external retrieval of
required credentials from the Key Vault is as good as hard-coding those
actual credentials directly. SP authentication should only be used for
DEV environments.

Example
-------
Use the module and :class:`AzureKeyVault` like this:
::

    import os
    from logging import getLogger

    from selenium_probes.helpers.vault import AzureKeyVault


    _logger = getLogger(__name__)

    # if testing, get secret from environment variable `TESTING_SECRET`
    if os.environ['ENV'] == 'testing':
        secret = os.environ['TESTING_SECRET']

    else:
        try:
            # if production, get secret from the Key Vault with Managed Identity
            if  os.environ['ENV'] == 'production':
                vault = AzureKeyVault(
                    vault_name=os.environ['VAULT_NAME'],
                )

            # if development, get secret from the Key Vault with Service Principal
            elif  os.environ['ENV'] == 'development':
                vault = AzureKeyVault(
                    vault_name=os.environ['VAULT_NAME'],
                    app_id=os.environ['SP_APPID'],
                    password=os.environ['SP_PWD'],
                    tenant=os.environ['SP_TENANT'],
                )
        except Exception as e:
            _logger.exception(
                "Exception: AzureKeyVault not properly initialized: {}".
                format(e))
        else:
            if not isinstance(vault, AzureKeyVault):
                _logger.exception("AzureKeyVault not properly initialized")

            secret = vault.get_secret(
                secret_name=os.environ['VAULT_SECRET'],
                secret_version='',
            )

"""

from logging import getLogger

from azure.keyvault import KeyVaultClient
from azure.keyvault.models import KeyVaultErrorException

from msrestazure.azure_active_directory import (
    MSIAuthentication,
    ServicePrincipalCredentials,
)


class AzureKeyVault:
    """Class to interact with the Azure Key Vault service.

    Relies on the Managed Identity access token to interact with the Key Vault.
    If used outside of the Azure environment (e.g. for development or testing),
    requires Service Principal to be defined.

    Warning
    -------
    Use Service Principal authentication only for DEV environments! It is as secure as
    hard-coding secrets into the code or application configuration.

    Attributes
    ----------
    _logger : :obj:`~logging.Logger`
        Channel to be used for log output specific to the module.

    _vault_name : :obj:`str`
        Name of Azure Key Vault to access.

    _service_principal : :obj:`dict`
        Service Principal credentials with access rights to Azure Key Vault,
        if provided. See :meth:`__init__` for more details

    _vault_creds : :obj:`BasicTokenAuthentication`
        Key Vault access token obtained either through
        Managed Identity (:obj:`MSIAuthentication`) or
        Service Principal (:obj:`ServicePrincipalCredentials`) authentication.

    _vault_uri : :obj:`str`
        Key Vault URI to query.

    _vault_client : :obj:`KeyVaultClient`
        Client instance to interact with Key Vault.

    """

    """Standard API endpoint URI for Azure Key Vault resource."""
    __AZURE_RESOURCE_KEYVAULT = "https://vault.azure.net"

    def __init__(self, **kwargs):
        """Initialize instance, get correct Key Vault access credentials.

        Keyword Arguments
        -----------------
        vault_name : :obj:`str`
            Name of Key Vault to access

        app_id : :obj:`str`, optional
            Service Principal ``appId`` to access Key Vault outside Azure
            (default :obj:`None`)

        password : :obj:`str`, optional
            Service Principal ``password`` to access Key Vault outside Azure
            (default :obj:`None`)

        tenant : :obj:`str`, optional
            Service Principal ``tenant`` for Azure Subscription
            (default :obj:`None`)
        """
        self._logger = getLogger(__name__)

        self._vault_name = kwargs.get("vault_name", None)
        if self._vault_name is None:
            self._logger.exception(
                "Exception: must provide 'vault_name' as a keyword argument"
            )
            raise ValueError("must provide 'vault_name' as a keyword argument")
        else:
            self._service_principal = {
                "app_id": kwargs.get("app_id", None),
                "password": kwargs.get("password", None),
                "tenant": kwargs.get("tenant", None),
            }

            # access Key Vault with Service Principal credentials, if defined
            if self._service_principal["app_id"] is not None:
                self._logger.info(
                    "access Key Vault '%s' with Service Principal", self._vault_name
                )
                self._logger.debug(
                    "Service Principal credentials: '%s'", self._service_principal
                )

                self._vault_creds = ServicePrincipalCredentials(
                    client_id=self._service_principal["app_id"],
                    secret=self._service_principal["password"],
                    tenant=self._service_principal["tenant"],
                    resource=self.__AZURE_RESOURCE_KEYVAULT,
                )

            # otherwise, access Key Vault with Managed Identity
            else:
                self._logger.info(
                    "access Key Vault '%s' with Managed Identity", self._vault_name
                )

                self._vault_creds = MSIAuthentication(
                    resource=self.__AZURE_RESOURCE_KEYVAULT
                )

            self._vault_uri = "https://{}.vault.azure.net/".format(self._vault_name)

            self._vault_client = KeyVaultClient(self._vault_creds)

            self._logger.debug(
                "Created instance from %s(%s)",
                self.__class__.__name__,
                ", ".join(
                    "{}='{}'".format(key, value) for key, value in locals().items()
                ),  # noqa
            )

    def get_secret(self, secret_name=None, secret_version=""):  # noqa
        """Get `secret_name` of specific `secret_version` from  Key Vault.

        Parameters
        ----------
        secret_name : :obj:`str`
            Name of secret to retrieve
            (default :obj:`None`)

        secret_version : :obj:`str`, optional
            Version of secret to retrieve, if empty means latest version
            (default '')

        Returns
        -------
        :obj:`SecretBundle`
            Object containing secret value with meta-data from Key Vault,
            or `None` if :obj:`KeyVaultErrorException` raised

        """
        if secret_name is None:
            self._logger.exception(
                "Exception: must provide 'secret_name' as a keyword argument"
            )
            raise ValueError("must provide 'secret_name' as a keyword argument")

        self._logger.info(
            "requesting secret '%s' of version '%s' from Key Vault URI '%s'",
            secret_name,
            secret_version,
            self._vault_uri,
        )

        secret = None

        try:
            secret = self._vault_client.get_secret(
                self._vault_uri, secret_name, secret_version
            )
        except KeyVaultErrorException:
            self._logger.exception("Exception: getting secret")
        else:
            self._logger.debug("received secret '%s'", secret)

        return secret

    def set_secret(
        self, secret_name=None, secret_value=None, content_type="application/json"
    ):
        """Set `secret_name` to specific `secret_value` in the  Key Vault.

        Parameters
        ----------
        secret_name : :obj:`str`
            Name of secret to be updated
            (default :obj:`None`)

        secret_value : :obj:`str`
            Value to be stored in ``secret_name``
            (default :obj:`None`)

        content_type : :obj:`str`, optional
            Content type of the value to be stored
            (default ``application/json``)

        Returns
        -------
        :obj:`SecretBundle`
            Object containing latest secret value with meta-data from Key Vault,
            or `None` if :obj:`KeyVaultErrorException` raised

        """
        if secret_name is None:
            self._logger.exception(
                "Exception: must provide 'secret_name' as a keyword argument"
            )
            raise ValueError("must provide 'secret_name' as a keyword argument")

        if secret_value is None:
            self._logger.exception(
                "Exception: must provide 'secret_value' as a keyword argument"
            )
            raise ValueError("must provide 'secret_value' as a keyword argument")

        self._logger.info(
            "updating secret '%s' with value of content type '%s' \
            at Key Vault URI '%s'",
            secret_name,
            content_type,
            self._vault_uri,
        )

        secret = None

        try:
            secret = self._vault_client.set_secret(
                self._vault_uri, secret_name, secret_value, content_type=content_type
            )
        except KeyVaultErrorException:
            self._logger.exception("Exception: updating secret")
        else:
            self._logger.debug("updated secret '%s'", secret)

        return secret
