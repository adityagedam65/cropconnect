import unittest
from services.permissions import can, ROLE_OWNER, ROLE_ADMIN, ROLE_MEMBER, ROLE_VIEWER


class TestPermissions(unittest.TestCase):
    def test_owner_permissions(self):
        owner = {"id": 1, "role": ROLE_OWNER, "organization_id": 100}
        self.assertTrue(can(owner, "org:delete"))
        self.assertTrue(can(owner, "pump:control"))
        self.assertTrue(can(owner, "data:export"))
        self.assertTrue(can(owner, "telemetry:read"))

    def test_admin_permissions(self):
        admin = {"id": 2, "role": ROLE_ADMIN, "organization_id": 100}
        self.assertFalse(can(admin, "org:delete"))
        self.assertTrue(can(admin, "pump:control"))
        self.assertTrue(can(admin, "crop:plan"))
        self.assertTrue(can(admin, "telemetry:read"))

    def test_viewer_permissions(self):
        viewer = {"id": 3, "role": ROLE_VIEWER, "organization_id": 100}
        self.assertFalse(can(viewer, "org:delete"))
        self.assertFalse(can(viewer, "pump:control"))
        self.assertFalse(can(viewer, "crop:plan"))
        self.assertTrue(can(viewer, "telemetry:read"))
        self.assertTrue(can(viewer, "market:read"))

    def test_tenant_resource_isolation(self):
        user_org_a = {"id": 1, "role": ROLE_OWNER, "organization_id": 101}
        resource_org_a = {"id": 10, "organization_id": 101, "name": "Pump Zone 1"}
        resource_org_b = {"id": 20, "organization_id": 202, "name": "Pump Zone 2"}

        # Can access own org resource
        self.assertTrue(can(user_org_a, "pump:control", resource=resource_org_a))
        # Blocked from accessing other org resource (cross-tenant access)
        self.assertFalse(can(user_org_a, "pump:control", resource=resource_org_b))


if __name__ == "__main__":
    unittest.main()
