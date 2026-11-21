---
description: Check markdown files against the writing voice and report what fired.
argument-hint: "[files...]"
---

Run the checker over the files given in $ARGUMENTS, from the root of the repo being worked in:

```powershell
uv run --no-project python "${CLAUDE_PLUGIN_ROOT}/scripts/check_markdown_writing.py" $ARGUMENTS
```

Report what fired for each file, and for every rule that fired, quote the line or the sentence that caused it so
it can be found without searching. Leave the files alone unless a rewrite was asked for, and where a file reads
fine, say so in one line instead of explaining the rules.
