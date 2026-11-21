---
name: guide
description: The writing voice of Anders Henriksen for markdown, with his measured sentence numbers, his opening and closing moves, and the tells that never go in. Use it only when he asks for his voice by name, or when the repo being worked in carries .claude/writing-voice.json. Never apply it to a CV, a cover letter, a job application, a blog post or any other writing where he has not asked for it.
when_to_use: When he asks to write, check or rewrite markdown in his voice, or when the repo carries .claude/writing-voice.json. Not otherwise, and never inferred from the subject matter alone.
---

<!-- writing-check: off -->

# The writing voice

This describes how one person writes, so that markdown written for him reads as though he wrote it, because he
did. The work it was built for is a playbook he has to defend in a room, where a section that sounds generated is
worse than no section, since the first thing a reader decides is whether a person thought about this at all.

## When this applies

Two cases, and no others. He has asked for his voice, naming it. Or the repo being worked in carries
`.claude/writing-voice.json`, which is how a repo opts in, and which also turns on the hook that checks every
markdown write there.

Anywhere else, leave it alone. The gate exists for the writing that already carries a voice of its own, such as a
CV, a letter or a post, where the numbers below would fight it.

## The target, measured

Counted over 23 answers he wrote by hand to questions about his work, which is 2,645 words in six kinds of
writing. The answers are his own and stay on his machine, so these numbers are what carries forward.

| What he was writing | Words per sentence | Longest | Under 9 words | First person | Hedges | Contrast |
|---|---|---|---|---|---|---|
| Deciding and defending | 28.9 | 60 | 0% | 1.9 | 3.5 | 0.2 |
| Saying no and giving bad news | 26.9 | 44 | 0% | 3.5 | 2.4 | 0.0 |
| Explaining it to someone outside the work | 29.4 | 52 | 0% | 2.1 | 1.1 | 0.2 |
| Short forms, such as a chat message | 24.0 | 46 | 23% | 7.1 | 1.3 | 0.0 |
| Himself, what he enjoys and where he was wrong | 31.4 | 57 | 0% | 7.4 | 2.2 | 0.0 |
| Describing how something works | 35.8 | 73 | 0% | 8.1 | 0.8 | 0.0 |
| All of it together | 29.1 | 73 | 3% | 4.7 | 1.9 | 0.1 |

The last three columns are counts per 100 words, from the word lists in `writing_rules.json` at the plugin root,
and bold spans are zero in every register.

Sentences stay long whatever he writes about, and the floor across the six registers is 24 words in a chat
message, so a passage averaging under about 22 words a sentence is not his however clean it reads. Nothing is
clipped either, since five of the six registers hold no sentence under nine words at all, and the 3 per cent
overall comes from a chat message opening with hello everyone and an interview answer opening with his name. The
first person is the column that moves, at about 2 per 100 words about the company and about 7 to 8 about himself
or about how something works, so a passage on his work with no I in it has lost something he would notice.

The hook complains under 16 words a sentence, above 30 per cent of sentences under nine words, above two bolded
spans and on any line that opens with one. Those numbers are the outer edge of writing he would disown, and not
this table, so a file can clear every rule and still be nowhere near his voice.

## How the sentences are built

Long sentences that join their clauses with and, so, since, given that and such that, where the reason sits in the
same sentence as the thing it explains. Clauses join with and 84 times and with so 20 times across the 23 answers,
against four becauses, one colon and no semicolons at all. Where a generated passage reaches for punctuation or
for a contrast, he adds another clause and keeps going.

First person, with the intent in it: I will, I would rather, I want to avoid. Hedges stay in, because the
uncertainty is real and sanding it off makes a claim he cannot defend. Tools get named as he would say them out
loud, such as power automate, excel or a python program. Examples are concrete and sometimes a bit odd, like the
piece of cardboard with the buttons drawn on it, and they are his rather than invented to fit the sentence.

Where he has no experience, the text says so. That is more useful to a reader than a confident paragraph covering
a hole, and it is the one thing an agent cannot write on his behalf.

## How a piece opens and closes

Thirteen of the 23 answers open with I. Of the twelve written to another person, seven open in that person's world
instead of his own, with their good work, their scepticism, the result their team got, the disagreement stated
neutrally, or something they already know, and his argument follows from there. Where the question was a yes or no
from a board member, the answer is the first word of the reply.

Nothing closes on a line that sounds good. The closing sentences run to a median of 27 words, and exactly one of
the 23 comes in under nine words. Seven answers end by handing the next move to the reader as an offer or a
question, such as do let me know what works for you, or can I book you for a meeting. Five more end on the
consequence of what was just said with a hedge inside it, such as this means that my work is probably 15 times
faster. Two end on a bracketed aside to the reader.

## The words he reaches for

Efficiency and ensure, eight times each in the 23 answers, over time seven times, as possible six times and value
five. Unfortunately is how bad news opens, four times. Super is an intensifier he uses in earnest, as in super
proud and super promising, and so are extremely, really and teeny-tiny. Given that and such that carry the
reasoning, three times each. I would is how he states a position, ten times over, and I want to make it clear is
how he marks the part the reader has to keep.

## What never goes in

The first group is checked by the hook, and the second is on the writer.

Checked: em dashes and the double hyphen, any line that opens with a bolded term, more than two bolded spans in a
file, the word list in `writing_rules.json` (delve, leverage, robust, crucial, seamless, moreover, furthermore,
additionally, worth noting, that said, at the end of the day, truly, genuinely, and the rest), sentences that
average under sixteen words, and more than three in ten sentences coming in under nine words.

Not checked, and more important:

- Aphorisms as paragraph closers. "A review that never stops anything is not a review." The shape does the
  persuading instead of the evidence. None of his own 23 closers is one of these.
- Invented specifics. Numbers, cadences, team counts, turnarounds and examples he never gave. A fabricated
  specific is worse than the vague phrasing it replaced, because it reads as fact. Ask him, or leave the gap
  visible.
- Invented stance. Reactions, preferences and opinions he never expressed, including the small ones ("which is
  usually more interesting than the thing that worked").
- The three-part list where he had two real items, and the second half of a contrast pair that exists only for
  balance.
- Rhetorical questions used as section transitions.
- Paragraphs that could be reordered without a reader noticing.

## Where the rules do not apply

A file that is mostly checkboxes or table rows is a checklist or a form, and the hook skips the bold and cadence
rules there. Short imperative items with a bolded lead term are the genre. Em dashes and the word list still apply
everywhere.

A file that has to quote the patterns it bans, like this one, carries the line `<!-- writing-check: off -->`. An
edit is checked as a fragment, which does not carry the first line of the file, so the hook reads the file it is
about to change and lets a fragment through when the file on disk has opted out.

## Running the checks

Both scripts live at `${CLAUDE_PLUGIN_ROOT}/scripts/` and need no virtual environment.

```powershell
uv run --no-project python "${CLAUDE_PLUGIN_ROOT}/scripts/check_markdown_writing.py" FILE.md
```

```powershell
uv run --no-project python "${CLAUDE_PLUGIN_ROOT}/scripts/measure_voice.py" FILE.md
```

The checker prints what fired for each file and exits non-zero when anything blocking did. The measuring script
prints the table above for whole files, or for each heading of a file of sample answers with `--registers`, which
is how the numbers get recounted when he writes a new batch.

## Where the rules come from

The word list and the tells are a subset of the `avoid-ai-writing` skill by Conor Bronsdon (MIT licensed), which
is a careful catalogue with its own carve-outs. The formatting rules, the word list, the never-inject list and the
aphorism and contrast patterns were kept.

Two parts of it were rejected after testing. Applied as a rewriting pass, its hedge-cutting and general tightening
pulled a passage away from his voice: average sentence length fell from 32 words to 24 against his own 29, and
hedges went from 1.9 per 100 words to zero against his own 1.3. The same passage, with only its never-inject rules
applied and the cadence left alone, came out at 27.6 words per sentence and 1.4 hedges, which is as close to his
own writing as any version got.

So the order matters. Draft in his voice first, then use the catalogue to find inventions and tells, and never let
it shorten a sentence or remove a hedge.
