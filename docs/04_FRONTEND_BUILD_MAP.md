# Smart Queue & Crowd Management System
## Frontend Build Map

**Purpose:** This file is the exact frontend work map for the second developer and her AI-assisted workflow.

**Frontend stack:**
- HTML
- CSS
- JavaScript
- no framework required for first implementation

The frontend developer can start against mock JSON immediately. She must follow `02_API_CONTRACT.md` exactly and must not invent endpoint names or field names.

---

## 1. Frontend Architecture

```text
frontend/
├── patient/
│   ├── register.html
│   ├── register.js
│   ├── status.html
│   └── status.js
│
├── staff/
│   ├── login.html
│   ├── dashboard.html
│   ├── login.js
│   └── dashboard.js
│
├── display/
│   ├── display.html
│   └── display.js
│
├── admin/
│   ├── settings.html
│   └── settings.js
│
└── shared/
    ├── api.js
    ├── auth.js
    ├── ui.js
    └── styles.css
```

---

## 2. Global Frontend Rules

- Backend owns business logic.
- Frontend never generates authoritative tokens.
- Do not hard-code departments, rooms, queue counts, or token numbers.
- Use mock JSON first.
- Replace mocks with the exact API later.
- Every async operation needs loading, success, and error states.
- Polling should be configurable.
- Do not expose private patient data on the public display.
- Do not put secrets in JavaScript.
- Do not place staff API credentials in page source.
- Keep browser console free of avoidable errors.

---

## 3. Patient Registration Page

### URL concept

```text
/register/<registration-location-id>
```

### UI

```text
Smart Queue

Name
Date of birth / age
Mobile
Patient type
Department

Anti-bot verification
[ Join Queue ]
```

### Behavior

1. Load registration location.
2. Resolve allowed/default department.
3. Validate fields.
4. Run anti-bot challenge when enabled.
5. Run verification flow according to backend policy.
6. POST `/api/register`.
7. Show success token and room.
8. Store/use returned private status URL.

### States

- loading
- ready
- verification pending
- registration success
- active-visit exists
- validation error
- rate-limited
- service unavailable

### Success screen

```text
YOUR TOKEN
G125

General Medicine
Room 2

[ View Queue Status ]
```

---

## 4. Patient Status Page

### URL concept

```text
/status/<random-status-id>
```

### Show

```text
Your Token: G125
Now Serving: G118
Patients Ahead: 6
Estimated Wait: ~30 min
Department: General Medicine
Room: 2
Status: WAITING
```

### Polling

Suggested initial interval:
- 4 seconds

Make it configurable.

### Error behavior

If the request fails:
- show connection/degraded state
- do not invent a new estimate
- do not silently display stale values as current

---

## 5. Staff Login

### Fields

```text
Username
Password

[ Sign In ]
```

### States

- loading
- wrong credentials
- locked/rate-limited
- server unavailable
- successful login

The frontend only controls presentation. Authentication/authorization is backend-enforced.

---

## 6. Staff Dashboard

### Main sections

```text
Header
Department cards
Queue list
Current serving token
Queue controls
Occupancy
Operational summary
```

### Department card

```text
General Medicine
Waiting: 18
Current: G118
Room: 2

[Call Next]
```

### Token controls

```text
Hold
Recall
Skip
Complete
Transfer
Priority
```

Only show controls allowed for the authenticated role, but backend authorization remains authoritative.

### Polling

Suggested initial interval:
- 3–4 seconds

After every action:
- send POST request
- re-fetch authoritative queue
- redraw affected UI

---

## 7. Public Display

### UI goal

Readable across a room.

Example:

```text
GENERAL MEDICINE

NOW SERVING

G118

ROOM 2

NEXT: G119
```

For multiple departments, use clearly separated cards/rows.

### Rules

- read only
- no patient identity
- no phone
- no private information
- refresh frequently
- show service-unavailable indicator if backend is unreachable

---

## 8. Occupancy Widget

Staff dashboard:

```text
WAITING AREA A

24 / 30

HIGH
```

States:

```text
NORMAL
MODERATE
HIGH
CRITICAL
```

Use backend-provided status.

Do not reimplement crowd policy independently in the frontend.

---

## 9. Analytics Page / Section

Show:

```text
Total Patients
Completed
Average Waiting Time
Average Consultation Time
Peak Occupancy
Peak Time
Longest Queue
Department-wise Waiting
```

Charts may be added later with Chart.js.

---

## 10. Admin UI

First useful admin screens:

### Staff
- list
- activate/deactivate
- role assignment

### Departments
- name
- code
- active

### Rooms
- department
- room number
- active

### Registration Locations
- location name
- department
- active
- QR generation/download

### Zones
- name
- capacity
- department
- active

### Devices
- device ID
- assigned zone
- active
- last seen

Do not expose device secrets in normal UI.

---

## 11. Mock API Strategy

Create one shared `api.js` layer.

Example:

```javascript
const USE_MOCKS = true;
```

When mocks are enabled:

```textUI → mock service → JSON
```

When integration begins:

```textUI → api.js → FastAPI
```

The page components should not care whether the source is mock or real.

---

## 12. Mock Data Shape

### Registration

```json
{
  "departments": [
    {
      "id": "dep-general",
      "name": "General Medicine",
      "code": "G",
      "room": "2"
    }
  ]
}
```

### Registration success

```json
{
  "visit_id": "visit-demo-001",
  "token_id": "token-demo-001",
  "status_access_id": "status-demo-random-id",
  "display_token": "G125",
  "department": "General Medicine",
  "room": "2",
  "status": "WAITING",
  "status_url": "/status/status-demo-random-id"
}
```

### Patient status

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

### Staff queue

```json
{
  "departments": [
    {
      "department_id": "dep-general",
      "name": "General Medicine",
      "waiting_count": 18,
      "current_token": "G118",
      "room": "2"
    }
  ]
}
```

### Public display

```json
{
  "department": "General Medicine",
  "current_token": "G118",
  "next_token": "G119",
  "room": "2"
}
```

### Occupancy

```json
{
  "zone_id": "zone-a",
  "current_count": 24,
  "capacity": 30,
  "level": "HIGH",
  "estimated": true
}
```

---

## 13. Required Frontend Build Order

### F1
Shared layout + styles + API abstraction

### F2
Registration page with mocks

### F3
Token success/result state

### F4
Patient status page with polling mock

### F5
Staff login UI

### F6
Staff dashboard skeleton

### F7
Queue action controls

### F8
Public display

### F9
Occupancy widget

### F10
Analytics section

### F11
Admin screens

### F12
Replace mocks with real endpoints

### F13
Integration bugs + mobile/desktop polish

---

## 14. Exact AI Prompt for Frontend Developer

Use this with the chosen coding agent:

```text
You are the frontend engineer for the Smart Queue & Crowd Management System.

Read:
- 01_TECHNICAL_PRD.md
- 02_API_CONTRACT.md
- 04_FRONTEND_BUILD_MAP.md

Your scope is frontend only.

Stack:
HTML
CSS
JavaScript

Rules:
- Do not change backend files.
- Do not invent API endpoints.
- Do not rename API fields.
- Do not generate tokens in the frontend.
- Do not hard-code queue data.
- Use mock JSON until real endpoints are available.
- Build the interface mobile-first for patients and desktop-friendly for staff.
- Include loading, success, empty, validation, error, and degraded states.
- Never show private patient information on the public display.
- Do not put secrets in frontend code.

Current task:
[INSERT ONE F1-F13 TASK HERE]

When complete:
1. explain what was built
2. list files changed
3. list API endpoints consumed
4. list mock data used
5. report assumptions
6. report known limitations
7. run a basic browser/UI test
8. return a concise change summary
```

---

## 15. Frontend Handoff Format

When a frontend task is finished, provide:

```text
Task:
Files changed:
Pages completed:
API endpoints consumed:
Mock/real mode:
Screenshots:
Known issues:
Commit:
```

This keeps the two developers synchronized without a heavy ticket bureaucracy.
