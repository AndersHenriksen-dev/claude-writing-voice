"""PreToolUse hook: keep markdown in my own writing voice, in the repos that ask for it.

Claude Code runs this before every Edit, Write and MultiEdit in every session the plugin is enabled in, so
the first thing it does is look for `.claude/writing-voice.json` in the repo the call belongs to. Without
that file it exits without reading anything, which is what keeps an installed plugin out of a CV, a cover
letter and every other repo on the machine. With it, the markdown in the call is checked against the
plugin's rules, with anything in that file laid over them, and a call that fires a rule is denied with the
findings so the text is rewritten before it reaches a file.

On the command line the check always runs, since asking for it is the point. A file that has to quote the
patterns it bans opts out with the line `<!-- writing-check: off -->`.
"""

from __future__ import annotations

import json
import os
import re
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Any

DEFAULT_RULES_PATH = Path(__file__).parents[1] / "writing_rules.json"
OPT_IN_NAME = "writing-voice.json"
STYLE_GUIDE = "the guide skill of the writing-voice plugin"
OPT_OUT = "<!-- writing-check: off -->"

# Edits arrive as fragments, where a sentence average says nothing. Only measure cadence on a real passage.
CADENCE_MINIMUM_WORDS = 80

# Parts of a file the checks must not read: code, link targets and anything in quotation marks, which is
# how both this repo and the skill it borrows from mark an example of writing to avoid.
HTML_COMMENT = re.compile(r"<!--.*?-->", re.DOTALL)
FENCED_CODE = re.compile(r"```.*?```", re.DOTALL)
INLINE_CODE = re.compile(r"`[^`]*`")
LINK_TARGET = re.compile(r"\]\([^)]*\)")
QUOTED = re.compile(r"\"[^\"\n]*\"")

CHECKBOX = re.compile(r"^\s*[-*+]\s+\[[ xX]\]\s")
TABLE_ROW = re.compile(r"^\s*\|")
EM_DASH = re.compile(r"[—–]|(?<![-\w])--(?![-\w])")
BOLD_SPAN = re.compile(r"\*\*[^*\n]+\*\*")
BOLD_LEAD_IN = re.compile(r"^\s*(?:[-*+]\s+|\d+\.\s+)?\*\*", re.MULTILINE)
EMPHASIS = re.compile(r"\*+|_{2,}")
SENTENCE_END = re.compile(r"[.!?]+(?:\s|$)")
WORD = re.compile(r"[A-Za-z0-9'’-]+")

FILE_PATH_KEYS: dict[str, str] = {"Edit": "file_path", "Write": "file_path", "MultiEdit": "file_path"}


@dataclass(frozen=True)
class Finding:
    """One rule that fired, in the words the agent is shown."""

    rule: str
    detail: str
    blocking: bool


@dataclass(frozen=True)
class Cadence:
    """How a passage sits against the shape of Anders's own writing."""

    words: int
    mean_sentence_words: float
    short_sentence_share: float
    contrast_per_100_words: float


def strip_examples(text: str) -> str:
    """Blank out code, link targets and quoted text, so an example of bad writing is not read as bad writing.

    Args:
        text: The markdown about to be written.

    Returns:
        The same text with those spans replaced by a single space.
    """
    for pattern in (HTML_COMMENT, FENCED_CODE, INLINE_CODE, LINK_TARGET, QUOTED):
        text = pattern.sub(" ", text)
    return text


def sentence_word_counts(prose: str) -> list[int]:
    """Count the words in each sentence, ignoring headings, list markers and empty lines."""
    body = "\n".join(line for line in prose.splitlines() if not line.lstrip().startswith("#"))
    counts = [len(WORD.findall(sentence)) for sentence in SENTENCE_END.split(EMPHASIS.sub("", body))]
    return [count for count in counts if count > 0]


def count_phrases(prose: str, phrases: list[str]) -> dict[str, int]:
    """Count how often each phrase appears, case-insensitively, as a whole word where it is one."""
    found: dict[str, int] = {}
    lowered = prose.lower()
    for phrase in phrases:
        pattern = re.escape(phrase.lower())
        if phrase[0].isalpha():
            pattern = r"\b" + pattern
        hits = len(re.findall(pattern, lowered))
        if hits:
            found[phrase] = hits
    return found


def measure_cadence(prose: str, rules: dict[str, Any]) -> Cadence:
    """Work out the three numbers that separate his prose from generated prose.

    Args:
        prose: The text with examples already stripped.
        rules: The `cadence` block of writing_rules.json.

    Returns:
        The measurements, with zeros when there is no sentence to measure.
    """
    counts = sentence_word_counts(prose)
    words = sum(counts)
    if not counts or not words:
        return Cadence(words=0, mean_sentence_words=0.0, short_sentence_share=0.0, contrast_per_100_words=0.0)
    short = sum(1 for count in counts if count < int(rules["short_sentence_words"]))
    contrasts = sum(count_phrases(prose, list(rules.get("contrast_phrases", []))).values())
    return Cadence(
        words=words,
        mean_sentence_words=words / len(counts),
        short_sentence_share=short / len(counts),
        contrast_per_100_words=100 * contrasts / words,
    )


def is_structured(text: str, share: float) -> bool:
    """Say whether a file is a checklist or a form, where short bolded items are the genre rather than a tell.

    Args:
        text: The markdown, with examples already stripped.
        share: How much of the file has to be checkbox or table lines before it counts.

    Returns:
        True when checkbox and table lines make up at least that share of the lines that carry content.
    """
    lines = [line for line in text.splitlines() if line.strip() and not line.lstrip().startswith("#")]
    if not lines:
        return False
    structured = sum(1 for line in lines if CHECKBOX.match(line) or TABLE_ROW.match(line))
    return structured / len(lines) >= share


def check_formatting(text: str, max_bold: int) -> list[Finding]:
    """Check the formatting tells: em dashes, bolded lead-ins and bold used as decoration."""
    findings: list[Finding] = []
    dashes = len(EM_DASH.findall(text))
    if dashes:
        findings.append(Finding("em dash", f"{dashes} found. Use commas, colons, full stops or brackets.", True))
    lead_ins = len(BOLD_LEAD_IN.findall(text))
    if lead_ins:
        findings.append(
            Finding("bold lead-in", f"{lead_ins} lines open with a bolded term. Lead with the point instead.", True),
        )
    bolds = len(BOLD_SPAN.findall(text))
    if bolds > max_bold:
        findings.append(Finding("bold overuse", f"{bolds} bolded spans, at most {max_bold} per file.", True))
    return findings


def check_cadence(cadence: Cadence, rules: dict[str, Any]) -> list[Finding]:
    """Check sentence length, short-sentence share and contrast density against his own numbers."""
    findings: list[Finding] = []
    if cadence.words < CADENCE_MINIMUM_WORDS:
        return findings
    if cadence.mean_sentence_words < float(rules["min_mean_sentence_words"]):
        findings.append(
            Finding(
                "sentences too short",
                f"{cadence.mean_sentence_words:.1f} words on average, "
                f"under the floor of {rules['min_mean_sentence_words']}. He averages 29.",
                True,
            ),
        )
    if cadence.short_sentence_share > float(rules["max_short_sentence_share"]):
        findings.append(
            Finding(
                "clipped sentences",
                f"{cadence.short_sentence_share:.0%} of sentences are under "
                f"{rules['short_sentence_words']} words, over the {float(rules['max_short_sentence_share']):.0%} "
                "ceiling. Short closing sentences are where aphorisms hide.",
                True,
            ),
        )
    if cadence.contrast_per_100_words > float(rules["max_contrast_per_100_words"]):
        findings.append(
            Finding(
                "contrast habit",
                f"{cadence.contrast_per_100_words:.1f} per 100 words of 'rather than', 'instead of' and "
                "'X, not Y'. He uses 0.4. State the positive claim.",
                False,
            ),
        )
    return findings


def review(text: str, rules: dict[str, Any]) -> list[Finding]:
    """Run every check over one piece of markdown.

    Args:
        text: The markdown about to be written.
        rules: The parsed writing_rules.json.

    Returns:
        Every finding, blocking and advisory, in the order they are worth reading.
    """
    if marked_opted_out(text):
        return []
    prose = strip_examples(text)
    checklist = is_structured(prose, float(rules["structured_line_share"]))
    findings = [] if checklist else check_formatting(prose, int(rules["max_bold_spans"]))
    dashes = len(EM_DASH.findall(prose)) if checklist else 0
    if dashes:
        findings.append(Finding("em dash", f"{dashes} found. Use commas, colons, full stops or brackets.", True))
    banned = count_phrases(prose, list(rules["banned_phrases"]))
    if banned:
        listed = ", ".join(f"{phrase} ({hits})" for phrase, hits in sorted(banned.items()))
        findings.append(Finding("banned phrase", listed, True))
    if checklist:
        return findings
    cadence_rules = dict(rules["cadence"])
    cadence_rules["contrast_phrases"] = rules.get("contrast_phrases", [])
    return findings + check_cadence(measure_cadence(prose, cadence_rules), cadence_rules)


def format_reason(findings: list[Finding]) -> str:
    """Turn the findings into the message the agent gets back in place of the write."""
    lines = [f"- {finding.rule}: {finding.detail}" for finding in findings]
    advisory = [finding for finding in findings if not finding.blocking]
    closing = f"The rules and the reasoning are in {STYLE_GUIDE}."
    if advisory:
        closing += " The last entries are advice, not blocks."
    return "This markdown reads as AI writing. Rewrite it and try again.\n" + "\n".join(lines) + "\n" + closing


def markdown_in_call(payload: dict[str, Any]) -> tuple[str, str]:
    """Pull the file path and the markdown out of an Edit, Write or MultiEdit call.

    Args:
        payload: The hook payload Claude Code puts on stdin.

    Returns:
        The file path and the text being written, both empty when the call is not one to check.
    """
    tool = str(payload.get("tool_name", ""))
    if tool not in FILE_PATH_KEYS:
        return "", ""
    tool_input = dict(payload.get("tool_input", {}))
    path = str(tool_input.get(FILE_PATH_KEYS[tool], ""))
    if not path.lower().endswith(".md"):
        return "", ""
    if tool == "Write":
        return path, str(tool_input.get("content", ""))
    if tool == "MultiEdit":
        edits = [str(edit.get("new_string", "")) for edit in tool_input.get("edits", [])]
        return path, "\n\n".join(edits)
    return path, str(tool_input.get("new_string", ""))


def report_on_files(paths: list[str], rules: dict[str, Any]) -> int:
    """Print the findings for files named on the command line, for a check outside an agent.

    Args:
        paths: The markdown files to read.
        rules: The parsed writing_rules.json.

    Returns:
        1 when any file has a blocking finding, so that a script can act on it, and 0 otherwise.
    """
    blocked = False
    for raw_path in paths:
        path = Path(raw_path)
        findings = review(path.read_text(encoding="utf-8"), rules)
        if not findings:
            print(f"{path}: reads fine")
            continue
        print(f"{path}:")
        for finding in findings:
            print(f"  - {finding.rule}: {finding.detail}")
        blocked = blocked or any(finding.blocking for finding in findings)
    return 1 if blocked else 0


def deny(reason: str) -> None:
    """Block the tool call and hand back the reason, in the shape Claude Code expects."""
    decision = {
        "hookSpecificOutput": {
            "hookEventName": "PreToolUse",
            "permissionDecision": "deny",
            "permissionDecisionReason": reason,
        },
    }
    print(json.dumps(decision))
    sys.exit(0)


def marked_opted_out(text: str) -> bool:
    """Say whether the opt-out line stands on a line of its own.

    A file that only mentions the marker in a sentence, which any file documenting the convention does, is still
    checked, so the marker counts only where it is the whole of a line.

    Args:
        text: The markdown to look in.

    Returns:
        True when one line is nothing but the marker.
    """
    return any(line.strip() == OPT_OUT for line in text.splitlines())


def opt_in_file(root: Path) -> Path:
    """Point at the file a repo uses to say that it wants its markdown checked.

    Args:
        root: The repo the call belongs to.

    Returns:
        The path the repo's own rules would sit at, whether or not anything is there.
    """
    return root / ".claude" / OPT_IN_NAME


def project_root(payload: dict[str, Any]) -> Path:
    """Work out which repo the call belongs to.

    Args:
        payload: The hook payload Claude Code puts on stdin.

    Returns:
        The project directory from the environment, falling back to the payload and then to the working directory.
    """
    for candidate in (os.environ.get("CLAUDE_PROJECT_DIR"), payload.get("cwd")):
        if candidate:
            return Path(str(candidate))
    return Path.cwd()


def merge_rules(defaults: dict[str, Any], asked: dict[str, Any]) -> dict[str, Any]:
    """Lay a repo's own rules over the plugin's, one level deep so a single threshold can be changed on its own.

    Args:
        defaults: The plugin's writing_rules.json.
        asked: Whatever the repo put in its own file, which is usually nothing.

    Returns:
        The rules to check against.
    """
    merged = dict(defaults)
    for key, value in asked.items():
        inherited = merged.get(key)
        merged[key] = {**inherited, **value} if isinstance(value, dict) and isinstance(inherited, dict) else value
    return merged


def read_rules(override: Path) -> dict[str, Any]:
    """Read the plugin's rules, with the repo's own file laid over them when there is one.

    A repo that is happy with the defaults opts in with an empty object, and a file that cannot be parsed is
    reported on stderr and ignored, so a typo in it never blocks writing.

    Args:
        override: The repo's .claude/writing-voice.json, which need not exist.

    Returns:
        The rules to check against.
    """
    defaults: dict[str, Any] = json.loads(DEFAULT_RULES_PATH.read_text(encoding="utf-8"))
    if not override.is_file():
        return defaults
    try:
        asked = json.loads(override.read_text(encoding="utf-8") or "{}")
    except json.JSONDecodeError as problem:
        print(f"writing-voice: ignoring {override}, which is not valid JSON ({problem}).", file=sys.stderr)
        return defaults
    return merge_rules(defaults, dict(asked))


def opts_out(path: str, text: str) -> bool:
    """Say whether this file has opted out of the checks, in the write itself or on disk already.

    An Edit arrives as a fragment, which does not carry the marker sitting on the first line of the file it is
    editing, so the file as it stands has to be read before a fragment of an opted-out file is judged.

    Args:
        path: The file the call is about to write.
        text: The markdown in the call.

    Returns:
        True when either the text or the file already on disk carries the opt-out line.
    """
    if marked_opted_out(text):
        return True
    existing = Path(path)
    return existing.is_file() and marked_opted_out(existing.read_text(encoding="utf-8"))


def read_payload() -> str:
    """Read the hook payload as UTF-8, whatever the console encoding happens to be.

    Claude Code writes the payload as UTF-8 bytes, and a Windows console hands Python cp1252 instead, which
    turns an em dash into three characters none of the checks can see. Decoding the raw bytes keeps every
    tell readable on every platform.

    Returns:
        The payload text, with anything undecodable replaced.
    """
    return sys.stdin.buffer.read().decode("utf-8", errors="replace")


def main() -> int:
    """Review the files named on the command line, or the markdown in the tool call waiting on stdin.

    As a hook this returns without reading the call at all unless the repo carries `.claude/writing-voice.json`,
    which is the whole of the gate that keeps the plugin out of repos that never asked for it.
    """
    if sys.argv[1:]:
        return report_on_files(sys.argv[1:], read_rules(opt_in_file(Path.cwd())))
    try:
        payload = json.loads(read_payload() or "{}")
    except json.JSONDecodeError:
        return 0
    opt_in = opt_in_file(project_root(payload))
    if not opt_in.is_file():
        return 0
    path, text = markdown_in_call(payload)
    if not path or not text.strip() or opts_out(path, text):
        return 0
    findings = review(text, read_rules(opt_in))
    if any(finding.blocking for finding in findings):
        deny(format_reason(findings))
    return 0


if __name__ == "__main__":
    sys.exit(main())
