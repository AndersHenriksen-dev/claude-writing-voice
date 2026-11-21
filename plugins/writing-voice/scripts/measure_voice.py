"""Print the numbers behind the voice the guide skill describes.

The hook next to this file blocks markdown that misses the target. This prints what the target is made of, for
whole files or, with --registers, for each heading of a file of sample answers, so the numbers in the guide can be
recounted from a new batch of writing instead of being trusted from memory.

It shares the hook's tokenizer on purpose, since a number counted a different way from the one the hook enforces
would not describe the same writing.
"""

from __future__ import annotations

import re
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from check_markdown_writing import (
    CHECKBOX,
    WORD,
    count_phrases,
    opt_in_file,
    read_rules,
    sentence_word_counts,
    strip_examples,
)

REGISTER_HEADING = re.compile(r"^##\s+(.+?)\s*$")
REGISTERS_FLAG = "--registers"
SHORT_SENTENCE_WORDS = 9


@dataclass(frozen=True)
class Voice:
    """One passage measured in the terms the style guide uses."""

    name: str
    words: int
    sentences: int
    mean_sentence_words: float
    longest_sentence_words: int
    short_sentence_share: float
    first_person_per_100: float
    hedges_per_100: float
    contrast_per_100: float


def count_markers(prose: str, markers: list[str]) -> int:
    """Count the words in a passage that appear in a marker list, matching whole words only.

    Args:
        prose: The text with examples already stripped.
        markers: Lowercase words to look for, such as the first person or the hedges.

    Returns:
        How many of the passage's words are in the list.
    """
    listed = {marker.lower() for marker in markers}
    return sum(1 for token in WORD.findall(prose) if token.lower() in listed)


def measure(name: str, text: str, rules: dict[str, Any]) -> Voice:
    """Measure one passage.

    Args:
        name: What the passage is called in the printed table.
        text: The markdown of the passage.
        rules: The parsed writing_rules.json.

    Returns:
        The measurements, with zeros where there is nothing to measure.
    """
    prose = strip_examples(text)
    counts = sentence_word_counts(prose)
    words = sum(counts)
    if not counts or not words:
        return Voice(name, 0, 0, 0.0, 0, 0.0, 0.0, 0.0, 0.0)
    markers = dict(rules["voice_markers"])
    per_100 = 100 / words
    return Voice(
        name=name,
        words=words,
        sentences=len(counts),
        mean_sentence_words=words / len(counts),
        longest_sentence_words=max(counts),
        short_sentence_share=sum(1 for count in counts if count < SHORT_SENTENCE_WORDS) / len(counts),
        first_person_per_100=per_100 * count_markers(prose, list(markers["first_person"])),
        hedges_per_100=per_100 * count_markers(prose, list(markers["hedges"])),
        contrast_per_100=per_100 * sum(count_phrases(prose, list(rules["contrast_phrases"])).values()),
    )


def answers_by_register(samples: str) -> dict[str, str]:
    """Split the samples file into the answers under each of its headings, dropping the questions.

    Args:
        samples: The whole writing-samples.md file.

    Returns:
        Each register heading mapped to the answers written under it, in file order.
    """
    answers: dict[str, list[str]] = {}
    register = ""
    for line in samples.splitlines():
        heading = REGISTER_HEADING.match(line)
        if heading:
            register = heading.group(1)
            answers.setdefault(register, [])
            continue
        if register and line.strip() and not CHECKBOX.match(line):
            answers[register].append(line)
    return {name: "\n".join(lines) for name, lines in answers.items() if lines}


def format_table(voices: list[Voice]) -> str:
    """Lay the measurements out as a markdown table, in the column order of the style guide."""
    header = (
        "| Passage | Words | Sentences | Words per sentence | Longest | Under 9 words | "
        "First person | Hedges | Contrast |\n|---|---|---|---|---|---|---|---|---|"
    )
    rows = [
        f"| {voice.name} | {voice.words} | {voice.sentences} | {voice.mean_sentence_words:.1f} | "
        f"{voice.longest_sentence_words} | {voice.short_sentence_share:.0%} | "
        f"{voice.first_person_per_100:.1f} | {voice.hedges_per_100:.1f} | {voice.contrast_per_100:.1f} |"
        for voice in voices
    ]
    return "\n".join([header, *rows])


def voices_in(paths: list[str], by_register: bool, rules: dict[str, Any]) -> list[Voice]:
    """Measure each file named on the command line, split by heading when that is asked for.

    Args:
        paths: The files to measure.
        by_register: True to split each file by its headings and add a row for the whole of it.
        rules: The rules the word lists come from.

    Returns:
        One measurement per file, or one per heading plus one for each whole file.
    """
    voices: list[Voice] = []
    for path in paths:
        text = Path(path).read_text(encoding="utf-8")
        if not by_register:
            voices.append(measure(path, text, rules))
            continue
        registers = answers_by_register(text)
        voices.extend(measure(name, body, rules) for name, body in registers.items())
        voices.append(measure("All of it together", "\n".join(registers.values()), rules))
    return voices


def main() -> int:
    """Print the table for the files named on the command line."""
    arguments = sys.argv[1:]
    paths = [argument for argument in arguments if argument != REGISTERS_FLAG]
    if not paths:
        print(f"usage: measure_voice.py [{REGISTERS_FLAG}] FILE...", file=sys.stderr)
        return 2
    rules = read_rules(opt_in_file(Path.cwd()))
    print(format_table(voices_in(paths, REGISTERS_FLAG in arguments, rules)))
    return 0


if __name__ == "__main__":
    sys.exit(main())
