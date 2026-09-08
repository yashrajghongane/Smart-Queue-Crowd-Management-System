# Smart Queue & Crowd Management System
## Database Schema

**Primary rule:** Patient identity, visit, queue token, device, zone, and audit data are separate entities.

The implementation should use an ORM/database abstraction so the application can use SQLite locally and PostgreSQL when hosted.

---

## 1. Entity Overview

```text
Staff
  │
  ├── AuditLog
  │
Department ── Room
  │
  ├── RegistrationLocation
  │
  └── Queue/Visits/Tokens

Patient
  │
  └── Visit
        │
        └── Token
              │
              └── Queue Events / Timing

Zone
  │
  └── Device
        │
        └── Occupancy Events
```

---

## 2. `departments`

Fields:

```text
id                 opaque primary key
name               display name
code               token prefix
active             boolean
created_at
updated_at
```

Examples:

```text
General Medicine / G
Dental / D
Eye / E
```

---

## 3. `rooms`

Fields:

```text
id
name_or_number
department_id
active
created_at
updated_at
```

A department may have one or more configured rooms.

---

## 4. `registration_locations`

Represents a physical/public QR entry point.

Fields:

```text
id                      opaque identifier
department_id           default department
name
qr_public_id             opaque non-secret identifier
active
created_at
updated_at
```

The QR should reference this location context rather than containing credentials.

---

## 5. `patients`

Fields:

```text
id                     opaque internal identifier
full_name
date_of_birth          nullable only if policy permits
mobile
patient_type_default   optional
verification_status
created_at
updated_at
```

The mobile number may need normalization before duplicate/lookup operations.

Do not use the visible token number as the patient identifier.

---

## 6. `patient_verifications`

Purpose:
- OTP/challenge bookkeeping
- provider-agnostic design

Fields:

```text
id
patient_id             nullable before patient creation
mobile
method                 OTP / other future method
challenge_reference
status
attempt_count
expires_at
verified_at
created_at
```

Never store a plaintext OTP when a secure one-way verification design can be used.

---

## 7. `visits`

A visit represents a patient's department/service interaction.

Fields:

```text
id
patient_id
department_id
status
started_at
ended_at
created_at
updated_at
```

Visit status can be derived from token state for the first release, or stored explicitly if required.

---

## 8. `tokens`

Authoritative queue object.

Fields:

```text
id
visit_id
department_id
display_token
status
priority
room_id
status_access_id
called_at
completed_at
created_at
updated_at
```

States:

```text
WAITING
SERVING
HOLD
SKIPPED
COMPLETED
```

Priority:

```text
NORMAL
PRIORITY
EMERGENCY
```

`status_access_id` must be random/unpredictable.

`display_token` is public queue information and is not a credential.

---

## 9. Queue/Token Configuration

Recommended configuration entity/fields should cover:

```text
sequence_scope       operating_day
sequence_start       101
prefix               G / D / E
priority_policy      configured
missed_timeout       configured
operating_timezone   configured
```

The final token policy is one sequence per department per operating day unless configuration explicitly selects another scope.

---

## 9. Token uniqueness

The database must enforce uniqueness appropriate to the active queue.

At minimum:
- `display_token` unique within the appropriate department/token scope
- `status_access_id` globally unique
- token/event IDs unique where exposed/used for idempotency

The registration transaction must prevent duplicate token allocation.

---

## 10. `queue_events`

Every significant token state/action is logged.

Fields:

```text
id
token_id
visit_id
actor_type          STAFF / SYSTEM / PATIENT / DEVICE
actor_id            nullable depending on actor type
action
from_status
to_status
metadata_json
created_at
```

Example action names:

```text
REGISTERED
CALLED
HELD
RECALLED
SKIPPED
COMPLETED
TRANSFERRED
PRIORITY_CHANGED
```

---

## 11. `consultation_records`

For timing/analytics.

Fields:

```text
id
token_id
started_at
ended_at
duration_seconds
created_at
```

The first implementation may derive timing directly from token timestamps if the final implementation does not need a separate table, but the schema must preserve enough data to calculate actual consultation duration.

---

## 12. `staff`

Fields:

```text
id
username
password_hash
display_name
role
active
created_at
updated_at
last_login_at
```

Roles:

```text
ADMIN
STAFF
```

Architecture may add:

```text
RECEPTION
QUEUE_OPERATOR
SUPERVISOR
DOCTOR
```

later.

---

## 13. `staff_sessions`

Fields:

```text
id
staff_id
session_identifier_hash
created_at
expires_at
last_seen_at
revoked_at
```

Use secure server-side sessions.

Do not store raw long-lived session secrets unnecessarily.

---

## 14. `zones`

Represents monitored physical waiting areas.

Fields:

```text
id
name
capacity
department_id       nullable
active
created_at
updated_at
```

Example:

```text
Waiting Area A / 30
```

---

## 15. `devices`

Fields:

```text
id
device_identifier
device_secret_hash_or_equivalent
zone_id
active
last_seen_at
created_at
updated_at
```

A device is assigned to a zone/doorway.

Do not store a device secret in plaintext if the chosen authentication design supports secure secret handling.

---

## 16. `occupancy_events`

Fields:

```text
id
device_id
zone_id
event_id
event_type
occurred_at
received_at
created_at
```

Event types:

```text
ENTRY
EXIT
```

`event_id` should support idempotency so a retried ESP32 event does not increment occupancy twice.

---

## 17. `occupancy_state`

Fields:

```text
zone_id
current_count
capacity
updated_at
```

Business rule:

```text
current_count >= 0
```

An invalid EXIT when current count is already zero should not make occupancy negative.

---

## 18. `occupancy_corrections`

Fields:

```text
id
zone_id
old_count
new_count
reason
staff_id
created_at
```

Every manual correction is auditable.

---

## 19. `notification_deliveries`

Provider-neutral notification record.

Fields:

```text
id
patient_id
visit_id
channel            SMS / WHATSAPP
template
destination
status
provider_reference
sent_at
created_at
```

The application should not depend directly on one notification vendor.

---

## 20. `audit_logs`

Fields:

```text
id
actor_type
actor_id
action
entity_type
entity_id
before_json
after_json
metadata_json
created_at
```

Examples:

```text
STAFF_LOGIN
TOKEN_COMPLETE
TOKEN_TRANSFER
PRIORITY_CHANGE
ROOM_CHANGE
OCCUPANCY_CORRECTION
QR_LOCATION_CREATED
STAFF_ROLE_CHANGED
```

---

## 21. Suggested seed data

Initial departments:

```text
General Medicine / G / Room 2
Dental / D / Room 4
Eye / E / Room 5
```

These are demo configuration, not universal hospital defaults.

---

## 22. Data Relationships

```text
departments 1 ─── N rooms

departments 1 ─── N registration_locations

patients 1 ─── N visits

visits 1 ─── 1 active token at a time

departments 1 ─── N tokens

tokens 1 ─── N queue_events

tokens 1 ─── 0..1 consultation_records

zones 1 ─── N devices

devices 1 ─── N occupancy_events

zones 1 ─── 1 occupancy_state
```

---

## 23. Security Rules

- Internal IDs are opaque.
- Public/private status identifiers are random.
- Patient mobile numbers are not public.
- Public token numbers are not treated as authentication.
- Passwords use secure hashing.
- Device secrets are protected.
- Audit records are append-oriented.
- Input validation is server-side.
- Database constraints should enforce critical uniqueness/integrity.
