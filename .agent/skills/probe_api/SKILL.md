---
name: Probe API
description: Systematically probe an unfamiliar external API (REST/WebSocket/GraphQL) to discover its real behavior, capture sample data, and produce verified documentation.
category: api
status: active
safety: writes-local
---

# Probe API

A skill for systematically probing unfamiliar external APIs. Instead of trusting documentation alone, this skill captures **actual payloads** from the live API, compares them to docs, and produces verified documentation for the project.

## When To Use

- Integrating a new external API (REST, WebSocket, GraphQL)
- Existing documentation looks outdated or incomplete
- You see unexpected responses (missing fields, different structure)
- Building a client library / consumer and need exact field names / types

## Instructions

### Phase 1: Environment Setup

**Goal**: Get a working connection to the API from the correct environment.

1. **Identify the API endpoints** from official docs, existing project code, or user input.
2. **Determine where to run tests** — follow the debugging methodology rule:
   - If the consumer runs in Docker → test from inside Docker first
   - If on host → test from host
   - **Always test from the actual runtime environment**
3. **Check network accessibility** — use layered diagnostics:
   ```
   DNS → Ping → TCP → TLS → HTTP → Application Protocol
   ```
   Use a **control target** (e.g., `google.com`) alongside the actual API to isolate network vs. API issues.
4. **Install minimal tools**:
   - Python: `pip install websockets requests` (for WS/REST)
   - Or use `curl` / `openssl s_client` for raw testing
5. **Find a representative test entity** when the API requires one:
   - Query a discovery/listing endpoint first.
   - Pick an entity that is active, public, and safe to inspect.
   - Record the entity ID for all subsequent tests.

### Phase 2: Capture Raw Payloads

**Goal**: Get the actual JSON the server sends, with zero assumptions.

#### For REST APIs:
```bash
curl -s "https://api.example.com/endpoint?param=VALUE" | python3 -m json.tool
```

#### For WebSocket APIs:
Write a minimal dump script — subscribe and print raw messages:
```python
import asyncio, json, websockets

async def dump():
    async with websockets.connect("wss://api.example.com/ws") as ws:
        await ws.send(json.dumps({"type": "subscribe", ...}))
        for i in range(10):
            msg = await asyncio.wait_for(ws.recv(), timeout=10)
            if msg in ("PONG", "[]"): continue  # skip heartbeats
            print(json.dumps(json.loads(msg), indent=2))

asyncio.run(dump())
```

**Key rules**:
- Print the **full raw payload** first — don't parse or filter yet
- Capture at least **3-5 different event types** to see all message shapes
- Note the **discriminator field** (e.g., `type`, `event_type`, `kind`)
- Record the **actual field names** — they often differ from docs (e.g., `price_changes` vs `changes`)

### Phase 3: Analyze & Compare

**Goal**: Compare actual payloads against documentation, noting discrepancies.

For each event type discovered:

1. **List all fields** present in the actual payload
2. **Compare to docs**: mark fields as:
   - ✅ Matches docs
   - ⚠️ Different from docs (wrong name, different type, different nesting)
   - 🆕 Not in docs (undocumented field)
   - ❌ In docs but missing from actual payload
3. **Identify patterns**:
   - What is the array vs object wrapping? (single object, array of objects, nested)
   - What are the heartbeat/keepalive messages?
   - What is the subscription acknowledgment format?
   - How are errors reported?

### Phase 4: Build Recorder Script

**Goal**: Create a reusable script that records events for extended observation.

The recorder should:
- Accept the target entity ID as argument
- Support configurable duration (`--duration 60`)
- Write events to JSONL file (one JSON per line)
- Log events in real-time with counters and timestamps
- Print a summary at the end (event counts, duration, key stats)
- Handle heartbeat/keepalive
- Display progress (per `.agent/rules/70-style-code.md`)

**JSONL record format**:
```json
{"ts": "2026-01-01T00:00:00Z", "elapsed_s": 1.234, "type": "event_name", ...event_fields}
```

Save the recorder script to `<project>/scripts/` for future use.

### Phase 5: Write Documentation

**Goal**: Produce a verified protocol document for the project.

The document should include:

1. **Overview** — what the API does, its architecture
2. **Endpoints** — exact URLs (verified, not from potentially stale docs)
3. **Authentication** — if any (API keys, headers, cookies)
4. **Subscription/Request format** — exact JSON payloads that work
5. **Event Payloads** — for each event type:
   - Event name and discriminator value
   - Full JSON example (from actual capture)
   - Field descriptions with types
   - Important notes (sorting, missing fields, gotchas)
6. **Keepalive / Heartbeat** — what to send, what to filter
7. **Rate Limits** — observed or documented
8. **Data Consistency Notes** — sorting order, normalization requirements

**Format rules**:
- Mark all payloads with verification date: `(Verified YYYY-MM-DD)`
- Use `> **Note**:` blocks for gotchas and discrepancies from official docs
- Include both the official doc URL and your verified findings

Save to `document/` directory in the project.

## Report Format

After completing the probe, produce a brief report:

```
## API Probe Report: [API Name]

### Endpoints Tested
- [endpoint 1]: ✅ Working / ❌ Blocked (reason)

### Event Types Discovered
- [event_type_1]: [field_count] fields, [frequency] (e.g., "~5/sec")
- [event_type_2]: ...

### Doc Discrepancies
- [discrepancy 1]
- [discrepancy 2]

### Artifacts Produced
- Recorder script: [path]
- Protocol document: [path]
- Sample data: [path to JSONL]
```
