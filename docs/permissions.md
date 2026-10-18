# CropConnect: Permissions & Authorization Model (Layer 4)

## 1. Role Definitions
CropConnect implements a strict Role-Based Access Control (RBAC) model across four standardized tenant roles:
1. **Owner**: The primary account holder and billing authority. Has unconditional authority within the tenant organization, including member management, data deletion, and billing.
2. **Admin**: Farm operations manager. Manages physical devices, configures irrigation thresholds, toggles manual pump overrides, invites workers, and generates agronomic reports.
3. **Member**: Farm operator/technician. Can view live telemetry, trigger crop scans, interact with the AI agronomy advisor, and operate assigned pump relays.
4. **Viewer**: Read-only auditor or external agronomist. Allowed to inspect historical sensor trends and weather forecasts without actuation permissions.

---

## 2. Permissions Matrix (`role × action`)

| Action / Capability | Owner | Admin | Member | Viewer |
|---|:---:|:---:|:---:|:---:|
| **Tenant & Team Management** | | | | |
| `org:delete` (Delete account/farm) | ✅ | ❌ | ❌ | ❌ |
| `org:transfer_ownership` | ✅ | ❌ | ❌ | ❌ |
| `org:update_billing` | ✅ | ❌ | ❌ | ❌ |
| `org:manage_members` (Change roles) | ✅ | ✅ | ❌ | ❌ |
| `org:invite_member` | ✅ | ✅ | ❌ | ❌ |
| `org:remove_member` | ✅ | ✅ | ❌ | ❌ |
| **Devices & Hardware** | | | | |
| `device:create` (Pair new ESP32) | ✅ | ✅ | ❌ | ❌ |
| `device:update` (Rename/recalibrate) | ✅ | ✅ | ❌ | ❌ |
| `device:delete` (De-register hardware) | ✅ | ❌ | ❌ | ❌ |
| `device:read` (View device status) | ✅ | ✅ | ✅ | ✅ |
| **Pump Actuation & Scheduling** | | | | |
| `pump:control` (Manual on/off toggle) | ✅ | ✅ | ✅ | ❌ |
| `pump:update_schedule` (Set thresholds)| ✅ | ✅ | ❌ | ❌ |
| **Agronomy & Intelligence** | | | | |
| `crop:plan` (Create/edit crop plan) | ✅ | ✅ | ✅ | ❌ |
| `crop:scan` (Upload leaf for disease) | ✅ | ✅ | ✅ | ❌ |
| `ai:query` (Ask Gemini advisor) | ✅ | ✅ | ✅ | ❌ |
| **Telemetry & Market Insights** | | | | |
| `telemetry:read` (View moisture graphs)| ✅ | ✅ | ✅ | ✅ |
| `market:read` (View live mandi prices) | ✅ | ✅ | ✅ | ✅ |
| `weather:read` (View 7-day forecast) | ✅ | ✅ | ✅ | ✅ |
| **Data Protection & Privacy** | | | | |
| `data:export` (Download JSON archive) | ✅ | ✅ | ❌ | ❌ |
| `data:delete` (Right to be forgotten) | ✅ | ❌ | ❌ | ❌ |

---

## 3. Central Permission Function: `can(user, action, resource)`

Authorization in CropConnect is centralized in `cropconnect-backend/services/permissions.py`:

```python
from services.permissions import can

# Example endpoint usage:
@router.post("/api/pumps/{pump_id}/toggle")
def toggle_pump(pump_id: int, current_user = Depends(get_current_user)):
    pump = get_pump_by_id(pump_id)
    if not pump:
        raise HTTPException(status_code=404, detail="Pump not found")
        
    # Enforce action permission and tenant boundary
    if not can(current_user, "pump:control", resource=pump):
        raise HTTPException(status_code=403, detail="Permission denied")
        
    # Execute pump toggle
    ...
```

### Core Enforcement Rules:
1. **Server is the Ultimate Source of Truth**: The React UI hides buttons that a user cannot click, but the FastAPI backend enforces `can()` on every state-changing request.
2. **Tenant Scoping**: If a user attempts to access an `id` belonging to Org B, the server responds with `404 Not Found` (never `403 Forbidden`) so attackers cannot enumerate existing tenant IDs.
3. **No Hard-Coded Ad-Hoc Role Checks**: All authorization logic flows through `can(user, action, resource)` to ensure auditability and consistent policies.
