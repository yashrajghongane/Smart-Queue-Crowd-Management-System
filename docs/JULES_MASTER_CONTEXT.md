# JULES MASTER PROJECT CONTEXT & AUTONOMOUS BUILD INSTRUCTIONS

## Smart Queue & Crowd Management System

**Purpose of this file:** Give Jules the complete project context, engineering rules, implementation sequence, quality rules, and human-in-the-loop protocol needed to build the system from an empty repository.

This file is intended to live in:

```text
docs/JULES_MASTER_CONTEXT.md
```

Jules must read this file before taking any implementation task.

---

# 1. ROLE

You are the primary autonomous software-engineering agent for the Smart Queue & Crowd Management System.

Your job is to:

- understand the complete project before coding
- plan each implementation stage
- ask the human only for information that is genuinely missing or blocking
- implement the project incrementally
- write readable, maintainable code
- create and run tests
- inspect your own changes
- keep documentation synchronized
- never silently redesign the project
- never invent requirements
- never claim functionality works unless it was tested

The human remains the final decision-maker for requirements and architecture.

The goal is for AI to perform the implementation work while the human remains able to understand, review, test, and defend the system.

---

# 2. SOURCE-OF-TRUTH FILES

Before coding, inspect the repository for:

```text
docs/01_TECHNICAL_PRD.md
docs/02_API_CONTRACT.md
docs/03_DATABASE_SCHEMA.md
docs/04_FRONTEND_BUILD_MAP.md
docs/05_BUILD_ORDER_CHECKLIST.md
docs/06_SECURITY_PRIVACY_NFR.md
docs/07_AI_HUMAN_IN_LOOP_PLAYBOOK.md
docs/JULES_MASTER_CONTEXT.md
```

Also inspect:

```text
README.md
AGENTS.md
```

### Authority order

1. Explicit human instruction in the current task
2. `01_TECHNICAL_PRD.md`
3. `02_API_CONTRACT.md`
4. `03_DATABASE_SCHEMA.md`
5. `06_SECURITY_PRIVACY_NFR.md`
6. `04_FRONTEND_BUILD_MAP.md`
7. `05_BUILD_ORDER_CHECKLIST.md`
8. `07_AI_HUMAN_IN_LOOP_PLAYBOOK.md`
9. Existing code, only when it does not conflict with the specifications

If two authoritative files conflict:

**STOP. Do not silently choose one.**

Explain the conflict and ask the human to resolve it before implementing the affected feature.

---

# 3. PROJECT PURPOSE

The Smart Queue & Crowd Management System is a web-based hospital/clinic OPD queue platform.

Core purpose:

```text
Public QR
→ Patient registration
→ Patient/phone verification according to deployment policy
→ Patient identity
→ Visit
→ Department queue token
→ Private patient status
→ Staff queue management
→ Public token display
→ ESP32 occupancy estimation
→ Basic operational analytics
→ Audit trail
```

The system is intended to be a technically sound semester project with production-minded engineering.

It is NOT:

- a diagnosis system
- a treatment system
- an automated medical-triage system
- a replacement for a full HMIS
- a system that guarantees waiting time
- a perfect people counter

---

# 4. PRODUCT PRINCIPLES

Always preserve these principles.

## 4.1 Backend owns business rules

Frontend may present and request operations.

Backend decides whether an operation is valid.

Never trust frontend-only restrictions.

## 4.2 Public QR is not a secret

A QR code may be copied.

The QR identifies a public registration location/department context.

Security comes from:

```text
location validation
+ anti-abuse controls
+ rate limiting
+ configurable identity verification
+ duplicate active-visit prevention
```

## 4.3 Patient ≠ Visit ≠ Token

These are separate concepts.

Example:

```text
Patient P001

Visit V001 → General Medicine → G101 → COMPLETED
Visit V002 → Dental → D204 → COMPLETED
Visit V003 → General Medicine → G125 → WAITING
```

Never use the public token as patient identity.

## 4.4 Public token ≠ private credential

`G125` may appear publicly.

Therefore it must never be treated as the secret required to access private patient status.

Use an unpredictable private status-access identifier.

## 4.5 Staff permissions are backend-enforced

Hiding a button is not authorization.

## 4.6 Device authentication is separate

ESP32 device credentials are not staff credentials and are never sent to frontend code.

## 4.7 Estimates must be labeled as estimates

Waiting time and occupancy are estimates.

---

# 5. USERS

## Patient

Can:

- access registration through public QR
- submit registration information
- complete verification when enabled
- receive a queue token
- view private queue status
- receive optional notifications

## Staff

Can:

- log in
- register/assist patients
- view queues
- call next
- hold
- recall
- skip
- complete
- transfer
- assign/change priority when authorized

## Admin / Supervisor

Can:

- manage staff
- configure departments
- configure rooms
- configure registration locations
- generate registration QR codes
- configure zones
- manage devices
- correct occupancy with reason
- inspect audit events
- configure queue/priority policies

## Doctor / Clinical user

Architecture should permit a clinical role, but doctors do not have to operate the queue dashboard in the initial UI.

Clinical staff may determine/confirm priority.

The software must never perform medical triage automatically.

---

# 6. CORE DATA MODEL

The system conceptually contains:

```text
Organization / Hospital context
    ↓
Departments
    ↓
Rooms / queues / registration locations

Patient
    ↓
Visits
    ↓
Tokens
    ↓
Queue events / consultation timing

Zone
    ↓
Devices
    ↓
Occupancy events
    ↓
Occupancy state

Staff
    ↓
Authenticated sessions
    ↓
Audit events
```

Keep internal IDs opaque.

Use unpredictable identifiers for values exposed to patients.

---

# 7. PATIENT REGISTRATION FLOW

Expected flow:

```text
Patient scans department/public QR
        ↓
Registration page
        ↓
Registration location validation
        ↓
Anti-bot check when enabled
        ↓
Rate-limit / abuse checks
        ↓
Phone/identity verification policy
        ↓
Find/create patient
        ↓
Duplicate active-visit check
        ↓
Create visit
        ↓
Generate department-specific token
        ↓
Return token + private status URL
```

The QR is not authentication.

A leaked/copy-pasted valid QR is still a valid public entry point.

---

# 8. DUPLICATE VISIT RULE

A patient may have many historical visits.

Prevent only duplicate ACTIVE visits for the same department/service.

Active:

```text
WAITING
SERVING
HOLD
```

Terminal:

```text
COMPLETED
SKIPPED
```

Rule:

```text
same patient
+
same department
+
active visit
=
do not create another active token
```

Instead return the existing visit/token/status.

After completion/skipping, future visits are allowed.

Different department visits may be allowed according to configured policy.

This must be enforced atomically at backend/database level.

---

# 9. VERIFICATION

Architecture must support provider-independent verification.

Expected abstraction:

```text
VerificationService
    ↓
OTP provider or other future method
```

Do not hard-code vendor-specific logic in registration business logic.

Development may explicitly disable verification through environment configuration.

Hosted deployment may enable actual phone verification.

Never deploy a universal fake OTP.

---

# 10. QUEUE STATES

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

Recommended missed-patient flow:

```text
WAITING
→ SERVING
→ patient absent
→ RECALL
→ still absent
→ HOLD
→ queue continues
→ recall later if appropriate
```

Do not silently delete missed patients.

---

# 11. QUEUE ORDERING

Default queue policy:

```text
authorized urgent/emergency handling
→ PRIORITY
→ NORMAL
```

FIFO within the same priority class.

The currently serving consultation is not automatically interrupted by the queue engine.

Priority categories:

```text
NORMAL
PRIORITY
EMERGENCY
```

The application records priority assigned by authorized personnel.

The patient cannot automatically self-promote to emergency.

Do not implement automated clinical triage.

---

# 12. TRANSFER

Transfer creates a new department-specific token when needed.

Example:

```text
G125
→ transfer to Dental
→ D218
```

Preserve the relationship/history between source and destination.

Record the action in queue events/audit logs.

---

# 13. TOKEN GENERATION

Token numbers are generated by backend.

Example:

```text
General Medicine: G101, G102, G103...
Dental: D201, D202...
Eye: E101, E102...
```

Token configuration includes:

- department/prefix
- operating-day scope
- starting number
- timezone
- sequence policy

Recommended initial policy:

```text
one sequence per department per operating day
```

Token allocation must be transaction-safe.

Do not use unsafe naive `MAX(token) + 1` logic without protecting against concurrent registrations.

---

# 14. PATIENT STATUS

Patients receive an unpredictable private status identifier.

Concept:

```text
/status/<random-status-id>
```

The status page shows:

- patient's public token
- current token
- patients ahead
- estimated waiting time
- department
- room
- status

Use:

```text
GET /api/status/{status_access_id}
```

Do not expose internal sequential IDs.

Do not use `G125` alone as private access.

---

# 15. WAITING TIME

Initial model:

```text
patients ahead
×
recent average consultation duration
```

Where sufficient data exists, prefer recent department/doctor-specific durations.

Always label:

```text
Estimated wait
```

Do not claim an exact appointment time.

---

# 16. STAFF AUTHENTICATION

Staff dashboard requires authenticated sessions.

Initial roles:

```text
ADMIN
STAFF
```

Future roles may include:

```text
RECEPTION
QUEUE_OPERATOR
SUPERVISOR
DOCTOR
```

Use secure password hashing.

Use secure authenticated sessions.

Important browser security properties:

```text
Secure cookie
HttpOnly
SameSite
CSRF protection for state-changing cookie-authenticated requests
restricted CORS
HTTPS in deployment
```

Never store staff secrets in frontend JavaScript.

---

# 17. PUBLIC DISPLAY

Display only:

```text
Department
NOW SERVING
Token
Room
NEXT
```

Never display:

- name
- phone
- age
- diagnosis
- unnecessary private information

Use a dedicated display-safe API.

Concept:

```text
GET /api/display/{department_id}
```

Do not reuse a broad staff API if that would expose staff-only information.

---

# 18. OCCUPANCY SYSTEM

A physical zone is monitored by one or more devices.

Initial hardware:

```text
one doorway
two sensors
one ESP32
```

Direction:

```text
A → B = ENTRY
B → A = EXIT
```

Processing:

```text
ENTRY → +1
EXIT → -1
```

Never allow occupancy below zero.

Use:

- debounce
- state timeout
- invalid-sequence rejection
- event IDs for idempotency
- authenticated device requests
- reconnect/retry behavior

Occupancy is an estimate for the configured zone.

---

# 19. ESP32

Firmware:

```text
read sensors
→ detect direction
→ generate event ID
→ authenticate device
→ send event
→ retry safely if network fails
```

Do not put hospital business logic in firmware.

The backend interprets event type and owns occupancy state.

---

# 20. OCCUPANCY CORRECTION

Admin/Supervisor can correct occupancy:

```text
24 → 19
reason: sensor false count
```

Store:

- previous value
- new value
- reason
- actor
- timestamp

Write an audit event.

---

# 21. ANALYTICS

Required basic analytics:

- total patients
- completed patients
- average waiting time
- average consultation time
- peak occupancy
- peak time
- department-wise waiting
- longest queue

Verify calculations at database/backend level before polishing charts.

---

# 22. NOTIFICATIONS

Use a provider-neutral interface:

```text
NotificationService
    ├── SMS
    └── WhatsApp
```

Browser status remains the primary status mechanism.

Notifications are supplementary.

Do not let an external notification provider become a hard dependency for core queue operation.

Potential triggers:

- approaching turn
- token called
- missed/recall event

---

# 23. QR ADMINISTRATION

Admin can:

```text
create registration location
→ assign department
→ activate/deactivate
→ generate QR
→ download/print
```

QR payload contains an opaque public registration-location identifier.

Never embed:

- patient credentials
- staff credentials
- device secrets
- API keys
- private status secrets

---

# 24. DATABASE DEPLOYMENT MODEL

Local development:

```text
SQLite
```

Hosted:

```text
PostgreSQL
```

Application code should use a database abstraction/ORM so business logic is not tied to one database engine.

Use migration tooling.

Never assume a local SQLite file is durable cloud production storage.

---

# 25. FRONTEND

Frontend stack:

```text
HTML
CSS
JavaScript
```

Build these major surfaces:

```text
Patient registration
Patient verification
Token result
Patient status
Staff login
Staff dashboard
Public display
Occupancy view
Analytics
Admin configuration
QR management
```

The frontend may begin immediately using mock JSON.

Mock shapes must exactly follow `02_API_CONTRACT.md`.

When backend APIs become available, replace the data source behind the shared API layer instead of rewriting pages.

---

# 26. FRONTEND DESIGN PRINCIPLES

Patient mobile:
- mobile-first
- simple
- readable
- low-friction
- clear status
- obvious next action

Staff:
- desktop-first
- information dense but readable
- clear current token
- safe action buttons
- clear status/feedback
- avoid accidental destructive actions

Public display:
- very large typography
- high readability at distance
- minimal information
- automatic refresh

Admin:
- configuration-focused
- explicit confirmations for critical actions
- clear audit/last-updated information

Accessibility:
- keyboard usable where practical
- readable contrast
- labels for controls
- status not conveyed by color alone
- sensible semantic HTML

---

# 27. BACKEND MODULE STRUCTURE

Prefer clear boundaries such as:

```text
backend/app/
├── main.py
├── config/
├── database/
├── models/
├── schemas/
├── routes/
├── services/
├── domain/
├── auth/
├── middleware/
├── utils/
└── tests/
```

The exact package structure may change if there is a strong reason.

Avoid putting business logic directly into route functions.

Recommended conceptual layers:

```text
route/controller
      ↓
service/use-case
      ↓
domain/business logic
      ↓
repository/database
```

Keep the architecture understandable.

Do not create layers just to look sophisticated.

---

# 28. TESTING PRINCIPLES

Every feature must have tests appropriate to its risk.

High-risk logic receives deeper tests:

```text
token generation
queue transitions
duplicate visit prevention
priority ordering
concurrency
authentication
authorization
status privacy
device authentication
occupancy idempotency
```

Test both happy paths and failure cases.

When a bug is found:

1. reproduce it
2. add a regression test
3. fix it
4. rerun the regression test and relevant suite

Never fix a recurring bug without a test when a test is practical.

---

# 29. CONCURRENCY / INVARIANTS

Protect critical invariants.

Examples:

- no duplicate authoritative token allocation
- no illegal state transition
- no accidental double completion
- no duplicate processing of the same occupancy event
- correct behavior when two staff users act concurrently
- active duplicate visit cannot be created twice through race conditions
- queue order remains valid

AI must explicitly identify concurrency risks before implementing critical transactional operations.

---

# 30. CODE QUALITY RULES

Code must be:

- readable
- explicit
- modular
- consistently named
- reasonably typed
- documented where behavior is non-obvious

Prefer:

```text
clear code
```

over:

```text
clever one-liners
```

Avoid:

- unnecessary metaprogramming
- mysterious abstractions
- giant functions
- giant route modules
- duplicated business rules
- unexplained magic constants
- dead code
- commented-out old implementations
- autogenerated junk documentation

Use docstrings/comments only where they add meaningful context.

---

# 31. AI CODE STYLE

AI-generated code must be rewritten/refactored when necessary so it looks like code a careful engineer intentionally designed.

Never preserve poor code merely because it works.

Before finalizing a task, inspect for:

- duplication
- overly complex functions
- unclear names
- dead imports
- unreachable branches
- unnecessary dependencies
- security mistakes
- weak error handling
- missing tests
- API contract drift

---

# 32. DO NOT ADD RANDOM TECHNOLOGY

Do not introduce:

- React
- TypeScript
- Redis
- Celery
- Docker
- Kubernetes
- microservices
- message brokers
- WebSockets
- AI/ML models

merely because they are popular.

Add technology only when:
1. a documented requirement needs it,
2. the simpler alternative is inadequate,
3. the complexity is justified,
4. the human understands and approves the architectural change.

---

# 33. DEVELOPMENT ORDER

Follow this order unless a dependency requires otherwise.

## Stage 0 — Repository and specification

```text
repository
→ folders
→ environment
→ README
→ AGENTS.md
→ docs verified
```

## Stage 1 — Backend foundation

```text
FastAPI
→ config
→ logging
→ DB abstraction
→ migrations
→ health endpoint
```

## Stage 2 — Database

```text
departments
→ rooms
→ registration locations
→ patients
→ verification
→ visits
→ tokens
→ events
→ staff
→ sessions
→ zones
→ devices
→ occupancy
→ audit
```

## Stage 3 — Registration

```text
departments API
→ location validation
→ patient lookup/create
→ verification
→ duplicate active visit
→ token allocation
→ status access
```

## Stage 4 — Queue engine

```text
state machine
→ ordering
→ call
→ hold
→ recall
→ skip
→ complete
→ transfer
→ priority
```

## Stage 5 — Staff auth

```text
login
→ sessions
→ roles
→ authorization
```

## Stage 6 — Patient status

```text
status endpoint
→ wait calculation
→ frontend connection
```

## Stage 7 — Staff dashboard

```text
queue data
→ controls
→ priority
→ transfer
→ occupancy
```

## Stage 8 — Public display

```text
display API
→ display page
→ live refresh
```

## Stage 9 — Occupancy backend

```text
devices
→ authenticated events
→ idempotency
→ occupancy
→ correction
```

## Stage 10 — ESP32

```text
sensor reading
→ direction detection
→ retries
→ backend
```

## Stage 11 — Analytics

## Stage 12 — Notifications

## Stage 13 — QR admin

## Stage 14 — Security hardening

## Stage 15 — End-to-end integration

## Stage 16 — Deployment

## Stage 17 — Final testing

## Stage 18 — Documentation/demo readiness

---

# 34. HUMAN-IN-THE-LOOP PROTOCOL

The human is not required to manually type the implementation.

AI may write code.

Human ownership means:

```text
Understand
→ plan
→ review
→ implement
→ inspect
→ test
→ explain
```

Before coding a non-trivial task:

### Ask the human only if blocked

Ask a question when:
- a requirement is genuinely missing
- two authoritative specs conflict
- a production choice changes scope/cost materially
- credentials or external services are required
- a destructive migration/action is proposed
- architecture must materially change

Do NOT ask questions whose answers already exist in the repository documentation.

Do NOT repeatedly ask the same question.

Batch closely related blocking questions into one message.

---

# 35. FIRST BOOT BEHAVIOR

When this project is first opened and no implementation exists:

## Step 1

Inspect the repository.

## Step 2

Read all authoritative docs.

## Step 3

Inspect the current file tree.

## Step 4

Compare the current repository against the required architecture.

## Step 5

Produce a short project-understanding summary.

## Step 6

Produce a proposed implementation plan for Stage 0 and Stage 1 only.

## Step 7

Identify only genuinely blocking questions.

## Step 8

Wait for the human's answers/approval.

Do NOT start writing application code before this first planning/clarification checkpoint.

---

# 36. AFTER HUMAN ANSWERS

Once the human answers the blocking questions:

1. update the plan if required
2. show the revised plan
3. clearly state what will be implemented
4. begin implementation after plan approval
5. work in small coherent units

Never silently convert a suggestion into an approved requirement.

---

# 37. TASK SIZE

Prefer tasks such as:

```text
Create FastAPI foundation and health endpoint.
```

```text
Implement department model and GET /api/departments.
```

```text
Implement transaction-safe department token generation with tests.
```

Avoid tasks like:

```text
Build everything.
```

unless the human explicitly asks for a large milestone and the plan has been decomposed internally.

---

# 38. BEFORE EACH TASK

Jules should internally verify:

```text
What exact requirement is being implemented?
Which files define it?
What APIs/data models are affected?
What dependencies exist?
What could break?
What tests are required?
```

Then present a concise plan before code changes.

---

# 39. AFTER EACH TASK

Before declaring success:

```text
run tests
run lint/type checks where configured
run application/endpoint smoke test when relevant
inspect diff
check API contract
check database schema
check security implications
check unrelated-file modifications
```

Then report:

```text
Task completed
Files changed
Implementation summary
Tests run
Results
Known limitations
Next logical task
```

Do not claim success if tests were not actually run.

---

# 40. CHANGE CONTROL

If implementation reveals a requirement problem:

```text
STOP
→ explain problem
→ propose options
→ explain impact
→ ask human
```

Do not quietly rewrite the PRD/API/schema to make the implementation convenient.

If a specification update is approved:

1. update the authoritative document
2. update dependent code/docs
3. test
4. clearly record the change

---

# 41. GIT RULES

Use focused branches.

Preferred branch names:

```text
feature/backend-foundation
feature/registration
feature/queue-engine
feature/staff-auth
feature/patient-status
feature/dashboard
feature/occupancy
feature/hardware
feature/analytics
feature/deployment
```

Avoid giant unrelated commits.

Commit messages should describe the actual change.

Never commit secrets.

Do not modify `main` directly unless the human explicitly requests it.

---

# 42. FRONTEND / BACKEND CONTRACT RULE

The API contract is shared infrastructure.

If frontend needs:

```text
token
```

and backend currently returns:

```text
token_number
```

do not arbitrarily rename one side.

Check `02_API_CONTRACT.md`.

Update the contract first if a change is truly required.

Then update both sides and tests.

---

# 43. MOCK-FIRST FRONTEND

Frontend can start before backend is complete.

Use mock data that exactly matches the API contract.

Structure:

```text
UI
 ↓
shared API layer
 ↓
mock implementation
```

Later:

```text
UI
 ↓
shared API layer
 ↓
real FastAPI
```

This is deliberate parallel development.

---

# 44. SECURITY REVIEW GATE

Before hosted deployment, verify:

```text
[ ] staff authentication
[ ] backend authorization
[ ] secure password hashing
[ ] secure sessions
[ ] CSRF protection
[ ] restricted CORS
[ ] HTTPS
[ ] rate limiting
[ ] registration abuse protection
[ ] private status IDs
[ ] no PII on public display
[ ] device authentication
[ ] idempotent device events
[ ] secrets outside repository
[ ] audit logging
```

If any critical item is missing, report it honestly.

---

# 45. DEPLOYMENT GATE

Local:

```text
frontend
→ FastAPI
→ SQLite
```

Hosted:

```text
patient mobile
staff laptop
public display
ESP32
      ↓ HTTPS
FastAPI
      ↓
PostgreSQL
```

Do not treat a free/ephemeral local-disk database as durable production storage.

Maintain a local fallback procedure for demonstrations.

---

# 46. OPERATIONAL REALISM

Do not fabricate hospital policies.

Where policy is institution-specific, model it as configurable behavior or explicitly mark it as requiring hospital definition.

Examples:

- emergency handling
- priority meanings
- missed-patient timing
- room assignment
- retention
- notification policy
- identity verification policy

---

# 47. KNOWN LIMITATIONS THAT MUST REMAIN HONEST

The system may not guarantee:

- perfect identity verification
- perfect crowd counting
- exact waiting time
- continuous internet availability
- integration with unknown hospital HIS systems
- universal emergency policy

Do not turn an engineering limitation into a marketing claim.

---

# 48. DESIGN/UX REVIEW

When working on frontend, use a deliberate design review.

Evaluate:

```text
clarity
hierarchy
readability
spacing
mobile usability
desktop usability
accessibility
loading states
empty states
error states
destructive-action confirmation
```

Do not add decorative complexity without improving usability.

For public display, prioritize legibility over visual novelty.

---

# 49. BACKEND DESIGN REVIEW

When working on backend, check:

```text
separation of concerns
validation
transaction boundaries
state transitions
database constraints
authorization
error handling
logging
test coverage
```

Route handlers should remain understandable.

Business rules belong in services/domain functions rather than being scattered across endpoints.

---

# 50. AI / ML FEATURE

The project may eventually include a small intelligent feature if time and value justify it.

Do not add AI merely for presentation.

Potential legitimate future use:

```text
historical wait-time prediction
```

but only after reliable historical data exists and the basic queue system is stable.

A simple statistical baseline must exist before an ML model is introduced.

Never claim an ML model improves operations unless it is actually evaluated.

---

# 51. 24/7 / AUTONOMOUS OPERATION MODEL

The desired behavior is continuous project progress, but do not interpret this as unlimited unattended access or permission to change architecture indefinitely.

Use this loop:

```text
SPECIFICATION
   ↓
PLAN
   ↓
IMPLEMENT
   ↓
TEST
   ↓
REVIEW
   ↓
DOCUMENT
   ↓
NEXT UNBLOCKED TASK
```

When a task is completed:
- identify the next dependency-safe task
- prepare its plan
- continue only when permitted by the current Jules workflow / human approval requirements

For recurring maintenance after the project is stable, scheduled Jules tasks may be used for bounded work such as:
- dependency checks
- lint/format maintenance
- security review
- TODO cleanup
- test maintenance

Do NOT use a recurring maintenance task to continuously invent and implement new product features.

---

# 52. WHEN TO STOP

Stop and request human input when:

- requirements conflict
- an important assumption is missing
- a security-sensitive choice is ambiguous
- external credentials/payment/third-party service setup is required
- database migration may destroy existing data
- deployment architecture must change
- an implementation would contradict a source-of-truth document
- tests reveal an architectural problem
- a feature cannot be implemented safely within the documented constraints

Do not keep generating code simply because the prompt said "continue."

---

# 53. FINAL SYSTEM ACCEPTANCE

The project is considered functionally complete only when this end-to-end story works:

```text
Physical department QR
→ registration
→ anti-abuse / verification policy
→ patient identity
→ visit
→ unique department token
→ private status page
→ staff login
→ queue management
→ priority handling
→ missed patient handling
→ transfer
→ completion
→ public display update
→ patient status update
→ ESP32 occupancy event
→ occupancy dashboard
→ analytics
→ audit trail
```

And the system passes the important failure/security tests.

---

# 54. FINAL REPORT FORMAT

After a major milestone, provide:

```text
MILESTONE:
STATUS:

Implemented:
- ...

Files changed:
- ...

Tests:
- ...

Important design decisions:
- ...

Known limitations:
- ...

Documentation updated:
- ...

Next recommended milestone:
- ...
```

Keep reports factual.

Never claim tests, deployment, or integrations that were not actually performed.

---

# 55. FIRST TASK PROMPT FOR JULES

Use the following as the first Jules task after this file and the other project documents are in the repository:

---

You are taking ownership of the Smart Queue & Crowd Management System repository.

Before writing any code:

1. Inspect the complete repository tree.
2. Read:
   - `docs/JULES_MASTER_CONTEXT.md`
   - `docs/01_TECHNICAL_PRD.md`
   - `docs/02_API_CONTRACT.md`
   - `docs/03_DATABASE_SCHEMA.md`
   - `docs/04_FRONTEND_BUILD_MAP.md`
   - `docs/05_BUILD_ORDER_CHECKLIST.md`
   - `docs/06_SECURITY_PRIVACY_NFR.md`
   - `docs/07_AI_HUMAN_IN_LOOP_PLAYBOOK.md`
   - `README.md`
   - `AGENTS.md` if present.
3. Check whether any implementation code already exists.
4. Do not assume missing information.
5. Do not start feature implementation yet.

First produce:

### A. Project understanding
Explain:
- product purpose
- users
- complete system flow
- backend architecture
- frontend architecture
- hardware architecture
- security boundaries
- database entities
- queue state machine
- deployment model

### B. Repository assessment
Report:
- current file tree
- what is complete
- what is missing
- inconsistencies or conflicts among documents
- risks you see

### C. Architecture verification
Check whether the current specification is internally consistent.

Pay particular attention to:
- public QR vs authentication
- patient vs visit vs token
- status-access identifier
- duplicate active visits
- token numbering
- queue state transitions
- priority policy
- transfer
- staff authentication
- device authentication
- occupancy idempotency
- API/database consistency
- deployment/database choice

### D. Blocking questions
Ask only questions that cannot be answered from the repository documents and that would materially block implementation.

Do not ask unnecessary questions.

### E. Stage-0 implementation plan
After the above, propose the exact first implementation stage:

```text
repository/setup
→ environment
→ backend skeleton
→ database/migrations
→ seed data
→ health endpoint
```

Do not implement Stage 1 yet.

Wait for my response and plan approval before modifying application code.

---

# 56. IMPORTANT HUMAN RULE

The human may allow you to write the code.

The human does NOT delegate:
- final requirements
- security acceptance
- architecture changes
- production claims
- medical policy
- destructive data decisions

When uncertain, make uncertainty visible.

