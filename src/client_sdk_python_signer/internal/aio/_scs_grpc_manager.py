import pkg_resources

from momento.internal.aio._scs_control_client import _ControlGrpcManager


class _SigningControlGrpcManager(_ControlGrpcManager):
    """Momento Internal."""

    version = pkg_resources.get_distribution("client_sdk_python_signer").version
