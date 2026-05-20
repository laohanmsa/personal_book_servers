# Optimizer Metric Patterns

Use this reference when the user's goal is too vague to benchmark directly.

## Metric Contract Template

Every metric needs:

- Name: stable column name for the result table.
- Direction: higher is better, lower is better, or target range.
- Unit: count, percent, ms, MB, dollars, rows, queries, etc.
- Source: command output, test assertion, fixture label, log line, profiler, DB query, API response, or report file.
- Threshold: minimum change that counts as real.
- Guard status: primary, guard, or secondary.

## Discovery And Set-Finding Algorithms

Use these for search, matching, market discovery, clustering, dedupe, entity resolution, and "find all valid items" tasks.

| User Term | Concrete Measurement |
| --- | --- |
| discovered amount | unique valid items found on a fixed corpus |
| quality | precision = valid discovered / all discovered |
| coverage | recall = valid discovered / oracle valid items |
| fewer missed sets | false negatives = oracle valid items not discovered |
| less noise | false positives = discovered invalid items |
| dedupe quality | duplicate groups, duplicate rate, or canonicalization accuracy |
| speed | median and p95 runtime over repeated runs |
| stability | result overlap across repeated runs or seeds |

When the oracle is incomplete, report both "known recall" against the labeled corpus and "candidate yield" on unlabeled data. Do not call candidate yield true recall.

## Ranking And Scoring Algorithms

Use these for recommendations, search result ranking, prioritization, classifiers, and trade signal scoring.

- `precision@k`: valid or accepted results in top K.
- `recall@k`: oracle positives captured in top K.
- `ndcg@k`: ranking quality when labels have graded relevance.
- `map`: mean average precision for multiple queries.
- `auc`: ranking separation for binary labels.
- `brier_score` or `log_loss`: probability calibration.
- `top_k_hit_rate`: whether at least one desired result appears in top K.

Always keep a confusion matrix or raw bucket table when optimizing a classifier-like threshold.

## Runtime And Resource Metrics

Use repeated runs and stable input sizes.

- latency: median, p95, p99
- throughput: items/sec or requests/sec
- query count: total SQL queries and slow-query count
- memory: peak RSS or allocation count
- CPU: wall time plus CPU time when available
- external calls: count, retries, rate-limit hits, error count
- cache behavior: hit rate, miss rate, warm vs cold timing

Warm-cache and cold-cache runs are different metrics. Record both when cache state affects behavior.

## Correctness Guards

Guard metrics should usually block acceptance rather than become weighted score components.

- existing unit/integration tests pass
- golden fixtures match exactly
- invariants hold on synthetic inputs
- no duplicate IDs or missing required fields
- public API shape unchanged
- output order deterministic when required
- safety constraints respected
- no new live external writes

## No-Oracle Strategies

If full truth is unavailable:

1. Golden set: small manually verified corpus.
2. Synthetic generator: seeded cases where truth is known.
3. Metamorphic tests: transformations that must preserve or predictably change output.
4. Shadow compare: compare old and new outputs and review differences.
5. Invariant checks: validate constraints every output must satisfy.
6. Sample audit: manually inspect a stratified sample of new/changed results.

State which parts are proved and which remain proxy evidence.

## Composite Scores

Prefer lexicographic ranking over weighted sums:

1. Guards pass.
2. Primary metric improves beyond threshold.
3. Secondary regressions are inside allowed limits.
4. Simpler implementation wins ties.

Use weighted sums only when the user or domain already owns the weights.
