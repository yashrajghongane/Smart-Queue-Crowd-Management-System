# JULES TASK CONTINUATION PROMPT

Use this prompt for subsequent milestone/task runs.

Read `docs/JULES_MASTER_CONTEXT.md` first.

Current task:

[DESCRIBE ONE MILESTONE OR FEATURE]

Requirements:
- use the repository source-of-truth documents
- inspect existing code before changing it
- preserve API and database contracts
- do not modify unrelated modules
- write tests for important logic
- run the relevant tests
- inspect the final diff
- keep code readable
- update documentation when behavior changes

Before coding:
1. summarize the relevant requirement
2. state assumptions
3. identify dependencies
4. propose a short implementation plan
5. identify risks

After coding:
1. run tests
2. run relevant lint/type/smoke checks
3. inspect changed files
4. check API/schema compatibility
5. check security/privacy implications
6. summarize exactly what changed
7. report tests and results
8. report known limitations
9. recommend the next dependency-safe task

Stop and ask the human when:
- requirements conflict
- a security-sensitive decision is ambiguous
- credentials/external service setup is required
- a migration could destroy data
- the documented architecture would need to change
