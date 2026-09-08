# Smart Queue & Crowd Management System
## AI-Assisted Development + Human-in-the-Loop Learning Plan

## 1. Objective

AI may write most or even all of the application code.

The human must still own:

```text
requirements
architecture
decisions
verification
testing
debugging
review
```

The goal is not "code without coding".

The goal is:

```text
AI accelerates implementation
+
human develops engineering judgment
```

---

## 2. Tool roles

Use one primary coding agent at a time for a feature.

### Primary coding agent
Choose either:
- Codex
- Gemini/Antigravity

based on which environment is currently more effective.

### In-editor assistant
Use GitHub Copilot for:
- autocomplete
- tiny refactors
- tests
- explaining lines/functions
- repetitive code

### Secondary reviewer
Use another model only when needed for:
- code review
- debugging
- architecture challenge
- security review

### Jules
Use only for clearly isolated GitHub tasks when asynchronous work provides real value.

Do not create a four-agent pipeline for every feature.

---

## 3. Human-in-the-loop development cycle

Every feature follows:

```text
REQUIREMENT
   ↓
HUMAN writes/understands acceptance criteria
   ↓
AI proposes plan
   ↓
HUMAN reviews plan
   ↓
AI implements
   ↓
HUMAN reads the diff
   ↓
HUMAN predicts expected behavior
   ↓
TEST
   ↓
AI fixes defects
   ↓
HUMAN verifies again
   ↓
MERGE
```

Never merge code that the human owner cannot explain at a useful level.

---

## 4. Learning gate before accepting AI code

For each non-trivial feature, answer these before accepting it:

### Gate A — What problem does it solve?

One or two sentences, in your own words.

### Gate B — What are the inputs and outputs?

Example:

```text
POST /api/register
input → patient data + location
output → visit + token + private status URL
```

### Gate C — What can go wrong?

Write at least three failure cases.

### Gate D — Why is the implementation correct?

Explain the important control flow.

### Gate E — How did we test it?

Give a concrete test command/request and expected result.

If you cannot answer one of these, ask the AI to teach/explain before continuing.

---

## 5. Critical logic should be understood, not blindly generated

AI can write the syntax.

The human must understand these particularly well:

```text
token generation
queue state machine
duplicate visit logic
priority ordering
transaction/concurrency behavior
authentication
authorization
session handling
private status access
occupancy direction logic
device authentication
analytics calculations
```

These are the parts most worth learning from.

---

## 6. Do not learn by retyping everything

You do not need to manually type every line.

Instead, learn by forcing yourself to:

```text
predict
inspect
run
break
debug
explain
```

Example:

Before asking AI to implement `call_next`, first write in plain English:

```text
Find eligible waiting tokens
→ apply priority policy
→ choose oldest eligible token
→ atomically change it to SERVING
→ record event
→ return updated token
```

Then let AI implement it.

Now the AI is converting your engineering plan into code rather than replacing the plan.

---

## 7. Debugging rule

When something breaks, do not immediately say:

```text
AI, fix this.
```

First:

```text
1. reproduce
2. read traceback/error
3. identify likely layer
4. inspect relevant code
5. state your hypothesis
6. ask AI to challenge/examine it
7. apply fix
8. rerun test
```

This is where a large fraction of actual programming skill is built.

---

## 8. AI prompt pattern

Use:

```text
Context:
Read the relevant project specification files first.

Task:
Implement only [small task].

Constraints:
- preserve API contract
- preserve database schema
- do not modify unrelated modules
- add tests
- explain important design decisions

Before coding:
Give a short implementation plan and identify risks.

After coding:
- summarize changes
- show tests run
- show known limitations
- identify files changed
```

This makes the agent act like an implementation partner rather than an uncontrolled code generator.

---

## 9. Feature size

Prefer:

```text
one issue
one feature
small diff
```

Examples:

Good:
```text
Implement POST /api/register
```

Bad:
```text
Build the entire backend.
```

Good:
```text
Implement queue transition WAITING → SERVING.
```

Bad:
```text
Fix the queue.
```

---

## 10. Three levels of human involvement

### Level 1 — Critical logic
Human reads deeply.

Examples:
- queue engine
- authentication
- database constraints
- concurrency
- security

### Level 2 — Normal application logic
Human reviews plan + diff + tests.

### Level 3 — Repetitive UI/boilerplate
AI may work more independently, but the human still checks behavior.

---

## 11. Daily skill-building loop

Each build session:

```text
15 min  understand today's task
10 min  write acceptance criteria
AI      implementation
20 min  read/explain important code
20 min  test/break it
15 min  fix/debug
10 min  write what you learned
```

The exact minutes are flexible. The sequence is what matters.

---

## 12. Build a personal engineering notebook

For every difficult feature, record:

```text
Problem
My initial approach
AI approach
Why the final approach works
Bug encountered
How I diagnosed it
Important concept learned
```

This becomes your real learning record.

---

## 13. Human ownership rule

The AI may produce:

```text
1000 lines of code
```

but the human remains responsible for:

```text
10 architecture decisions
20 important invariants
30 test cases
```

Do not measure progress by lines of code.

Measure:

```text
features understood
bugs diagnosed independently
tests written
architecture decisions defended
```

---

## 14. Suggested skill progression through this project

### Stage 1
Learn:
- Git
- Python/FastAPI basics
- HTTP
- JSON
- database basics

### Stage 2
Learn:
- CRUD
- validation
- SQL
- transactions
- REST API design

### Stage 3
Learn:
- state machines
- concurrency
- authentication
- sessions
- authorization

### Stage 4
Learn:
- browser APIs
- fetch
- async JavaScript
- polling
- responsive UI

### Stage 5
Learn:
- embedded events
- sensor debouncing
- Wi-Fi
- HTTP from ESP32

### Stage 6
Learn:
- deployment
- environment variables
- PostgreSQL
- HTTPS
- logs
- monitoring

The project itself becomes the curriculum.

---

## 15. Red flags that mean AI is replacing your learning

Stop and learn the concept if you repeatedly say:

```text
"What does this function do?"
"Why does this database query work?"
"Why is this transaction needed?"
"Why can't we use the token as the ID?"
"Why did this request need CSRF protection?"
"Why did two registrations get the same number?"
```

Do not simply ask the AI to make the confusion disappear.

Make it explain until you can explain it yourself.

---

## 16. Weekly checkpoint

At the end of each week, you should be able to verbally explain:

```text
Week 1:
How registration and token generation work.

Week 2:
How the queue state machine and authentication work.

Week 3:
How hardware events become occupancy data and how the whole system is deployed.
```

The goal is to finish with a working system **and** enough understanding to defend it line by line.
