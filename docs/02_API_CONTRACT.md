# Smart Queue & Crowd Management System
## API Contract

**Rule:** This file is the single source of truth for endpoint naming, request/response shapes, and status names. Frontend and backend must not invent conflicting contracts.

---

## 1. API Conventions

Base path:

```text
/api
```

JSON is used for request/response bodies.

All timestamps should use ISO 8601 in UTC internally.

Public/private IDs should be opaque and non-sequential where exposed externally.

Backend owns validation and business rules.

---

## 2. Authentication Domains

### Public patient endpoints
Used by registration/status flows.

### Staff endpoints
Require authenticated staff session and role authorization.

### Device endpoints
Require device authentication.

---

## 3. Health

### GET `/api/health`

Response:

```json
{
  "status": "ok"
}
```

---

## 4. Registration Locations / Departments

### GET `/api/departments`

Response:

```json
{
  "departments": [
    {
      "id": "dep_...",
      "name": "General Medicine",
      "code": "G",
      "room": "2",
      "active": true
    }
  ]
}
```

The public registration page consumes this only when department selection is needed.

---

## 5. Patient Verification

### POST `/api/patient/verification/start`

Request:

```json
{
  "mobile": "9999999999",
  "method": "OTP"
}
```

Response:

```json
{
  "challenge_id": "challenge_...",
  "expires_at": "..."
}
```

### POST `/api/patient/verification/confirm`

Request:

```json
{
  "challenge_id": "challenge_...",
  "code": "..."
}
```

Response:

```json
{
  "verified": true,
  "verification_token": "opaque-short-lived-token"
}
```

OTP provider details remain behind a provider-neutral service interface.

---

## 5. Patient Registration

### POST `/api/register`

Request:

```json
{
  "registration_location_id": "loc_opaque_id",
  "name": "Test Patient",
  "date_of_birth": "2000-01-01",
  "mobile": "9999999999",
  "department_id": "dep_...",
  "patient_type": "NEW",
  "verification_token": "opaque-short-lived-token",
  "anti_bot_token": "..."
}
```

Notes:
- `date_of_birth` may be replaced by the final agreed age/DOB policy.
- `patient_type` is `NEW` or `FOLLOW_UP`.
- verification is configurable by environment/policy.
- the anti-bot token is validated server-side when enabled.

Successful response:

```json
{
  "visit_id": "visit_...",
  "token_id": "token_...",
  "display_token": "G125",
  "department": "General Medicine",
  "room": "2",
  "status": "WAITING",
  "status_url": "/status/opaque-random-id"
}
```

Duplicate active visit response should not create another token.

Example:

```json
{
  "error": "ACTIVE_VISIT_EXISTS",
  "visit_id": "visit_...",
  "display_token": "G125",
  "status": "WAITING",
  "status_url": "/status/opaque-random-id"
}
```

---

## 6. Patient Status

### GET `/api/status/{status_access_id}`

The exposed `status_access_id` is an opaque random identifier. Do not use a visible queue number or sequential database ID as the private status credential.

Response:

```json
{
  "display_token": "G125",
  "current_token": "G118",
  "patients_ahead": 6,
  "estimated_wait_minutes": 30,
  "department": "General Medicine",
  "room": "2",
  "status": "WAITING"
}
```

Possible status values:

```text
WAITING
SERVING
HOLD
SKIPPED
COMPLETED
```

A status request is authorized through the private status-access mechanism. The browser-facing status page uses the private random status identifier, not the public display token.

---

## 7. Staff Authentication

### POST `/api/auth/login`

Request:

```json
{
  "username": "staff01",
  "password": "..."
}
```

Response:

```json
{
  "staff": {
    "id": "staff_...",
    "display_name": "Staff User",
    "role": "STAFF"
  }
}
```

Authentication state is maintained using a secure authenticated session.

### POST `/api/auth/logout`

Invalidates the session.

### GET `/api/auth/me`

Returns current authenticated staff identity/role.

---

## 8. Staff Dashboard

### GET `/api/staff/queues`

Response should contain only staff-authorized data:

```json
{
  "departments": [
    {
      "department_id": "dep_...",
      "name": "General Medicine",
      "waiting_count": 18,
      "current_token": "G118",
      "room": "2"
    }
  ]
}
```

---

## 9. Queue Actions

### POST `/api/staff/queue/{department_id}/next`

Calls the next eligible token.

Response:

```json
{
  "token_id": "token_...",
  "display_token": "G118",
  "status": "SERVING",
  "room": "2"
}
```

### POST `/api/staff/token/{token_id}/hold`

### POST `/api/staff/token/{token_id}/recall`

### POST `/api/staff/token/{token_id}/skip`

### POST `/api/staff/token/{token_id}/complete`

All return the updated token summary.

Example:

```json
{
  "token_id": "token_...",
  "display_token": "G118",
  "status": "COMPLETED"
}
```

### POST `/api/staff/token/{token_id}/transfer`

Request:

```json
{
  "target_department_id": "dep_..."
}
```

Response:

```json
{
  "source_token": "G125",
  "target_token": "D218",
  "target_department": "Dental",
  "status": "WAITING"
}
```

---

## 10. Priority

### POST `/api/staff/token/{token_id}/priority`

Request:

```json
{
  "priority": "PRIORITY"
}
```

Possible values:

```text
NORMAL
PRIORITY
EMERGENCY
```

Only authorized roles may perform this action.

The backend never performs medical triage.

---

## 11. Public Display

### GET `/api/display/{department_id}`

Display-safe response:

```json
{
  "department": "General Medicine",
  "current_token": "G118",
  "next_token": "G119",
  "room": "2"
}
```

No private patient information.

---

## 12. Occupancy

### POST `/api/devices/{device_id}/events`

Authenticated device request:

```json
{
  "event_type": "ENTRY",
  "event_id": "opaque-event-id",
  "occurred_at": "2026-09-08T10:10:20Z"
}
```

Possible event types:

```text
ENTRY
EXIT
```

Backend validates:
- device identity
- device enabled status
- event format
- duplicate event ID
- timestamp sanity

### GET `/api/zones/{zone_id}/occupancy`

Response:

```json
{
  "zone_id": "zone_...",
  "current_count": 24,
  "capacity": 30,
  "level": "HIGH",
  "estimated": true,
  "updated_at": "2026-09-08T10:10:20Z"
}
```

### POST `/api/staff/zones/{zone_id}/occupancy-correction`

Request:

```json
{
  "corrected_count": 19,
  "reason": "Sensor false count"
}
```

Requires authorized role.

---

## 13. Analytics

### GET `/api/staff/analytics`

Response concept:

```json
{
  "total_patients": 120,
  "completed_patients": 104,
  "average_wait_minutes": 22.4,
  "average_consultation_minutes": 5.8,
  "peak_occupancy": 29,
  "peak_time": "11:40",
  "longest_queue": {
    "department": "General Medicine",
    "waiting": 18
  }
}
```

---

## 14. QR Administration

### POST `/api/admin/registration-locations`

Creates/configures a registration location.

### GET `/api/admin/registration-locations`

Lists locations.

### GET `/api/admin/registration-locations/{id}/qr`

Returns QR image or QR payload for printing.

---

## 15. Error Format

Use a consistent error shape:

```json
{
  "error": "ACTIVE_VISIT_EXISTS",
  "message": "Patient already has an active visit for this department."
}
```

Common errors:

```text
VALIDATION_ERROR
UNAUTHORIZED
FORBIDDEN
NOT_FOUND
ACTIVE_VISIT_EXISTS
INVALID_STATE_TRANSITION
QUEUE_EMPTY
RATE_LIMITED
OTP_REQUIRED
OTP_INVALID
ANTI_BOT_FAILED
DEVICE_UNAUTHORIZED
DUPLICATE_EVENT
```

---

## 16. API Contract Rules

1. Endpoint names must not be changed casually.
2. Field names must not be silently renamed.
3. Frontend must use the exact response shape.
4. Backend tests must cover validation and authorization.
5. Public display gets a restricted response shape.
6. Device APIs are authenticated separately from staff APIs.
7. Breaking changes require updating this document and dependent frontend code before implementation continues.
