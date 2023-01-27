from datetime import timedelta
from typing import Optional

from momento_wire_types.controlclient_pb2 import (
    _CreateSigningKeyRequest,
    _ListSigningKeysRequest,
    _RevokeSigningKeyRequest,
)
from momento_wire_types.controlclient_pb2_grpc import ScsControlStub

from momento import logs
from momento.auth import CredentialProvider
from momento.errors import convert_error
from momento.internal._utilities import _validate_ttl
from momento_signed_urls.internal.aio._scs_grpc_manager import _SigningControlGrpcManager
from momento_signed_urls.responses import (
    CreateSigningKeyResponse,
    ListSigningKeysResponse,
    RevokeSigningKeyResponse,
)

_DEADLINE_SECONDS = 60.0  # 1 minute


class _ScsControlClient:
    """Momento Internal."""

    def __init__(self, credential_provider: CredentialProvider):
        endpoint: str = credential_provider.get_control_endpoint()
        self._logger = logs.logger
        self._logger.debug("Simple cache control client instantiated with endpoint: %s", endpoint)
        self._grpc_manager = _SigningControlGrpcManager(credential_provider)
        self._endpoint = endpoint

    @property
    def endpoint(self) -> str:
        return self._endpoint

    async def create_signing_key(self, ttl: timedelta, endpoint: str) -> CreateSigningKeyResponse:
        try:
            _validate_ttl(ttl)
            ttl_minutes = round(ttl.total_seconds() / 60)
            self._logger.info(f"Creating signing key with ttl (in minutes): {ttl_minutes}")
            create_signing_key_request = _CreateSigningKeyRequest()
            create_signing_key_request.ttl_minutes = ttl_minutes
            return CreateSigningKeyResponse.from_grpc_response(
                await self._build_stub().CreateSigningKey(create_signing_key_request, timeout=_DEADLINE_SECONDS),
                endpoint,
            )
        except Exception as e:
            self._logger.warning(f"Failed to create signing key with exception: {e}")
            raise convert_error(e)

    async def revoke_signing_key(self, key_id: str) -> RevokeSigningKeyResponse:
        try:
            self._logger.info(f"Revoking signing key with key_id {key_id}")
            request = _RevokeSigningKeyRequest()
            request.key_id = key_id
            await self._build_stub().RevokeSigningKey(request, timeout=_DEADLINE_SECONDS)
            return RevokeSigningKeyResponse()
        except Exception as e:
            self._logger.warning(f"Failed to revoke signing key with key_id {key_id} exception: {e}")
            raise convert_error(e)

    async def list_signing_keys(self, endpoint: str, next_token: Optional[str] = None) -> ListSigningKeysResponse:
        try:
            list_signing_keys_request = _ListSigningKeysRequest()
            list_signing_keys_request.next_token = next_token if next_token is not None else ""
            return ListSigningKeysResponse.from_grpc_response(
                await self._build_stub().ListSigningKeys(list_signing_keys_request, timeout=_DEADLINE_SECONDS),
                endpoint,
            )
        except Exception as e:
            raise convert_error(e)

    def _build_stub(self) -> ScsControlStub:
        return self._grpc_manager.async_stub()

    async def close(self) -> None:
        await self._grpc_manager.close()
