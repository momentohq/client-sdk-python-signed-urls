import pkg_resources
from momento.internal.synchronous._scs_control_client import _ControlGrpcManager


class _SigningControlGrpcManager(_ControlGrpcManager):
    """Momento Internal."""

    version = pkg_resources.get_distribution("momento_signed_urls").version
