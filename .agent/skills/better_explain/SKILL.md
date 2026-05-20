---
name: Better Explain
description: Explain algorithms, data structures, pipelines, and system behavior with accurate, easy-to-scan markdown-first visuals. Use Mermaid by default, choose the right diagram type for the question, generate SVG or PNG when the renderer cannot show Mermaid directly, and pair every graph with a concise walkthrough, invariants, and caveats. Trigger on requests like explain, show me, how does this work, visualize this, or draw the flow.
category: docs
status: active
safety: writes-local
---

# Better Explain

Use this skill when the user wants understanding, not just a raw answer.

Typical triggers:

- `explain`
- `show me`
- `how does this work`
- `walk me through`
- `visualize this`
- `draw the flow`

The goal is not to add diagrams everywhere. The goal is to produce the clearest accurate explanation for the user's exact question. Use a graph only when it removes ambiguity faster than prose alone.

## Core Contract

1. Start from a source of truth:
   - code
   - schema
   - API contract
   - logs
   - a user-provided text snippet
2. State what the user is trying to understand in one line.
3. Choose the smallest diagram that answers that question.
4. Keep the diagram fact-aligned with the source material.
5. Pair the diagram with a short walkthrough, not a diagram dump.
6. Call out assumptions, omitted branches, or uncertainty explicitly.

## Diagram Choice

Use Mermaid by default when the explanation is going into markdown and the renderer supports Mermaid.

- Flowchart:
  - best for algorithms, branch logic, processing stages, and pipelines
- Sequence diagram:
  - best for request lifecycles, RPC chains, async queues, and actor ordering
- State diagram:
  - best for lifecycle transitions and finite-state behavior
- Class diagram or ER diagram:
  - best for data models, ownership, and cardinality

Use a static asset instead of inline Mermaid only when needed:

- Mermaid CLI:
  - best fallback when the markdown target cannot render Mermaid directly
- D2:
  - use when richer static styling, markdown inside nodes, or a different layout engine is the main need
- Graphviz:
  - use when a real tree or graph layout must be precise

Read `references/diagram_patterns.md` when you need the selection matrix, render commands, or markdown embedding patterns.

## Output Shape

For chat answers:

1. one-sentence model of the idea
2. the diagram
3. a step-by-step walkthrough tied to the diagram
4. invariants, edge cases, or omitted details

For durable docs:

1. save a dated markdown file under `docs/`
2. include a timestamp
3. include the diagram source directly in the markdown when Mermaid is supported
4. if static rendering is required, embed an SVG with normal markdown image syntax
5. run `bash .agent/skills/secretary/secretary.sh scan --incremental` after the doc lands

Read `references/report_template.md` when you need a reusable document skeleton.

## Accuracy Rules

1. Use the same object names as the source material unless the user explicitly asks for friendlier aliases.
2. Label important decision branches and transitions.
3. Do not hide failure paths when they matter to the question.
4. If the diagram is simplified, say what was omitted.
5. Prefer two small diagrams over one overloaded diagram.
6. Validate syntax before trusting the final render.

## Local Environment Note

This environment has `npm` and `node` available, so the default render path for static Mermaid output can be:

```bash
npx -y -p @mermaid-js/mermaid-cli mmdc -i diagram.mmd -o diagram.svg
```

Do not assume `d2`, `dot`, or a globally installed `mmdc` exist unless you verify them in the current session.
