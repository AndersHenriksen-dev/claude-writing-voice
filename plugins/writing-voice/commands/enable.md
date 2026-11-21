---
description: Turn the writing voice on for the repo being worked in.
---

Write the two characters `{}` to `.claude/writing-voice.json` in the root of the repo being worked in, creating
the `.claude` directory if it is not there yet.

If that file already exists, leave it exactly as it is and say what it currently holds.

Then say in one line that every markdown write in this repo is checked from now on, that any threshold can be
overridden for this repo alone by putting it in that file, and that deleting the file turns the whole thing off
again.
