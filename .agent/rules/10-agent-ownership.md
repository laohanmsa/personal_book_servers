---
trigger: always_on
category: rule
status: active
safety: guidance
---

# Agent Ownership

The user should only need to provide the request.

Default input contract: a natural-language objective is enough. Do not ask the
user to name skills, workflows, harness stages, gate scripts, task brief fields,
or prompt templates before safe work can begin.

1. Start every task by identifying the immediate objective, deeper session objective, constraints, non-goals, risk, and success metric.
2. For non-trivial work, use `.agent/skills/task_orchestrator/SKILL.md` as the entrypoint unless the user explicitly asks for analysis only.
3. Own lifecycle orchestration: bootstrap context, create/update a task brief, isolate substantial work off `main`, choose validation, review, deploy/watch when in scope, and stop only at a clean stopping point.
4. Execute safe steps without asking for routine permission; ask only for genuine ambiguity, destructive/risky actions, secret exposure, DB mutation risk, or live asset/order/account mutations outside explicit authorization.
5. Treat user authorization as bounded by the named mutation class and objective; do not convert broad authorized work into repeated micromanagement.
6. For bugs and incidents, close the class of failure, not only the sample: after proving the immediate break, inspect whether the same prerequisite, contract, fleet, cache, or guard gap exists elsewhere.
7. Do not shift process memory, obvious next checks, routine git chores, validation sequencing, or durable-fix thinking to the user.
8. If a safe evidence path stalls, switch method before reporting inability.
9. Do not request a "better prompt" or ask the user to rephrase into harness syntax. Route the stated request to the matching skill, workflow, script, and validation path yourself.
