"""Security primitives for KrishiMitra-AI."""

from __future__ import annotations

from krishimitra_security.api_keys import (
    ApiKey,
    ApiKeyManager,
    GeneratedApiKey,
)
from krishimitra_security.authentication import (
    AuthenticatedPrincipal,
    AuthenticationError,
    AuthenticationMethod,
    AuthenticationResult,
    AuthenticationService,
)
from krishimitra_security.authorization import (
    AuthorizationContext,
    AuthorizationDecision,
    AuthorizationError,
    AuthorizationResult,
    AuthorizationService,
)
from krishimitra_security.permissions import (
    Permission,
    is_valid_permission,
    permission_value,
)
from krishimitra_security.rate_limit import (
    RateLimitDecision,
    TokenBucketRateLimiter,
)
from krishimitra_security.roles import (
    ROLE_PERMISSIONS,
    Role,
    has_permission,
    permissions_for_role,
    roles_for_permission,
)
from krishimitra_security.secrets import (
    SecretManager,
    SecretMetadata,
)

__all__ = [
    "ApiKey",
    "ApiKeyManager",
    "AuthenticatedPrincipal",
    "AuthenticationError",
    "AuthenticationMethod",
    "AuthenticationResult",
    "AuthenticationService",
    "AuthorizationContext",
    "AuthorizationDecision",
    "AuthorizationError",
    "AuthorizationResult",
    "AuthorizationService",
    "GeneratedApiKey",
    "Permission",
    "ROLE_PERMISSIONS",
    "RateLimitDecision",
    "Role",
    "SecretManager",
    "SecretMetadata",
    "TokenBucketRateLimiter",
    "has_permission",
    "is_valid_permission",
    "permission_value",
    "permissions_for_role",
    "roles_for_permission",
]