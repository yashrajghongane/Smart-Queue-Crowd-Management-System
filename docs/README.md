# Jules Documentation

Files:

- `JULES_MASTER_CONTEXT.md` — complete project context + operating rules
- `JULES_FIRST_BOOT_PROMPT.md` — first prompt to start the project
- `JULES_TASK_TEMPLATE.md` — reusable prompt for later milestone tasks

Recommended use:

1. Commit the project specification files.
2. Commit `JULES_MASTER_CONTEXT.md`, `JULES_FIRST_BOOT_PROMPT.md`, and `JULES_TASK_TEMPLATE.md`.
3. In Jules, connect the GitHub repository.
4. Start with `JULES_FIRST_BOOT_PROMPT.md`.
5. Review Jules' generated plan before approving it.
6. Answer only genuine blocking questions.
7. Keep implementation in bounded milestones.
8. Review diffs and tests before merging.

The Jules agent can work autonomously after a task is started and its plan is approved. Use scheduled tasks for bounded recurring maintenance, not as an uncontrolled feature-generation loop.
