# Smart Queue & Crowd Management System
## Technical Product Requirements Document (PRD)

**Status:** Baseline specification for implementation  
**Primary source:** Project Overview + reviewed build-order decisions  
**Target:** Semester project with production-minded architecture, implemented by a two-person core development team in ~3 weeks

---

## 1. Product Goal

Build a credible Smart Queue & Crowd Management System for hospitals, clinics, and OPD departments.

The system shall:

- digitize patient registration and queue/token flow
- let patients join a department queue through a public QR entry point
- provide patients with a private status page
- let authenticated hospital staff manage queues
- display currently served tokens on a public screen
- estimate occupancy in configured waiting-area zones using ESP32 sensor nodes
- provide basic operational analytics
- maintain auditability, privacy, and clear separation between operational queue logic and clinical decision-making

The system is **not** a diagnosis system, treatment system, automated medical-triage system, or complete HMIS replacement.

---

## 2. System Principles

1. **Backend owns business rules.**
2. **Frontend never generates authoritative tokens.**
3. **Queue state transitions are enforced by the backend state machine.**
4. **A public QR code is not treated as a secret or authentication credential.**
5. **Patient identity, visit, queue token, and public display number are separate concepts.**
6. **Staff operations require authentication and authorization.**
7. **ESP32 devices require device authentication before sending events.**
8. **Public displays expose queue information only, never private patient information.**
9. **Waiting time and occupancy are estimates.**
10. **The implementation should be simple enough to finish and explain, but structured so important security and deployment decisions are not hand-waved.**

---

## 3. User Types

### Patient
Can:
- open the public registration flow
- provide required registration information
- verify identity/phone when configured
- receive an active visit/token
- view private queue status
- receive optional queue notifications

### Staff
Can:
- sign in
- register/assist patients
- view department queues
- call, hold, recall, skip, complete, and transfer tokens
- assign/change operational priority where authorized
- view occupancy and operational information

### Supervisor/Admin
Can additionally:
- manage departments, rooms, zones, and devices
- manage staff accounts/roles
- correct occupancy with a required reason
- review audit events
- configure queue/priority/notification policies
- generate department/location QR codes

### Doctor/Clinical User
Architecture supports a separate clinical/doctor role later, but the first UI does not require doctors to operate the queue dashboard. Clinical priority decisions remain outside automated medical triage.

---

## 4. Core Patient Flow

```text
Patient arrives
    ↓
Scans physical/public QR
    ↓
Registration location + department resolved
    ↓
Anti-abuse checks
    ↓
Patient identity / phone verification according to configured policy
    ↓
Create or identify patient
    ↓
Create visit
    ↓
Check active duplicate visit rule
    ↓
Generate department-specific token
    ↓
Return private patient status URL
    ↓
Patient waits away from physical line
    ↓
Staff calls token
    ↓
Patient sees status / public display / optional notification
    ↓
Patient reaches assigned room
    ↓
Staff completes consultation
    ↓
Visit/token becomes terminal
```

---

## 5. QR Registration Design

### Public QR principle

The printed QR code is intentionally public. A copied QR is not considered a security breach by itself.

The QR identifies a valid **registration location / department context**.

Example concept:

```text
https://queue.example/register/<opaque-location-id>
```

The QR must not contain:
- patient IDs
- staff credentials
- API keys
- device secrets
- private status tokens

### Department-specific QR

Use department/location-specific QR codes as the default.

Examples:
- General Medicine registration QR
- Dental registration QR
- Eye registration QR

The registration page may still allow a department change only if policy permits it.

### QR generation

Admin functionality should generate a QR for an enabled registration location and allow it to be printed/downloaded.

---

## 6. Patient Identity Model

Do not use the visible queue token as patient identity.

Use separate identifiers:

```text
Patient
  patient_id = internal random identifier

Visit
  visit_id = internal random identifier

Queue Token
  token_id = internal random identifier
  display_token = G125
  status_access_id = private random identifier
```

The public token `G125` is not a credential.

### Persistent patient account

The architecture uses a persistent patient identity with separate visits.

Example:

```text
Patient P123
  ├── Visit V001 → General Medicine → COMPLETED
  ├── Visit V002 → Dental → COMPLETED
  └── Visit V003 → General Medicine → ACTIVE
```

This allows the same patient to return later without creating a new identity.

---

## 7. Patient Verification

### Verification policy

Verification is configurable.

Recommended deployment policy:
- **OTP verification enabled** for public production-like deployment.
- A provider-independent verification service interface is used so the application is not locked to one SMS vendor.
- OTP may be disabled only in controlled development/testing environments.

Never hard-code a universal OTP in deployed code.

### Why

A public QR can be copied. QR possession therefore cannot establish patient authenticity.

The practical security chain is:

```text
Public QR
→ anti-abuse controls
→ identity/phone verification
→ duplicate active-visit prevention
→ authenticated/private status access
```

Phone OTP proves control of the phone number. It does not by itself prove the person's medical identity. If a real hospital later supplies an authoritative patient identifier, an integration can add that verification layer.

---

## 8. Registration Abuse Protection

The system shall use layered protection rather than relying on one mechanism.

Minimum design:
- server-side input validation
- rate limiting
- registration attempt throttling
- OTP-request throttling when OTP is enabled
- duplicate active-visit prevention
- anti-automation challenge on public registration when deployed
- audit/monitoring of suspicious registration behavior

The exact thresholds are configuration values, not hard-coded business rules.

Example categories:
- requests per IP/time window
- registration attempts per phone/time window
- OTP requests per phone/time window
- abnormal repeated attempts from a source

An administrator may temporarily block abusive sources if needed.

---

## 9. Required Patient Data

Baseline registration fields:

- Full name
- Date of birth or age, according to final UI policy
- Mobile number
- Department
- Patient type (new/follow-up)

Avoid collecting unrelated personal or medical data.

If an actual hospital later requires additional fields, they must be explicitly justified and added to the data model/documentation.

---

## 10. Duplicate Active Visit Rule

A patient may have multiple historical visits.

The duplicate check applies only to active visits.

Recommended rule:

```text
Same patient
+
same department/service
+
active visit
=
do not create another active token
```

Active visit states:
- WAITING
- SERVING
- HOLD

Terminal states:
- COMPLETED
- SKIPPED

Behavior:
- If the patient already has an active visit for that department, return the existing active status instead of issuing another token.
- A completed/skipped historical visit does not permanently block future registration.
- Different departments may have concurrent visits if hospital policy permits.

This rule must be enforced server-side.

---

## 11. Queue and Token Model

Department-specific display tokens are generated by the backend.

Examples:

```text
General Medicine: G101, G102, G103...
Dental: D201, D202, D203...
Eye: E101, E102, E103...
```

The exact numbering prefix/sequence is configuration.

Token generation must be transaction-safe so two near-simultaneous registrations cannot receive the same authoritative token.

---

## 12. Queue States

Persistent token states:

```text
WAITING
SERVING
HOLD
SKIPPED
COMPLETED
```

Actions:

```text
CALL NEXT
HOLD
RECALL
SKIP
COMPLETE
TRANSFER
```

`RECALL` is an action, not a persistent state.

---

## 13. Missed Patient Policy

Recommended operational behavior:

```text
WAITING
   ↓
SERVING
   ↓
No response
   ↓
RECALL
   ↓
Still absent
   ↓
HOLD
   ↓
Queue continues
   ↓
Patient may be recalled later
```

Do not automatically erase the visit or silently issue a new token.

The exact waiting/recall timing is configurable.

---

## 14. Priority / Emergency

The software records and applies operational priority assigned by authorized personnel.

Categories:

```text
NORMAL
PRIORITY
EMERGENCY
```

Patient self-declaration may be recorded as a request/flag, but cannot automatically promote the patient into an emergency queue.

Authorized clinical/operational staff determine the actual priority.

The system must not:
- diagnose
- determine medical severity
- decide medical urgency
- automatically triage patients

### Priority policy

Make the ordering policy configurable.

Initial recommended policy:

```text
EMERGENCY / authorized urgent handling
        ↓
PRIORITY
        ↓
NORMAL
```

A currently serving consultation is not automatically interrupted by software.

Emergency handling may instead be routed outside the normal queue flow according to hospital policy.

---

## 15. Transfer

Transfer is a supported staff action.

Recommended semantics:

```text
Old visit/token
   ↓
transfer record
   ↓
New department/service
   ↓
new department-specific token
```

Example:

```text
G125 → Dental → D218
```

Maintain a link between the original and new token/visit event so the audit trail remains understandable.

---

## 16. Patient Status

Every active visit/token receives a private, random status-access identifier.

Example:

```text
/status/<random-status-id>
```

Do not use the public token alone as the private status credential.

Patient status shows:
- patient's token
- current token being served
- patients ahead
- estimated waiting time
- department
- room
- status

The page may refresh by polling.

---

## 17. Notifications

Browser-based status is always available and is the primary mechanism.

Notification delivery is optional/configurable.

Architecture:

```text
Queue event
   ↓
NotificationService
   ├── SMS provider
   └── WhatsApp provider
```

The queue engine must not depend directly on a vendor.

The first implementation may use one provider or leave notification delivery disabled while the interface remains available.

Notifications are particularly useful for missed-turn/near-turn scenarios, but the hospital may choose whether to use them.

---

## 18. Staff Authentication and Roles

Staff dashboard requires authentication.

Initial roles:
- ADMIN
- STAFF

Architecture allows:
- RECEPTION
- QUEUE_OPERATOR
- SUPERVISOR
- DOCTOR

Passwords are never stored in plaintext.

Use:
- password hashing
- secure authenticated sessions
- server-side authorization checks
- rate limiting on login attempts

Role checks are enforced by the backend, not only by hiding frontend buttons.

---

## 19. Doctor/Queue Architecture

Use a department-first queue model with optional doctor assignment.

```text
Department
  ↓
Queue
  ↓
Room
  ↓
optional Doctor
```

This keeps the initial operational workflow simple while allowing later doctor-specific queues.

Doctors do not need to operate the main queue dashboard in the first UI.

---

## 20. Rooms

Rooms are configurable data, not frontend constants.

Example:

```text
General Medicine → Room 2
Dental → Room 4
Eye → Room 5
```

Admin/Supervisor can update room assignments.

---

## 21. Occupancy / Crowd Model

Represent a monitored area as a configurable `Zone`.

Example:

```text
Zone: Waiting Area A
Capacity: 30
Doorway: A
Device: ESP32-01
```

A device can later serve another zone without redesigning the database.

### Sensor direction

```text
A → B = ENTRY
B → A = EXIT
```

Use:
- debounce
- sequence timeout
- invalid-sequence rejection
- occupancy floor of zero
- event logging

Occupancy is an estimate for the configured zone, not a guaranteed perfect headcount.

---

## 22. ESP32 Security

Each device must have:
- device identifier
- secret/key or equivalent credential
- enabled/disabled status
- zone assignment

Device events are authenticated by the backend.

Do not expose a public unauthenticated endpoint such as:

```text
POST /occupancy/increment
```

The backend receives a sensor event and applies the occupancy change.

---

## 23. Occupancy Correction

ADMIN/SUPERVISOR may manually correct occupancy.

A correction requires:
- previous value
- corrected value
- reason
- actor
- timestamp

The correction becomes an audit event.

---

## 24. Public Display

Display is read-only.

Show:

```text
Department
NOW SERVING
Token
Room
NEXT
```

Never show:
- patient name
- phone
- age
- diagnosis
- other private information

Use a display-specific API response that exposes only display-safe fields.

---

## 25. Waiting-Time Estimation

Initial formula:

```text
Estimated wait
≈
patients ahead × recent average consultation time
```

Prefer recent department/doctor-specific consultation durations when enough historical data exists.

Always label the result as an estimate.

The backend computes the authoritative estimate.

---

## 26. Analytics

Required basic analytics:
- total patients
- completed patients
- average waiting time
- average consultation time
- peak occupancy
- peak time
- department-wise waiting
- longest queue

Charts are secondary to queue reliability.

---

## 27. Deployment Architecture

### Development

```text
Browser
  ↓
Local frontend
  ↓
FastAPI
  ↓
SQLite
```

### Hosted

```text
Patient mobile
Staff laptop
Public display
ESP32
      ↓
   HTTPS
      ↓
FastAPI
      ↓
PostgreSQL
```

Use a database abstraction/ORM so application logic remains portable.

Do not depend on a local SQLite file as the durable source of truth for a cloud deployment.

### Fallback

Maintain a local deployment procedure for demonstrations and network failure.

---

## 28. Offline / Failure Behavior

The main system is cloud-connected.

When the cloud/network is unavailable:
- show clear offline/degraded status
- preserve important local device events where practical
- retain a documented manual/local fallback procedure
- do not silently claim that the live queue is synchronized when it is not

A full distributed offline-first architecture is not part of the first implementation.

---

## 29. Audit Logging

Audit important operational and administrative events.

Examples:
- login/logout
- patient registration correction
- token generation
- call
- hold
- recall
- skip
- complete
- transfer
- priority change
- occupancy correction
- room change
- department configuration change
- device enable/disable

Each event should identify actor/device, timestamp, action, and relevant entity.

---

## 30. Data Retention

Retention is configurable.

Every patient/visit/queue/audit/occupancy record should carry timestamps so retention/anonymization can be introduced later.

The semester implementation may keep the policy simple but should not design away the possibility of retention management.

---

## 31. Security Boundaries

```text
Public patient API
    ├── registration
    └── private status access

Authenticated staff API
    ├── queue controls
    ├── configuration
    └── administrative actions

Authenticated device API
    └── sensor events
```

Never rely solely on frontend visibility for authorization.

---

## 32. Non-Goals

Not in scope for the core release:
- diagnosis
- automated medical triage
- treatment recommendations
- complete HMIS replacement
- guaranteed waiting times
- guaranteed perfect crowd counting
- enterprise-scale hospital integration
- complex distributed offline synchronization

---

## 33. Definition of Success

The system is successful when a realistic end-to-end flow works:

```text
Public QR
→ patient registration
→ verification/anti-abuse controls
→ patient/visit creation
→ unique token
→ private status URL
→ staff login
→ call next
→ public display update
→ patient status update
→ missed-turn handling
→ consultation complete
→ wait statistics
→ ESP32 entry/exit event
→ occupancy update
→ audit trail
```

Every core behavior must be explainable to the mentor from the code and data model.
