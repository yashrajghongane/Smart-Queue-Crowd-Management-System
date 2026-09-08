# Smart Queue & Crowd Management System — Agent Instructions

## 0. Purpose

You are an AI coding agent working inside the Smart Queue & Crowd Management System repository.

Your job is to implement the project correctly, incrementally, and readably while preserving the approved architecture and project scope.

You are allowed to write most or all project code.

You are NOT allowed to silently redesign the system.

The repository documentation is the source of truth.

---

# 1. Source of Truth

Before making meaningful code changes, read the relevant files in `docs/`.

Primary documents:

```text
docs/01_TECHNICAL_PRD.md
docs/02_API_CONTRACT.md
docs/03_DATABASE_SCHEMA.md
docs/04_FRONTEND_BUILD_MAP.md
docs/05_BUILD_ORDER_CHECKLIST.md
docs/06_SECURITY_PRIVACY_NFR.md
docs/07_AI_HUMAN_IN_LOOP_PLAYBOOK.md
```

Jules-specific guidance:

```text
docs/JULES_MASTER_CONTEXT.md
docs/JULES_FIRST_BOOT_PROMPT.md
docs/JULES_TASK_TEMPLATE.md
```

When two documents appear to conflict:

1. Do NOT choose silently.
2. Identify the conflict.
3. Determine whether the conflict can be resolved from the existing documentation.
4. If it materially affects architecture, API, database, security, or behavior, ask for clarification before implementation.
5. Never invent a new contract just to make coding easier.

---

# 2. Project Objective

The system is a smart hospital/clinic/OPD queue and crowd-management platform.

Core flow:

```text
Public QR
→ Registration
→ Verification / abuse controls
→ Patient identity
→ Visit
→ Department-specific token
→ Private patient status
→ Staff queue management
→ Public token display
→ Consultation completion
→ Operational analytics
```

Hardware flow:

```text
Sensor A/B
→ ESP32
→ authenticated device event
→ backend
→ occupancy state
→ staff dashboard
```

The system is NOT:

- a diagnosis system
- a treatment system
- an automated medical-triage system
- a replacement for a complete HMIS
- a guarantee of exact waiting time
- a guarantee of perfect crowd counting

Never add functionality that violates these boundaries.

---

# 3. Core Architecture

Preferred stack:

```text
Frontend:
HTML + CSS + JavaScript

Backend:
Python + FastAPI

Database:
SQLite for local development
PostgreSQL for hosted deployment

Hardware:
ESP32 + two sequential sensors

Communication:
REST/HTTP + polling initially
```

Do not introduce React, WebSockets, Redis, Docker, microservices, message brokers, Kubernetes, or other infrastructure merely because they are fashionable.

Add technology only when:
- the specification requires it, or
- there is a demonstrated technical reason,
- and the change is approved.

Prefer a simple system that can be understood and defended.

---

# 4. Mandatory Domain Separation

These concepts are different:

```text
Patient
Visit
Queue Token
Public Display Token
Private Status Identifier
Staff Account
Device
Zone
```

Do NOT collapse them into one ID.

The visible token such as `G125` is public queue information.

It is NOT:
- the patient's identity
- a password
- a private status credential
- an internal database primary key

Patient status uses an unpredictable private status identifier.

---

# 5. Backend Owns Business Logic

The backend is authoritative for:

- patient identity handling
- verification policy
- duplicate active-visit prevention
- token generation
- queue ordering
- queue state transitions
- priority behavior
- transfer
- consultation timing
- waiting-time calculation
- authentication
- authorization
- occupancy processing
- device authentication
- audit logging
- analytics

The frontend must never be trusted to enforce business rules.

Examples:

BAD:

```text
Frontend decides who is next.
```

GOOD:

```text
Frontend asks backend to call next.
Backend determines eligible token.
```

BAD:

```text
Frontend generates G125.
```

GOOD:

```text
Backend generates and persists G125.
```

---

# 6. Queue State Machine

Persistent token states are exactly:

```text
WAITING
SERVING
HOLD
SKIPPED
COMPLETED
```

`RECALL` is an action, not a permanent state.

Important behavior:

```text
WAITING
→ SERVING

SERVING
→ HOLD

HOLD
→ SERVING

SERVING
→ SKIPPED

SERVING
→ COMPLETED
```

Missed patient behavior:

```text
SERVING
→ RECALL
→ HOLD if still absent
→ queue continues
→ later RECALL possible
```

Do not invent additional persistent states without approval.

---

# 7. Priority / Emergency Safety Boundary

Priority values:

```text
NORMAL
PRIORITY
EMERGENCY
```

The system records and applies authorized operational priority.

The system must NOT:
- diagnose
- infer medical severity
- automatically decide that someone is an emergency
- allow a patient to self-promote directly into an emergency queue

Priority is assigned or confirmed by authorized staff/clinical personnel.

Current serving consultation is not automatically interrupted by software.

---

# 8. Registration and QR

The physical QR is PUBLIC.

Treat the QR as a registration entry point, not a secret.

QR should identify:
- an opaque registration-location identifier
- department/location context

QR must never contain:
- API keys
- staff credentials
- device secrets
- patient private identifiers

Public registration must use layered controls:

```text
QR/location validation
→ anti-automation challenge when enabled
→ rate limiting
→ verification policy
→ duplicate active-visit rule
```

Never claim that a copied QR can be detected merely because it was copied.

---

# 9. Duplicate Registration Rule

Patients may have multiple historical visits.

Duplicate prevention applies to ACTIVE visits.

Recommended business rule:

```text
same patient
+
same department/service
+
active visit
=
do not create another active token
```

Completed/terminal visits do not permanently prevent future visits.

Do not implement:

```text
one mobile number = one lifetime token
```

---

# 10. Patient Verification

Verification must be provider-neutral.

Do not hard-code one SMS/WhatsApp provider throughout the application.

Use an abstraction such as:

```text
VerificationService
```

with a provider implementation beneath it.

Development-only verification bypass must be explicitly configuration-controlled.

Never hard-code a universal OTP in production code.

Phone OTP proves control of a phone number. It does not by itself prove medical identity.

---

# 11. Authentication and Authorization

Staff dashboard requires authentication.

Minimum roles:

```text
ADMIN
STAFF
```

Architecture may support additional roles later:

```text
RECEPTION
QUEUE_OPERATOR
SUPERVISOR
DOCTOR
```

Rules:

- passwords are never stored in plaintext
- use secure password hashing
- use secure authenticated sessions
- use `HttpOnly` and `Secure` cookies in hosted deployment
- use appropriate `SameSite` settings
- protect state-changing browser requests against CSRF
- rate-limit login attempts
- enforce authorization in the backend
- hiding a button is NOT authorization

Do not store staff session credentials in frontend localStorage unless explicitly approved by the security specification.

---

# 12. CORS / HTTPS / Secrets

Hosted deployment must use HTTPS.

CORS must use an explicit allow-list of trusted frontend origins.

Do NOT use wildcard CORS with credentialed requests.

Never commit:

```text
passwords
API keys
OTP secrets
notification provider keys
device secrets
database passwords
session secrets
```

Use environment variables or platform secret storage.

Keep:

```text
.env
```

out of Git.

Commit:

```text
.env.example
```

with placeholders only.

---

# 13. Database Rules

Use migrations for schema changes.

Do not manually modify production database schema without migration history.

Critical integrity rules should exist at both:

```text
application/business-logic level
+
database constraint/index level where practical
```

Important concerns:

- unique private status identifiers
- token uniqueness according to configured sequence policy
- event ID uniqueness for idempotency
- staff usernames
- appropriate foreign keys
- useful indexes

Use an ORM/database abstraction so local SQLite and hosted PostgreSQL remain practical.

---

# 14. Token Numbering

Token numbering must be deterministic and transaction-safe.

Configuration should define:

```text
department prefix
sequence scope
operating day
starting number
timezone
```

Default policy:

```text
one sequence per department per operating day
```

Example:

```text
G101
G102
G103
```

Do not use an unsafe naïve implementation that can produce duplicate tokens under simultaneous registration.

---

# 15. Queue Concurrency

Queue actions may be triggered by multiple staff users or repeated browser requests.

Protect against:

- double-clicked actions
- duplicate requests
- two staff users calling next simultaneously
- completing an already completed token
- transferring the same token twice
- invalid state transitions

Use database transactions/locking appropriate to the database.

Do not assume requests arrive one at a time.

---

# 16. API Contract

The API contract in:

```text
docs/02_API_CONTRACT.md
```

is authoritative.

Do not rename endpoints or fields for convenience.

Examples include:

```text
GET  /api/health

GET  /api/departments

POST /api/patient/verification/start
POST /api/patient/verification/confirm

POST /api/register

GET  /api/status/{status_access_id}

POST /api/auth/login
POST /api/auth/logout
GET  /api/auth/me

GET  /api/staff/queues

POST /api/staff/queue/{department_id}/next
POST /api/staff/token/{token_id}/hold
POST /api/staff/token/{token_id}/recall
POST /api/staff/token/{token_id}/skip
POST /api/staff/token/{token_id}/complete
POST /api/staff/token/{token_id}/transfer

POST /api/staff/token/{token_id}/priority

GET  /api/display/{department_id}

POST /api/devices/{device_id}/events
GET  /api/zones/{zone_id}/occupancy

POST /api/staff/zones/{zone_id}/occupancy-correction

GET /api/staff/analytics
```

Use the exact current contract in the file rather than relying on this abbreviated list if there is any difference.

---

# 17. Public Display Privacy

Public display must be read-only.

It may show:

```text
Department
Current token
Next token
Room
```

It must NOT show:

```text
patient name
mobile
date of birth
diagnosis
private status identifier
```

Create/use a display-specific API response rather than reusing a broad staff response.

---

# 18. Patient Status Privacy

Patient status URL uses:

```text
random/unpredictable status_access_id
```

Do not use:

```text
G125
database integer 42
patient integer 17
```

as the private credential.

Do not expose internal database identifiers unnecessarily.

Only return the data required for the patient's queue status.

---

# 19. Occupancy System

Hardware flow:

```text
A → B = ENTRY
B → A = EXIT
```

Backend rules:

```text
ENTRY → occupancy + 1
EXIT  → occupancy - 1
```

Never allow occupancy to become negative.

ESP32 events require:
- authenticated device
- event ID
- timestamp
- valid event type
- idempotent processing

Same event retried twice must not count twice.

Occupancy is explicitly an estimate for the monitored zone.

---

# 20. ESP32 Behavior

Firmware should implement:

- sensor reading
- direction detection
- debounce/filtering
- sequence timeout
- invalid sequence rejection
- event ID generation
- authenticated API communication
- Wi-Fi reconnect
- retry behavior
- local buffering when practical

Do not start physical doorway integration before bench testing.

---

# 21. Zones and Devices

Occupancy must be modeled around configurable zones.

Example:

```text
Zone:
Waiting Area A
Capacity:
30
Device:
ESP32-01
Doorway:
A
```

Architecture should permit multiple devices/zones later without requiring a redesign.

---

# 22. Notifications

Use a provider-neutral notification interface.

Concept:

```text
NotificationService
├── SMS
└── WhatsApp
```

The queue engine must not contain vendor-specific code.

Browser status remains the primary status mechanism.

Do not make the project dependent on a notification provider to function.

---

# 23. Waiting-Time Estimation

Initial estimate:

```text
patients ahead
×
recent average consultation duration
```

Prefer department/doctor-specific recent data when enough historical data exists.

Always call it:

```text
Estimated Wait
```

Never claim a guaranteed appointment time.

---

# 24. Analytics

Required basic analytics include:

```text
total patients
completed patients
average waiting time
average consultation time
peak occupancy
peak time
department-wise waiting
longest queue
```

Do not build complex analytics infrastructure before core queue reliability.

---

# 25. Audit Logging

Important actions must produce audit records.

Examples:

```text
login
logout
registration correction
token generated
call
hold
recall
skip
complete
transfer
priority change
occupancy correction
room change
configuration change
device enable/disable
```

Audit should identify:

```text
who/what actor
role or device
what happened
which entity
when
relevant before/after information
```

Normal users should not rewrite historical audit records.

---

# 26. Frontend Rules

Frontend must:

- use the API contract exactly
- use mock JSON before the real backend exists
- use a centralized API layer
- handle loading states
- handle empty states
- handle validation errors
- handle network errors
- show degraded/offline status when appropriate
- never generate authoritative tokens
- never calculate authoritative queue ordering
- never contain secrets
- never expose private information on the public display

The frontend should be readable by a student who did not write it.

Prefer:
- descriptive names
- small functions
- simple control flow
- comments for WHY, not obvious WHAT
- limited abstraction
- consistent formatting

---

# 27. Code Quality Rules

Write code that is easy to read before optimizing it.

Prefer:

```text
clear
boring
explicit
testable
```

over:

```text
clever
compressed
magical
over-abstracted
```

Avoid:
- giant functions
- giant files
- unexplained metaprogramming
- unnecessary design patterns
- copy-pasted business logic
- magic numbers
- hard-coded configuration

Use:
- typed Python where practical
- clear module boundaries
- small service functions
- validation models
- structured errors
- tests for important logic

---

# 28. Project Structure

Prefer this structure unless an existing implementation has a justified alternative:

```text
backend/
  app/
    main.py
    api/
    models/
    schemas/
    services/
    database/
    auth/
    core/
  tests/

frontend/
  patient/
  staff/
  display/
  admin/
  shared/

firmware/
  esp32/

docs/
```

Do not create a new architectural layer merely because it has a sophisticated name.

---

# 29. Testing Requirements

Every backend feature should have relevant tests.

Priority areas:

```text
registration
duplicate visits
token generation
queue state transitions
priority ordering
missed patient behavior
transfer
authentication
authorization
status access
occupancy processing
device authentication
idempotency
analytics
```

At least test:
- happy path
- invalid input
- invalid state
- authorization failure
- retry/duplicate request where relevant

---

# 30. AI-Agent Behavior

Before implementation of a meaningful task:

1. Read the relevant docs.
2. Inspect the current repository.
3. Identify dependencies.
4. Produce a short implementation plan.
5. Identify risks.
6. Ask questions only when a decision is genuinely blocking.

Do not ask unnecessary questions that the docs already answer.

Before modifying major architecture:
- explain why
- identify affected files
- identify API/database consequences
- wait for approval if required

After implementation:
- run tests
- inspect errors
- review your own diff
- report changed files
- report tests run
- report known limitations

---

# 31. Never Hide Problems

If you encounter:

```text
contradictory requirements
missing API definition
unsafe security behavior
ambiguous business rule
migration problem
broken test
deployment limitation
```

do not work around it silently.

State it clearly.

Do not make up a requirement simply to keep the task moving.

---

# 32. Human-in-the-Loop Learning Requirement

The project owner wants AI to write most/all of the code while still genuinely developing engineering skill.

Therefore, for important features, provide after implementation:

```text
What this feature does
Important design decision
Important business rule
Files changed
Tests run
One likely failure case
```

Do NOT flood the response with a line-by-line explanation unless requested.

For critical logic, explain enough that the project owner can understand and defend the implementation.

Critical areas include:

```text
token generation
queue ordering
state machine
duplicate prevention
transactions/concurrency
authentication
authorization
sessions
status access
device authentication
occupancy direction
analytics calculations
```

---

# 33. Implementation Style for Learning

When a feature is non-trivial:

1. State the intended behavior in plain language.
2. Show a small plan.
3. Implement.
4. Test.
5. Explain the important code path.
6. Mention one failure case.

Do not replace learning with massive generated explanations.

---

# 34. Task Scope

Prefer one bounded task at a time.

Good:

```text
Implement POST /api/register with validation and tests.
```

Bad:

```text
Build the whole backend.
```

Good:

```text
Implement WAITING → SERVING transition and tests.
```

Bad:

```text
Fix the queue.
```

Do not modify unrelated parts of the repository.

---

# 35. Git Rules

Use feature branches.

Do not casually modify `main`.

Keep commits focused.

Commit messages should describe what changed.

Before merge/PR:
- tests pass
- relevant diff reviewed
- no unrelated file churn
- docs updated if behavior/contract changed

Do not rewrite existing history unless explicitly instructed.

---

# 36. Development Order

Follow the dependency order:

```text
1. Repository/environment
2. FastAPI skeleton
3. Database + migrations
4. Seed departments/rooms
5. Patient identity
6. Verification abstraction
7. Registration
8. Duplicate active-visit protection
9. Transaction-safe token generation
10. Queue state machine
11. Queue API
12. Staff authentication/authorization
13. Patient status
14. Staff dashboard integration
15. Public display
16. Consultation timing
17. Waiting-time estimation
18. Occupancy backend
19. ESP32
20. Analytics
21. Notifications
22. QR administration
23. Security hardening
24. Full integration
25. Failure testing
26. Deployment
27. Demo preparation
```

Frontend work may proceed in parallel with mock JSON once the API contract is frozen.

---

# 37. Definition of Done

A task is not done simply because code exists.

For meaningful tasks:

```text
[ ] requirements understood
[ ] relevant docs read
[ ] implementation scoped
[ ] code written
[ ] tests written/updated
[ ] tests pass
[ ] errors handled
[ ] API contract preserved
[ ] security implications considered
[ ] no unrelated files changed
[ ] code readable
[ ] summary prepared
```

For user-visible features also verify actual browser behavior.

For hardware features also verify real or bench behavior where applicable.

---

# 38. Final System Acceptance Flow

The complete system should eventually demonstrate:

```text
Physical QR
→ public registration
→ anti-abuse/verification
→ patient identity
→ active-visit duplicate prevention
→ department token
→ private status page
→ staff login
→ call next
→ public display update
→ patient status update
→ missed patient handling
→ recall/hold
→ transfer
→ priority handling
→ complete consultation
→ analytics
→ ESP32 entry/exit
→ occupancy update
→ audit event
```

Do not consider the project complete until the core end-to-end flow works.

---

# 39. When Time Is Running Out

If schedule pressure appears:

POSTPONE/REDUCE:

```text
advanced analytics
notification-provider integration
extra UI polish
advanced hardware features
multi-doctor complexity
extra departments
```

Do NOT sacrifice:

```text
registration
token generation
queue correctness
authentication
authorization
duplicate protection
patient status
public display
basic occupancy
auditability
testing
```

---

# 40. Final Agent Principle

Your goal is not to maximize lines of code.

Your goal is to produce:

```text
correct behavior
+
clear architecture
+
readable code
+
tested system
+
defensible engineering decisions
```

When in doubt:

```text
Understand
→ Plan
→ Implement
→ Test
→ Inspect
→ Explain
→ Continue
```