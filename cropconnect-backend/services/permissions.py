# Role-Based Access Control (RBAC) and tenant authorization service.
# Implements can(user, action, resource) as required by Layer 4 of SaaS Playbook.
from typing import Any, Mapping

# Available roles in CropConnect
ROLE_OWNER = "Owner"
ROLE_ADMIN = "Admin"
ROLE_MEMBER = "Member"
ROLE_VIEWER = "Viewer"

ROLES = {ROLE_OWNER, ROLE_ADMIN, ROLE_MEMBER, ROLE_VIEWER}

# Permission matrix: Role -> set of allowed actions
ROLE_PERMISSIONS: dict[str, set[str]] = {
    ROLE_OWNER: {
        # Tenant management
        "org:delete",
        "org:transfer_ownership",
        "org:update_billing",
        "org:manage_members",
        "org:invite_member",
        "org:remove_member",
        # Devices & pumps
        "device:create",
        "device:read",
        "device:update",
        "device:delete",
        "pump:control",
        "pump:update_schedule",
        # Agronomy & advisory
        "crop:plan",
        "crop:scan",
        "ai:query",
        # Telemetry & read
        "telemetry:read",
        "market:read",
        "weather:read",
        # Data export & privacy
        "data:export",
        "data:delete",
    },
    ROLE_ADMIN: {
        "org:invite_member",
        "org:manage_members",
        "device:create",
        "device:read",
        "device:update",
        "pump:control",
        "pump:update_schedule",
        "crop:plan",
        "crop:scan",
        "ai:query",
        "telemetry:read",
        "market:read",
        "weather:read",
        "data:export",
    },
    ROLE_MEMBER: {
        "device:read",
        "pump:control",
        "crop:plan",
        "crop:scan",
        "ai:query",
        "telemetry:read",
        "market:read",
        "weather:read",
    },
    ROLE_VIEWER: {
        "device:read",
        "telemetry:read",
        "market:read",
        "weather:read",
    },
}


def get_user_role(user: Mapping[str, Any] | tuple[int, str] | None) -> str:
    """Extract role from user dict or default to Owner for single-tenant users."""
    if not user:
        return ROLE_VIEWER
    if isinstance(user, (list, tuple)):
        # (user_id, email)
        return ROLE_OWNER
    return str(user.get("role") or ROLE_OWNER)


def get_user_org_id(user: Mapping[str, Any] | tuple[int, str] | None) -> str | int | None:
    """Extract organization_id / tenant_id from user context."""
    if not user:
        return None
    if isinstance(user, (list, tuple)):
        # Single-tenant user ID is their primary org scope
        return str(user[0])
    return user.get("organization_id") or user.get("org_id") or user.get("id")


def can(
    user: Mapping[str, Any] | tuple[int, str] | None,
    action: str,
    resource: Mapping[str, Any] | None = None,
) -> bool:
    """
    Central authorization function.
    Checks:
    1. Does the user's role have permission for 'action'?
    2. If a tenant resource is provided, does resource organization_id match user org?
    """
    if not user:
        return False

    role = get_user_role(user)
    allowed_actions = ROLE_PERMISSIONS.get(role, set())
    if action not in allowed_actions:
        return False

    # Check multi-tenant resource scoping if resource is supplied
    if resource is not None:
        user_org = get_user_org_id(user)
        resource_org = (
            resource.get("organization_id")
            or resource.get("org_id")
            or resource.get("user_id")
            or resource.get("owner_id")
        )

        # If resource is scoped to an org/user, enforce strict match
        if resource_org is not None and user_org is not None:
            if str(resource_org) != str(user_org):
                return False

    return True
