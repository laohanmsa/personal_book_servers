---
name: Dig Deep
description: Intensive deep-dive research on a topic. Gathers raw materials (social media, expert opinions, academic papers, open-source tools), composes concrete research objectives, and systematically completes each objective with detailed findings.
category: research
status: active
safety: writes-local
---

# Dig Deep Research

A skill for conducting intensive, structured research on any topic. Instead of surface-level searches, this skill gathers **raw source materials**, formulates **concrete research objectives**, and systematically works through each objective to produce actionable findings.

## When To Use

- Starting research on a new strategy, technology, or approach
- Need to understand the competitive landscape for a feature/product
- Evaluating feasibility of a new system or integration
- Want a comprehensive, evidence-based analysis before building

## Inputs

- **`{topic}`**: The research topic (e.g., "local-first reading workflow")
- **`{project}`**: The project this research belongs to (e.g., "personal_reader")
- The current conversation title will be used as `{session_name}` for context

## Instructions

### Phase 0: Setup

**Goal**: Create the research directory structure.

1. **Identify the session name** from the conversation context.
2. **Create research directory**: `research/{project}/{topic}/`
   - Use snake_case for `{topic}` directory name (e.g., `multi_outcome_bundle_arb`)
3. **Create `raw_material/` subdirectory** under the research dir.
4. **Log the session**: Record `{session_name}`, `{topic}`, date, and initial context in a `README.md` at the research root.

```
research/
  {project}/
    {topic}/
      README.md          ← session name, date, context
      raw_material/      ← downloaded source materials
      objectives.md      ← research objectives (Phase 2)
```

### Phase 1: Initial Search & Raw Material Gathering

**Goal**: Cast a wide net. Gather diverse source materials from multiple channels.

Perform searches across these categories:

#### 1.1 Social Media & Community Discussion
- **Twitter/X**: Search for topic-related tweets, threads from experts
- **Reddit**: Relevant subreddits, top posts, AMAs
- **Discord/Telegram**: Notable community discussions (if accessible)
- **Hacker News**: Technical discussions

**Search strategy**: Use 3-5 different search queries per platform, varying keywords.

#### 1.2 Expert Voices
- **Twitter/X accounts**: Find recognized experts on the topic, save their relevant posts
- **YouTube**: Search for talks, tutorials, explainers (save links + key timestamps, NOT videos)
- **Blogs/Vlogs**: Medium articles, Substack posts, personal blogs from practitioners
- **Podcasts**: Find relevant episodes (save links + timestamps)

#### 1.3 Academic & Technical Papers
- **arxiv.org**: Search for relevant preprints
- **Google Scholar**: Academic papers and citations
- **SSRN**: Working papers (especially for finance/economics topics)
- **Conference proceedings**: NeurIPS, ICML, etc. for ML topics

#### 1.4 Open Source & Tools
- **GitHub**: Repositories, code examples, existing implementations
- **npm/PyPI**: Relevant packages and libraries
- **Documentation**: Official docs for platforms/APIs involved

#### 1.5 News & Analysis
- **News articles**: Recent coverage of the topic
- **Industry reports**: Market analysis, trend reports
- **Blog posts**: Technical deep-dives from practitioners

### Raw Material Storage Rules

Save **every** gathered resource to `raw_material/` with these rules:

| Source Type    | Format  | Naming Convention                                             |
| -------------- | ------- | ------------------------------------------------------------- |
| Tweet/thread   | `.md`   | `twitter_{author}_{topic_short}.md`                           |
| Reddit post    | `.md`   | `reddit_{subreddit}_{title_short}.md`                         |
| Article/blog   | `.md`   | `article_{source}_{title_short}.md`                           |
| Academic paper | `.md`   | `paper_{author}_{year}_{title_short}.md`                      |
| YouTube video  | `.md`   | `youtube_{channel}_{title_short}.md` (link + key points only) |
| GitHub repo    | `.md`   | `github_{owner}_{repo}.md` (README excerpt + key details)     |
| Search results | `.json` | `search_{query_short}.json`                                   |
| API response   | `.json` | `api_{endpoint}_{description}.json`                           |

**Content rules for `.md` files**:
```markdown
# Source: [title]
- **URL**: [original URL]
- **Author**: [author name]
- **Date**: [publication date]
- **Type**: [tweet/article/paper/video/repo]
- **Relevance**: [1-sentence why this is relevant]

## Key Content
[Stripped-down content: main arguments, data points, conclusions]
[For videos: key timestamps + summary of each section]

## Notable Quotes
> [Direct quotes worth referencing]

## Tags
[comma-separated tags for cross-referencing]
```

### Phase 2: Compose Research Objectives

**Goal**: After reviewing raw materials, define concrete, actionable research objectives.

Create `{research_dir}/objectives.md` with this structure:

```markdown
# Research Objectives: {topic}

## Final Objective
[One clear sentence describing the end goal]
Example: "Build a complete, evidence-backed import and annotation workflow"

## Sub-Objectives

### 1. Community & Expert Analysis
All discussions on the topic, ordered by influence/authority.
**Status**: [ ] Not started

### 2. Open Source & Service Landscape
Current open-source tools, services, and frameworks related to the final objective.
**Status**: [ ] Not started

### 3. Competitive Analysis
Who else is doing this? How? What are their advantages/disadvantages vs. us?
**Status**: [ ] Not started

### 4. Execution Pipeline Design
Step-by-step execution pipeline. For each node: what data/resources are needed.
**Status**: [ ] Not started

### 5. Resource Gap Analysis
What data/resources we currently have vs. what is needed. Cost estimates for gaps.
**Status**: [ ] Not started
```

> **Important**: The sub-objectives above are **examples**. Adapt them to the specific topic. Add or remove objectives as appropriate. Each objective should be specific enough to produce a concrete deliverable.

**Present objectives to the user for review before proceeding to Phase 3.**

### Phase 3: Execute Research Objectives

**Goal**: Systematically complete each research objective with detailed findings.

For each sub-objective:

1. **Mark as in-progress** in `objectives.md` (`[/]`)
2. **Do focused research** — additional searches, deeper analysis of raw materials
3. **Write detailed findings** directly in `objectives.md` under the objective
4. **Include evidence** — cite raw materials, link to sources
5. **Mark as complete** (`[x]`)
6. **Update the user** after completing each objective (via walkthrough if in task mode)

### Findings Format (per objective)

```markdown
### N. [Objective Title]
**Status**: [x] Complete

#### Summary
[2-3 sentence executive summary]

#### Detailed Findings
[Structured analysis with headers, tables, lists as appropriate]

#### Evidence & Sources
- [Source 1](link) — [what it proves]
- [Source 2](link) — [what it proves]

#### Implications for Our Project
[How this finding affects our approach]
```

### Phase 4: Synthesis

**Goal**: Tie all findings together into actionable recommendations.

After all objectives are complete, add a synthesis section to `objectives.md`:

```markdown
## Synthesis & Recommendations

### Key Findings
1. [Finding 1]
2. [Finding 2]
...

### Recommended Approach
[Based on all research, what should we build/do?]

### Risk Assessment
[What could go wrong?]

### Next Steps
[Concrete action items with priorities]
```

## Output Artifacts

After completion, the research directory should contain:

```
research/{project}/{topic}/
  README.md              ← session context
  objectives.md          ← objectives + detailed findings + synthesis
  raw_material/
    twitter_*.md         ← social media sources
    reddit_*.md
    article_*.md         ← blog/news articles
    paper_*.md           ← academic papers
    youtube_*.md         ← video references (links only)
    github_*.md          ← repo analyses
    search_*.json        ← raw search results
    api_*.json           ← API data captures
```

## Report Format

Present the final research summary as a walkthrough report file with:

1. **Objective completion status** (checklist)
2. **Key findings per objective** (concise)
3. **Synthesis & recommendations**
4. **Links to all raw materials and detailed findings**
