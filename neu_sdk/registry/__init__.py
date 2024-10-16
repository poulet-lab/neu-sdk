__all__ = ["consul"]

from neu_sdk.registry.consul import (
    get_service,
    register_service,
    deregister_service,
    ping_consul,
)
