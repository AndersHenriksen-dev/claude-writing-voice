---
description: Measure markdown against the numbers in the writing voice.
argument-hint: "[--registers] [files...]"
---

Measure the files given in $ARGUMENTS, from the root of the repo being worked in:

```powershell
uv run --no-project python "${CLAUDE_PLUGIN_ROOT}/scripts/measure_voice.py" $ARGUMENTS
```

Print the table as it comes back, then say in a line or two where each file sits against the target in the guide
skill, which is about 29 words a sentence with almost nothing under nine words. Pass `--registers` when a file
holds sample answers under headings, since that splits the numbers by heading instead of averaging a file that
mixes several kinds of writing into one row.
