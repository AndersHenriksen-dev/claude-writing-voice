# Claude writing voice

A Claude Code plugin that keeps markdown in my own writing voice, and a marketplace of one so that it installs
from this folder without going through GitHub. The voice itself, with the numbers it was measured from, is in
[the guide skill](plugins/writing-voice/skills/guide/SKILL.md).

## What is in it

A skill holding the guide, which says how the sentences are built, how a piece opens and closes, which words I
reach for and what never goes in. A hook that runs before every edit and write, checks the markdown in the call
against the rules, and denies the call with its findings when a rule fires, so the text gets rewritten before it
reaches a file instead of after a reader notices it sounds generated. Two scripts behind it, one that checks a
file and one that measures it, and the rules as data in
[writing_rules.json](plugins/writing-voice/writing_rules.json).

## It stays out of the way until a repo asks for it

An enabled plugin is part of every session, so the hook would otherwise fire on everything I write in every repo
on this machine, including the writing that already has a voice of its own, such as a CV or a letter, where these
rules would be the wrong ones. The first thing the hook does is look for
`.claude/writing-voice.json` in the repo the call belongs to, and without that file it exits without reading the
call at all.

A repo opts in by running `/writing-voice:enable`, or by writing the file by hand, and an empty object takes the
rules as they ship:

```powershell
New-Item -ItemType Directory -Force .claude; Set-Content -Encoding utf8 .claude\writing-voice.json '{}'
```

The same file overrides any rule for that repo alone, laid one level deep over the defaults, so a repo that wants
more bold and longer sentences than I usually write can say so and leave everything else as it is:

```json
{ "max_bold_spans": 10, "cadence": { "min_mean_sentence_words": 20 } }
```

Deleting the file turns the whole thing off again for that repo.

The skill is gated differently, since a skill cannot read the repo before an agent has chosen it. Its description
says to use the voice only when I ask for it by name or when that file is present, and my global CLAUDE.md says
the same, which makes the skill side a matter of the agent following instructions rather than something the plugin
enforces.

## Installing it

From a shell, with the path to this folder:

```powershell
claude plugin marketplace add <path to this folder>
```

```powershell
claude plugin install writing-voice@anders-plugins
```

## Using it without an agent

Check one or more files, which works in any repo whether or not it has opted in, since asking for the check is the
point:

```powershell
uv run --no-project python plugins\writing-voice\scripts\check_markdown_writing.py FILE.md
```

Measure a file against the table in the guide:

```powershell
uv run --no-project python plugins\writing-voice\scripts\measure_voice.py FILE.md
```

Add `--registers` when the file holds sample answers under headings, which splits the numbers by heading instead
of averaging several kinds of writing into one row.

## The scripts

The ruff and mypy settings are in [pyproject.toml](pyproject.toml), and both tools read them straight from there
without a virtual environment:

```powershell
uvx ruff@0.14.4 check plugins/
```

```powershell
uvx mypy@1.18.2 plugins/writing-voice/scripts/
```
