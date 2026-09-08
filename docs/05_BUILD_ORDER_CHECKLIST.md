# Smart Queue & Crowd Management System
## 3-Week Build Order Checklist

**Principle:** Follow dependency order, not person order. Frontend may work from mock JSON in parallel once the API contract is frozen.

---

# WEEK 1 — CORE SYSTEM

## Phase 0 — Specification Lock

### [ ] 1. Freeze source-of-truth documents
Confirm these files are committed:

```text
01_TECHNICAL_PRD.md
02_API_CONTRACT.md
03_DATABASE_SCHEMA.md
04_FRONTEND_BUILD_MAP.md
05_BUILD_ORDER_CHECKLIST.md
```

Do not start coding before endpoint/state/schema naming is frozen.

### [ ] 2. Create GitHub repository

```text
backend/
frontend/
firmware/esp32/
docs/
```

Add:
- `.gitignore`
- `README.md`

### [ ] 3. Write root `AGENTS.md`
### [ ] 3A. Write the security/deployment baseline
Commit `06_SECURITY_PRIVACY_NFR.md` and freeze:
- session approach
- CORS/CSRF policy
- HTTPS requirement
- rate limiting
- device authentication
- status identifier policy
- token numbering policy


Tell AI agents:
- read the PRD/API/schema
- preserve API names
- backend owns business logic
- never expose patient secrets
- never add unapproved architecture
- do not modify unrelated areas

---

# Phase 1 — Backend Skeleton

### [ ] 4. Create FastAPI project
- virtual environment
- FastAPI
- server startup
- `/api/health`

### [ ] 5. Configure database abstraction
Local:

```text
SQLite
```

Hosted:

```text
PostgreSQL
```

### [ ] 6. Add migration tooling and initial schema

Implement:
- migration tooling (e.g. Alembic)
- departments
- rooms
- registration_locations
- patients
- patient_verifications
- visits
- tokens
- queue_events
- staff
- staff_sessions
- zones
- devices
- occupancy_events
- occupancy_state
- audit_logs

Only add tables when required by the implementation.

### [ ] 7. Seed three departments

```text
General Medicine
Dental
Eye
```

Configure rooms.

---

# Parallel Frontend Track — Start immediately

### [ ] F1. Create frontend folder structure
Follow `04_FRONTEND_BUILD_MAP.md`.

### [ ] F2. Build registration page with mock data
Do not wait for backend.

### [ ] F3. Build token success state

### [ ] F4. Build patient status page with mock polling

The frontend uses exactly the JSON structures defined in `02_API_CONTRACT.md`.

---

# Phase 2 — Registration + Identity

### [ ] 8. Implement department endpoint

```text
GET /api/departments
```

### [ ] 9. Implement registration location validation

Verify:
- location exists
- active
- department valid

### [ ] 10. Implement patient lookup/creation

Rules:
- normalize mobile
- create patient if new
- reuse existing patient identity where appropriate

### [ ] 11. Implement verification policy

Support:

```text
development:
verification disabled only by explicit configuration

deployed:
OTP verification enabled when configured
```

Create provider-neutral interface.

### [ ] 12. Implement duplicate active-visit check

Same patient + same department + active visit:

```text
return existing visit
do not create another token
```

### [ ] 13. Implement transaction-safe token generation

Must prevent duplicate token allocation under simultaneous registration requests.

### [ ] 14. Test registration using curl/API client

Verify:
- valid registration
- invalid fields
- duplicate active visit
- different department
- repeat after completion
- simultaneous registration attempt

---

# WEEK 2 — QUEUE + FRONTEND INTEGRATION

# Phase 3 — Queue State Machine

### [ ] 15. Implement plain Python queue transition functions

Required states:

```text
WAITING
SERVING
HOLD
SKIPPED
COMPLETED
```

Required actions:

```text
CALL NEXT
HOLD
RECALL
SKIP
COMPLETE
TRANSFER
```

Test state transitions independently from HTTP.

### [ ] 16. Implement call-next ordering

Queue ordering must consider:
- active status
- priority
- queue position/time
- configured policy

Do not let frontend decide eligibility.

### [ ] 17. Implement missed-turn behavior

```text
SERVING
→ RECALL
→ HOLD if still absent
→ continue queue
```

### [ ] 18. Implement staff queue endpoints

```text
POST /api/staff/queue/{department_id}/next
POST /api/staff/token/{token_id}/hold
POST /api/staff/token/{token_id}/recall
POST /api/staff/token/{token_id}/skip
POST /api/staff/token/{token_id}/complete
POST /api/staff/token/{token_id}/transfer
```

### [ ] 19. Implement priority endpoint

```text
NORMAL
PRIORITY
EMERGENCY
```

Enforce staff role authorization.

### [ ] 20. Implement consultation timing

Capture:
- called time
- completed time
- consultation duration

---

# Phase 4 — Staff Authentication

### [ ] 21. Implement login
- password hashing
- secure cookie session
- CSRF protection for state-changing browser requests

- password hashing
- secure session
- login rate limiting
- logout
- `/api/auth/me`

### [ ] 22. Implement staff roles

Minimum:

```text
ADMIN
STAFF
```

Authorization must be backend enforced.

---

# Phase 5 — Patient Status

### [ ] 23. Implement patient status endpoint

```text
GET /api/status/{status_access_id}
```

Return:
- token
- current token
- patients ahead
- estimated wait
- department
- room
- status

### [ ] 24. Connect frontend status page

Replace mock API with real API.

### [ ] 25. Verify private status access

Test:
- valid private identifier
- invalid identifier
- expired/invalid session where applicable
- private data not leaking through public endpoints

---

# Phase 6 — Staff Dashboard

### [ ] F5. Staff login page
### [ ] F6. Dashboard skeleton
### [ ] F7. Connect queue cards
### [ ] F8. Connect queue actions
### [ ] F9. Connect priority/transfer
### [ ] F10. Connect occupancy display

After every action:
- call backend
- re-fetch authoritative state
- redraw

---

# Phase 7 — Public Display

### [ ] 26. Implement display endpoint

```text
GET /api/display/{department_id}
```

### [ ] F11. Build public display UI

Verify:
- large readable token
- room
- next token
- no private data

### [ ] 27. Start display on separate laptop/TV browser

---

# WEEK 3 — HARDWARE + INTEGRATION + FIXES

# Phase 8 — Occupancy Backend

### [ ] 28. Implement device records

Each device:
- ID
- credential
- zone
- active status

### [ ] 29. Implement device event endpoint

```text
POST /api/devices/{device_id}/events
```

### [ ] 30. Implement event idempotency

Retried events must not increment occupancy twice.

### [ ] 31. Implement zone occupancy endpoint

```text
GET /api/zones/{zone_id}/occupancy
```

### [ ] 32. Implement crowd levels

Configured:

```text
NORMAL
MODERATE
HIGH
CRITICAL
```

### [ ] 33. Implement occupancy correction

Admin/Supervisor only.
Reason required.
Audit event required.

---

# Phase 9 — ESP32

### [ ] 34. Build sensor direction detection

```text
A → B = ENTRY
B → A = EXIT
```

### [ ] 35. Add debounce/state timeout

### [ ] 36. Add authenticated API request

### [ ] 37. Add event ID/retry behavior

### [ ] 38. Bench test

Test:
- A→B
- B→A
- false trigger
- rapid repeated trigger
- sequence timeout
- Wi-Fi failure
- reconnect

### [ ] 39. Connect real backend

Confirm server occupancy changes from actual sensor events.

---

# Phase 10 — Analytics

### [ ] 40. Implement analytics queries

Required:
- total patients
- completed patients
- average waiting time
- average consultation time
- peak occupancy
- peak time
- department-wise waiting
- longest queue

### [ ] F12. Build analytics UI

Charts are optional visual polish after the values are correct.

---

# Phase 11 — Notifications

### [ ] 41. Implement provider-neutral notification interface

```text
NotificationService
 ├── SMS
 └── WhatsApp
```

### [ ] 42. Enable one provider only if time/credentials are available

Do not let notification setup block the core queue system.

Browser status remains mandatory.

---

# Phase 12 — QR Administration

### [ ] 43. Create admin registration-location management

### [ ] F13. Build QR management UI

Admin can:
- create location
- select department
- activate/deactivate
- generate/download QR

---

# Phase 13 — End-to-End Integration

### [ ] 44. Full patient flow

```text
Scan QR
→ register
→ verify according to policy
→ receive token
→ open private status
```

### [ ] 45. Full staff flow

```text
Login
→ view queue
→ call
→ recall/hold/skip
→ complete
→ transfer
```

### [ ] 46. Display flow

```text
Call next
→ display updates
→ patient status updates
```

### [ ] 47. Hardware flow

```text
Person enters
→ ESP32
→ backend
→ occupancy changes
→ dashboard updates
```

---

# Phase 14 — Security/Failure Tests

### [ ] 48. Registration abuse

Test:
- repeated registration
- repeated OTP request
- invalid anti-bot token
- rate-limit behavior

### [ ] 49. Duplicate visit

Test:
- same patient + same department while active
- same patient after completion
- same patient in different department

### [ ] 50. Queue correctness

Test every state/action combination.

### [ ] 51. Staff authorization

Test:
- unauthenticated request
- STAFF attempting ADMIN action
- valid role
- expired session

### [ ] 52. Device authentication

Test:
- unknown device
- wrong credential
- disabled device
- duplicate event

### [ ] 53. Privacy

Confirm public display and public endpoints never return:
- names
- phone numbers
- unnecessary patient fields

---

# Phase 15 — Fix-Only Freeze

### [ ] 54. Freeze feature additions

From this point:
- no new major features
- fix defects
- improve reliability
- improve presentation
- improve documentation

---

# Phase 16 — Deployment

### [ ] 55. Local deployment rehearsal

Run full system locally.

### [ ] 56. Hosted deployment

Frontend:
- hosted public URL

Backend:
- HTTPS FastAPI service

Database:
- PostgreSQL

### [ ] 57. Configure production environment variables

Never commit:
- passwords
- API keys
- OTP provider secrets
- device secrets

### [ ] 58. Generate actual demo QR codes

Print/prepare department QR codes.

### [ ] 59. Test from an independent phone

Do not test only from the development laptop.

---

# Phase 17 — Demo Readiness

### [ ] 60. Demonstrate patient registration

### [ ] 61. Demonstrate duplicate prevention

### [ ] 62. Demonstrate staff login

### [ ] 63. Demonstrate queue control

### [ ] 64. Demonstrate missed token + recall

### [ ] 65. Demonstrate transfer

### [ ] 66. Demonstrate priority handling

### [ ] 67. Demonstrate public display

### [ ] 68. Demonstrate ESP32 occupancy

### [ ] 69. Demonstrate analytics

### [ ] 70. Demonstrate audit trail

### [ ] 71. Demonstrate failure/fallback behavior

---

# Final Rule

The minimum complete system is:

```text
QR
→ Patient Registration
→ Patient Verification Policy
→ Duplicate Prevention
→ Visit + Token
→ Private Status
→ Staff Login
→ Queue State Machine
→ Public Display
→ ESP32 Occupancy
→ Audit
→ Basic Analytics
```

Optional features must never break this chain.

When time becomes tight:
1. remove visual polish
2. reduce analytics complexity
3. reduce notification scope
4. reduce deployment extras

Do **not** remove:
- backend validation
- queue correctness
- staff authorization
- patient/private identifier separation
- device authentication
- duplicate prevention
- auditability
- privacy controls


# Human-in-the-loop rule

For every numbered feature, record: requirement understood, AI plan reviewed, diff reviewed, tests run, and one sentence explaining the important business rule in your own words. AI may write the code; the human must own the behavior.
