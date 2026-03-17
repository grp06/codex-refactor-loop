---
name: find-best-refactor
description: Find the single highest-leverage refactor in a repo from first principles. Use when the user asks what to refactor, wants the best refactor, highest-leverage cleanup, architectural simplification, boundary extraction, duplication removal, complexity reduction, testability improvement, or an ExecPlan for the best refactor. Accept optional user guidance about scope, constraints, refactor style, or risk tolerance.
---

# Find Best Refactor

## Overview

Inspect the repo from first principles, generate multiple plausible refactor candidates, and pick the one with the best leverage relative to cost and risk.

Do not ask the user to choose among options. Make the call, explain it, and write an implementation-ready ExecPlan.

## Mindset

Approach this like a principal engineer finding the one refactor that most improves the codebase per unit of churn.

You are not limited to one refactor shape. The winning move might be:
- consolidation of duplicate abstractions or parallel modules
- extraction of domain logic from infrastructure-heavy flows
- removal of a dead or thin abstraction layer
- extraction of an implicit state machine or policy engine
- merge of duplicate orchestration paths
- simplification of a leaky interface that forces callers to know too much

The question you are answering is:
"What is the single highest-leverage refactor in this repo, given the evidence and any user guidance?"

## User Guidance Handling

The user may give extra guidance when invoking the skill. Use it, but interpret it correctly.

Treat guidance as one of two kinds:

- **Hard constraints** — explicit scope or prohibitions such as:
  - "only look in `app/auth`"
  - "do not propose schema changes"
  - "stay in the frontend"
  - "find the best low-risk refactor"
- **Soft guidance** — hints or priors such as:
  - "I think the API layer is messy"
  - "prefer testability wins"
  - "I suspect auth has duplication"
  - "look for something we could land quickly"

Rules:
- Honor hard constraints strictly.
- Treat soft guidance as a weighting signal, not as proof.
- If the repo-wide best candidate differs from the soft guidance, still make the best call within the guided scope if the user clearly wanted that scope. Briefly mention the distinction.
- If the user names a refactor type explicitly, evaluate that type first, but reject it if the evidence is weak and another interpretation is clearly better within the stated scope.

## Workflow

### Step 1: Establish Scope and Constraints

Determine scope from context. Default to the workspace root if unspecified.

Infer and state:
- target repo or directory
- hard constraints
- soft guidance
- risk tolerance
- whether the user wants the repo-wide best refactor or the best refactor inside a named area

Do not ask clarifying questions unless the guidance is directly contradictory.

### Step 2: Build a First-Principles Model of the Repo

Read the codebase systematically:
1. Start with `README`, `ARCHITECTURE.md`, or similar docs.
2. Identify languages, frameworks, major entry points, and the top 5-10 most referenced modules.
3. Map 3-5 core user-facing or business-critical flows.
4. Collect lightweight repo evidence before proposing anything:
   - import/reference frequency
   - file size and directory spread
   - change frequency from git history when available
   - co-change evidence for concepts that evolve together
   - whether tests exist near the affected code
   - whether the area is a stable core path or a niche edge path

Output a mental model:
- core concepts and file locations
- dependency highlights
- major flows
- evidence signals that suggest leverage or risk

### Step 3: Generate Candidate Refactor Classes

Generate 2-5 candidates across refactor classes. Good candidates often come from these patterns:

- **Consolidation**
  - duplicate abstractions
  - thin wrappers
  - parallel hierarchies
  - config-driven duplication
  - branch-by-environment forks
  - duplicate state models
- **Boundary extraction**
  - domain logic buried in handlers, repositories, consumers, or middleware
  - I/O-heavy god flows
  - transformation pipelines coupled to fetch/write steps
  - shared mutable state between boundary and core
- **Control-flow extraction**
  - implicit state machines
  - policy logic spread across unrelated files
  - duplicated orchestration with minor variations
- **Layer removal**
  - dead adapters
  - pass-through services
  - stale compatibility layers
  - abstractions whose callers still know implementation details

For each candidate, capture:
- candidate name
- refactor class
- files and flows involved
- why it looks promising
- what evidence supports it
- what could make it a trap

Actively collect negative evidence too:
- what only looks duplicated but is intentionally separate
- what is ugly but actually a clean boundary
- what would require a rewrite rather than a refactor
- what lies outside hard constraints

### Step 4: Score Candidates

Filter out any candidate that violates hard user constraints.

Score remaining candidates with this rubric:

| Criteria | Weight | Score (1-5) |
|----------|--------|-------------|
| Leverage/payoff (concepts removed, complexity reduced, future work unblocked) | 25% | |
| Blast radius vs. risk | 20% | |
| Cognitive load reduction | 15% | |
| Testability or boundary improvement | 15% | |
| Bug surface reduction | 10% | |
| Seam clarity (how clear the cut line is) | 5% | |
| Evidence confidence | 5% | |
| Ease of validation/rollback | 5% | |

Apply modifiers:
- small bonus for matching soft user guidance
- penalty for weak evidence
- penalty for hidden migration cost
- penalty for speculative architecture
- penalty when the candidate sounds elegant but removes little real pain

The winner is the highest-scoring candidate after modifiers.

### Step 5: Make the Call

Present only the single best refactor.

Your answer should include:
1. **Current state** — what exists today and why it hurts
2. **Chosen refactor class** — consolidation, boundary extraction, layer removal, state-machine extraction, or similar
3. **Scope** — exact files and flows involved
4. **Why this is the best move** — evidence-based rationale
5. **What stays untouched** — boundary of the change
6. **Implementation sketch** — target module shape, moves, import changes, and the first 1-2 tests to write or update
7. **Risks and mitigations** — realistic failure modes
8. **Why not the others** — 1-2 bullets per rejected candidate

If user guidance materially shaped the outcome, say how:
- "This is the best refactor within the frontend scope you requested."
- "Repo-wide, I would also consider X, but within your auth focus this is the best move."

### Step 6: Write the ExecPlan

After choosing the winner:
1. Use the `execplan-create` skill.
2. Read `{baseDir}/.agent/PLANS.md` in full.
3. If `{baseDir}/.agent/PLANS.md` is missing, follow the `execplan-create` fallback flow and use its bundled `PLANS.md`.
4. Write the plan to `.agent/execplan-pending.md`.
5. Make the plan implementation-ready: name specific files, describe the cut line, note the first safe slice to land, define validation steps, and include rollback notes.

## Anti-Patterns to Avoid

- **Offering a menu** — Do not ask the user to pick from candidates.
- **Confusing scope guidance with proof** — A user hunch is a lead, not evidence.
- **Ignoring explicit user bounds** — If they said "frontend only," do not roam the backend.
- **Function-level nitpicking** — Focus on flow/module-level leverage, not tiny local cleanups.
- **Cosmetic refactors** — Renames and formatting are not winning moves.
- **Boiling the ocean** — Avoid repo-wide rewrites disguised as refactors.
- **No evidence** — Every recommendation must cite files, flows, and concrete signals.
- **Shallow wins** — Prefer fewer concepts, cleaner seams, and lower future bug surface over cleverness.
- **Vague plans** — If someone could not start implementation from the ExecPlan, the job is incomplete.
