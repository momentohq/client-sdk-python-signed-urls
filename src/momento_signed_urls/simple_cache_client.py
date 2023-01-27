from datetime import timedelta
from types import TracebackType
from typing import Optional, Type

from momento import logs
from momento.auth import CredentialProvider
from momento.config import Configuration

try:
    from momento.internal._utilities import _validate_request_timeout

    from momento_signed_urls.internal.synchronous._scs_control_client import (
        _ScsControlClient,
    )
except ImportError as e:
    if e.name == "cygrpc":
        import sys

        print(
            "There is an issue on M1 macs between GRPC native packaging and Python wheel tags. "
            "See https://github.com/grpc/grpc/issues/28387",
            file=sys.stderr,
        )
        print("-".join("" for _ in range(99)), file=sys.stderr)
        print("    TO WORK AROUND:", file=sys.stderr)
        print("    * Install Rosetta 2", file=sys.stderr)
        print(
            "    * Install Python from python.org (you might need to do this if you're using an arm-only build)",
            file=sys.stderr,
        )
        print("    * re-run with:", file=sys.stderr)
        print("arch -x86_64 {} {}".format(sys.executable, *sys.argv), file=sys.stderr)
        print("-".join("" for _ in range(99)), file=sys.stderr)
    raise e

from momento_signed_urls.responses import (
    CreateSigningKeyResponse,
    ListSigningKeysResponse,
    RevokeSigningKeyResponse,
)


class SimpleCacheClient:
    """Simple Cache Client"""

    def __init__(self, configuration: Configuration, credential_provider: CredentialProvider):
        """Creates an async SimpleCacheClient

        Args:
            configuration (Configuration): An object holding configuration settings for communication with the server.
            credential_provider (CredentialProvider): An object holding the auth token and endpoint information.
            default_ttl (timedelta): A default Time To Live timedelta for cache objects created by this client.
                It is possible to override this setting when calling the set method.
        Raises:
            IllegalArgumentException: If method arguments fail validations.
        """
        _validate_request_timeout(configuration.get_transport_strategy().get_grpc_configuration().get_deadline())
        self._logger = logs.logger
        self._next_client_index = 0
        self._control_client = _ScsControlClient(credential_provider)
        self._cache_endpoint = credential_provider.get_cache_endpoint()

    def __enter__(self) -> "SimpleCacheClient":
        return self

    def __exit__(
        self,
        exc_type: Optional[Type[BaseException]],
        exc_value: Optional[BaseException],
        traceback: Optional[TracebackType],
    ) -> None:
        self._control_client.close()

    def create_signing_key(self, ttl: timedelta) -> CreateSigningKeyResponse:
        """Creates a Momento signing key

        Args:
            ttl: The key's time-to-live represented as a timedelta

        Returns:
            CreateSigningKeyResponse

        Raises:
            SdkException: validation, server-side, or other runtime error
        """
        return self._control_client.create_signing_key(ttl, self._cache_endpoint)

    def revoke_signing_key(self, key_id: str) -> RevokeSigningKeyResponse:
        """Revokes a Momento signing key, all tokens signed by which will be invalid

        Args:
            key_id: The id of the Momento signing key to revoke

        Returns:
            RevokeSigningKeyResponse

        Raises:
            SdkException: validation, server-side, or other runtime error
        """
        return self._control_client.revoke_signing_key(key_id)

    def list_signing_keys(self, next_token: Optional[str] = None) -> ListSigningKeysResponse:
        """Lists all Momento signing keys for the provided auth token.

        Args:
            next_token: Token to continue paginating through the list. It's used to handle large paginated lists.

        Returns:
            ListSigningKeysResponse

        Raises:
            SdkException: validation, server-side, or other runtime error
        """
        return self._control_client.list_signing_keys(self._cache_endpoint, next_token)
