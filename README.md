# `codex-refactor-loop`

`run-cycle` is a small CLI that drives the Codex app-server through a repeatable multi-turn workflow.

The point is simple: if you use Codex directly, you often get one useful pass and then have to remember what to ask next. Improve the plan. Improve it again. Implement it. Review the result. Review it again with fresh eyes. `run-cycle` turns that sequence into one command.

It keeps the whole run on one Codex thread, so later stages build on earlier work instead of starting over. It also writes a complete run log, which makes the session inspectable after the fact rather than something that only existed in the terminal.

By default, one cycle is:

1. `execplan-create`
2. `execplan-improve` x4
3. `implement-execplan`
4. `review-recent-work` x5

You can change the number of full cycles, improvement passes, and review passes.

## Why Use It

- It turns a hand-run prompting sequence into a deterministic loop.
- It preserves continuity by reusing one thread across planning, implementation, and review.
- It stays noninteractive, so failures are explicit instead of hiding behind approval prompts.
- It keeps the terminal readable by showing only agent commentary, final agent text, and token usage.
- It writes a full timestamped log with stage banners, command output, file-change progress, MCP progress, and item lifecycle events.
- It works from the root of any repo because it sends your current working directory to `thread/start`.

This is useful when you want compounding effort rather than a single answer.

## Prerequisites

- Python 3.11 or newer.
- Rust and `cargo`.
- A separate clone of the open-source Codex repository.
- ChatGPT authentication if the active Codex provider requires OpenAI auth.

The bundled skills used by `run-cycle` live in `.agents/skills` inside this repository.

## Setup

Clone this repository and clone Codex separately:

```bash
git clone https://github.com/grp06/codex-refactor-loop.git
git clone https://github.com/openai/codex.git
```

Point `run-cycle` at the Codex Rust workspace:

```bash
export CODEX_WORKSPACE=/path/to/codex/codex-rs
```

You can also pass the path per command with `--codex-workspace /path/to/codex/codex-rs`.

Authenticate through the wrapped Codex login flow:

```bash
cd codex-refactor-loop
./run-cycle auth login
./run-cycle auth login --device-auth
./run-cycle auth status
./run-cycle auth logout
```

The auth wrapper keeps stdin, stdout, and stderr attached to the terminal, so browser and device-code login behave like native `codex login`.

If you sign in with your ChatGPT account, Codex uses the access included with your ChatGPT plan. OpenAI's current docs say Codex is included with ChatGPT Plus and Pro, so the normal ChatGPT-authenticated flow uses that plan-backed access for inference instead of requiring you to paste an API key manually. Official docs: [Using Codex with your ChatGPT plan](https://help.openai.com/en/articles/11369540-using-codex-with-your-chatgpt-plan).

## Basic Use

Run the default workflow from the repository you want Codex to work on:

```bash
cd /path/to/target-repo
/path/to/codex-refactor-loop/run-cycle --prompt "help me build a CRM"
```

Start from refactoring instead of greenfield planning:

```bash
cd /path/to/target-repo
/path/to/codex-refactor-loop/run-cycle --mode refactor --prompt "focus on testability and simplifying boundaries"
/path/to/codex-refactor-loop/run-cycle --mode refactor
```

Increase the amount of iteration:

```bash
cd /path/to/target-repo
/path/to/codex-refactor-loop/run-cycle --prompt "help me build a CRM" --cycles 2 --improvements 5 --review 3
```

`run-cycle` always targets the directory you launch it from, not the `codex-refactor-loop` repository.

## Modes And Counts

`--mode pipeline` is the default. It requires `--prompt` and starts with `execplan-create`.

`--mode refactor` keeps the same follow-up structure, but replaces stage 1 with `find-best-refactor`. `--prompt` is optional in refactor mode. If you omit it, the first stage asks for the single highest-leverage refactor in the current repository.

`--cycles` controls how many times the full loop runs.

`--improvements` controls how many `execplan-improve` turns run inside each cycle.

`--review` controls how many `review-recent-work` turns run inside each cycle.

Defaults:

- `--cycles 1`
- `--improvements 4`
- `--review 5`

When `--cycles` is greater than 1, stage labels in the run log are cycle-qualified, for example `cycle-2-execplan-create`.

## Codex Workspace Configuration

When `run-cycle` launches the real Codex app-server or wrapped auth commands, it resolves the Codex workspace in this order:

1. `--codex-workspace /path/to/codex-rs`
2. `CODEX_WORKSPACE`

If neither is set, the command fails with a clear setup error.

Examples:

```bash
./run-cycle --codex-workspace /path/to/codex/codex-rs --prompt "help me build a CRM"
./run-cycle auth --codex-workspace /path/to/codex/codex-rs login
```

## What It Actually Does

Before stage 1, the client performs:

1. `initialize` with `capabilities.experimentalApi = true`
2. `initialized`
3. `account/read`
4. `thread/start`

If `account/read` says OpenAI auth is required and no account is logged in, the command fails immediately and tells you to run `./run-cycle auth login`.

After that, every stage runs as a `turn/start` on the same thread. That is what gives the workflow continuity. The implementation and review stages see the plan that was just created and improved.

## Output Model

The terminal is intentionally sparse. During a run, it shows:

- agent-message commentary
- final agent-message text
- token usage

Everything else goes to the run log:

- stage banners
- command output
- file-change progress
- MCP progress
- item lifecycle notices
- failure details

Each run writes a full log to `runs/`. Log filenames start with the basename of the directory you launched from, followed by a UTC timestamp, for example `my-repo-20260317T213000Z.log`.

This split is deliberate. The terminal stays readable while the log remains complete.

## Reliability Contract

- Model and sandbox settings are inherited from your current Codex config. In v1, `run-cycle` only overrides `cwd` and `approvalPolicy`.
- The thread uses `approvalPolicy: "never"`.
- If the server asks for approvals, user input, permissions, MCP elicitation, or ChatGPT token refresh, `run-cycle` responds deterministically, marks the stage failed, and exits after the matching `turn/completed`.
- Successful turns require real token data from `thread/tokenUsage/updated`. If a turn completes successfully without token usage, the run fails instead of printing invented zeros.
- Skill paths are validated before the app-server starts, so broken local setup fails early.

The tool is strict on purpose. When something is wrong, it should stop in a way you can diagnose.

## Tests

Run the test suite from the repository root:

```bash
python3 -m unittest discover -s tests -p 'test_*.py' -v
```
