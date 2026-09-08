# Smart Queue & Crowd Management System
## Security, Privacy & Non-Functional Requirements

This document closes the gaps that were found during re-verification of the first specification pack.

## 1. Security is layered

The public QR is intentionally public.

Security controls are layered:

```text
Public QR
→ registration-location validation
→ anti-bot challenge
→ rate limiting
→ phone/identity verification policy
→ duplicate active-visit rule
→ secure private status access
```

No single layer is trusted as the whole security mechanism.

Cloudflare Turnstile is a suitable optional anti-automation layer; its current free plan is intended for most production applications and provides unlimited challenges, subject to plan limits such as widget/hostname limits. It must still be verified server-side. [web source: Cloudflare Turnstile]

## 2. Staff sessions

Use server-side sessions with:

```text
Secure
HttpOnly
SameSite=Strict or Lax
```

Do not store staff session IDs/JWTs in localStorage.

Because cookie-based authenticated browser requests can be exposed to CSRF, implement CSRF protection for state-changing staff requests.

CORS must be an explicit allow-list of known frontend origins, not `*` when credentials are used.

## 3. HTTPS

Hosted deployment must use HTTPS.

The frontend, staff dashboard, patient status, and device-to-backend communication must not use plain HTTP in deployment.

## 4. Input validation

Validate on the server:

- required fields
- string length
- dates
- mobile format
- enum values
- identifiers
- JSON body shape
- request size

Frontend validation improves UX but never replaces server validation.

## 5. Authentication boundaries

Do not use the same mechanism for:

```text
public patient access
staff authentication
device authentication
```

Staff and device credentials must never appear in public HTML/JavaScript.

## 6. Patient status security

Use an unpredictable status-access identifier.

A patient status URL must not expose:
- internal sequential database IDs
- staff information
- unnecessary patient data

An optional OTP re-verification layer may be enabled for sensitive actions.

A status page should not expose personal medical information on the public display.

## 7. Duplicate and abuse protection

The registration service must make duplicate prevention atomic:

```text
lookup active visit
+
create visit/token
```

must occur inside a safe transaction/constraint strategy.

Rate limiting should cover at least:
- registration attempts
- OTP requests
- login attempts
- device event abuse

Exact limits are deployment configuration.

## 8. Idempotency

ESP32 events need an `event_id`.

If an ESP32 retries the same event because of a network failure, the backend must process it once.

Important staff actions should also resist accidental duplicate execution caused by double clicks/retries.

## 9. Queue concurrency

The backend must enforce queue invariants under concurrent staff actions.

Examples:
- only one active `SERVING` token per queue/resource unless explicitly configured otherwise
- a `COMPLETED` token cannot be completed again
- two staff users cannot successfully advance the same queue twice from one queue state
- transfer cannot duplicate a token

Use database transactions/locking appropriate to the chosen database.

## 10. Token numbering policy

Token numbering must be explicitly configured.

Required configuration:

```text
department code
sequence scope
daily reset or continuous sequence
starting number
```

Recommended first policy:

```text
one sequence per department per operating day
```

Example:

```text
G101, G102, G103...
```

The policy must be documented and tested before deployment.

## 11. Queue fairness

Priority must not accidentally create permanent starvation.

Define:
- ordering of priority classes
- behavior of held/recalled tokens
- emergency handling
- whether old waiting tokens gain priority over newer normal tokens

Default policy for the first implementation:

```text
authorized emergency/urgent handling
→ priority
→ normal
```

with FIFO ordering inside a priority class.

The currently serving patient is not automatically interrupted by the queue engine.

## 12. Audit integrity

Audit records should be append-oriented.

Do not let normal staff actions rewrite historical audit entries.

An audit event should include:
- actor
- actor role/device
- timestamp
- action
- affected entity
- relevant before/after information where appropriate

## 13. Secrets

Never commit:
- database passwords
- session secrets
- OTP provider credentials
- notification provider keys
- device secrets
- deployment secrets

Use environment variables or the hosting platform's secret store.

## 14. CORS

If frontend and API are deployed on different origins, allow only known origins.

Do not use wildcard CORS with credentialed requests.

## 15. Observability

Backend should provide:
- structured application logs
- request/error logs
- health endpoint
- readiness/dependency check
- device last-seen information

Do not put patient names/mobile numbers into ordinary logs.

## 16. Backup and recovery

For the hosted database, establish at least a basic backup/export strategy before calling it a deployable system.

A free hosted database with no backups must be treated as a demonstration environment, not durable production storage.

## 17. Privacy principle

Collect only the fields needed for the queue workflow.

Public display must expose only:

```text
department
current token
next token
room
```

Never expose names, phone numbers, or medical information.

## 18. Indian privacy/legal boundary

The project should not claim legal/compliance certification.

If real patient data is ever used, the team must obtain appropriate institutional authorization and review applicable Indian privacy/data-protection requirements before deployment.

For the semester implementation, use synthetic/test data unless explicitly authorized.

## 19. Security test checklist

Before deployment test:

```text
[ ] unauthenticated staff API rejected
[ ] wrong role rejected
[ ] duplicate active visit prevented
[ ] rate limiting works
[ ] invalid anti-bot token rejected
[ ] invalid device credential rejected
[ ] repeated device event does not double count
[ ] private status ID is non-sequential
[ ] public display has no PII
[ ] secrets absent from repository
[ ] HTTPS used in hosted deployment
[ ] CORS restricted
[ ] CSRF protection tested
[ ] password hashes only
[ ] queue concurrency tested
```
