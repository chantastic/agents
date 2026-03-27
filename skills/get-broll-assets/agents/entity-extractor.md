---
name: entity-extractor
description: "DEPRECATED — Entity extraction is now done directly by the LLM reading the transcript. No external NER tool needed. This file is kept for reference only."
---

# Entity Extractor (Deprecated)

Entity extraction was previously done via spaCy NER (`scripts/extract-entities.py`).

It is now done by the LLM directly reading the Deepgram transcript. The LLM is better at:
- Recognizing domain-specific entities (product names, technical terms)
- Properly casing entities (WorkOS not "work os")
- Understanding context to determine entity type
- Filtering noise (common words that happen to be capitalized)

The entity extraction instructions are in the main SKILL.md, Step 2.
