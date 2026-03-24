#!/usr/bin/env python3
"""
Extract named entities from Whisper transcript JSON using spaCy NER.

This script parses a Whisper transcript JSON file and extracts proper nouns
(companies, products, people, locations) using spaCy's pre-trained NER model.
Falls back to regex-based extraction if spaCy is unavailable.

Usage:
    python3 extract-entities.py <transcript.json> <output.json>

Output Format:
    [{
        "name": "OpenAI",
        "type": "ORG",
        "first_mention_ms": 8120,
        "mention_count": 5,
        "relevance_score": 10,
        "context": "and then OpenAI released ChatGPT..."
    }]
"""

import json
import sys
import re
from collections import Counter, defaultdict
from pathlib import Path


def extract_entities_spacy(transcript_path: str, output_path: str) -> int:
    """Extract entities using spaCy NER (preferred method)."""
    try:
        import spacy
        # Try loading from standard location first
        try:
            nlp = spacy.load("en_core_web_sm")
        except OSError:
            # Try loading from manual download location
            model_path = Path.home() / ".spacy" / "data" / "en_core_web_sm-3.8.0" / "en_core_web_sm" / "en_core_web_sm-3.8.0"
            if model_path.exists():
                nlp = spacy.load(str(model_path))
            else:
                raise OSError(f"Model not found. Tried standard location and {model_path}")
    except (ImportError, OSError) as e:
        print(f"spaCy not available ({e}). Using fallback extraction.", file=sys.stderr)
        return extract_entities_fallback(transcript_path, output_path)

    # Read Whisper transcript
    with open(transcript_path) as f:
        data = json.load(f)

    # Handle both direct array and object with 'transcription' key
    if isinstance(data, dict) and 'transcription' in data:
        segments = data['transcription']
    elif isinstance(data, list):
        segments = data
    else:
        print("Error: Unexpected transcript format", file=sys.stderr)
        return 0

    # Extract entities with timing and context
    entity_mentions = []
    entity_first_mention = {}
    entity_contexts = defaultdict(list)

    for segment in segments:
        text = segment.get('text', '').strip()
        if not text:
            continue

        timestamp_ms = segment.get('offsets', {}).get('from', 0)

        # Process with spaCy
        doc = nlp(text)

        for ent in doc.ents:
            # Filter for relevant entity types
            if ent.label_ not in ['ORG', 'PRODUCT', 'PERSON', 'GPE', 'NORP', 'FAC', 'EVENT']:
                continue

            # Clean entity text
            entity_text = ent.text.strip()
            if len(entity_text) < 2:  # Skip single characters
                continue

            # Track entity
            entity_key = (entity_text, ent.label_)
            entity_mentions.append(entity_key)

            # Store first mention
            if entity_key not in entity_first_mention:
                entity_first_mention[entity_key] = timestamp_ms
                entity_contexts[entity_key].append(text)

    # Rank entities by frequency and relevance
    entity_counter = Counter(entity_mentions)
    ranked_entities = []

    for (name, label), count in entity_counter.most_common():
        # Calculate relevance score:
        # - Higher frequency = more relevant
        # - Longer names = more specific (likely proper nouns)
        # - Multi-word entities score higher
        word_count = len(name.split())
        relevance_score = count * word_count

        ranked_entities.append({
            'name': name,
            'type': label,
            'first_mention_ms': entity_first_mention[(name, label)],
            'mention_count': count,
            'relevance_score': relevance_score,
            'context': entity_contexts[(name, label)][0][:200]  # First 200 chars
        })

    # Sort by relevance score descending
    ranked_entities.sort(key=lambda x: x['relevance_score'], reverse=True)

    # Write output
    with open(output_path, 'w') as f:
        json.dump(ranked_entities, f, indent=2)

    print(f"Extracted {len(ranked_entities)} entities using spaCy")
    return len(ranked_entities)


def extract_entities_fallback(transcript_path: str, output_path: str) -> int:
    """Fallback: Extract entities using regex patterns."""
    # Read transcript
    with open(transcript_path) as f:
        data = json.load(f)

    # Handle both formats
    if isinstance(data, dict) and 'transcription' in data:
        segments = data['transcription']
    elif isinstance(data, list):
        segments = data
    else:
        segments = []

    # Pattern for capitalized multi-word phrases (likely proper nouns)
    # Matches "OpenAI", "ChatGPT", "San Francisco", etc.
    pattern = r'\b([A-Z][a-z]*(?:\s+[A-Z][a-z]*)*)\b'

    # Track entities
    entity_mentions = []
    entity_first_mention = {}
    entity_contexts = {}

    for segment in segments:
        text = segment.get('text', '').strip()
        if not text:
            continue

        timestamp_ms = segment.get('offsets', {}).get('from', 0)

        # Find capitalized phrases
        matches = re.findall(pattern, text)

        for match in matches:
            # Filter common words that get capitalized
            if match.lower() in {'i', 'a', 'the', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for'}:
                continue

            # Skip single letters
            if len(match) < 2:
                continue

            entity_mentions.append(match)

            if match not in entity_first_mention:
                entity_first_mention[match] = timestamp_ms
                entity_contexts[match] = text[:200]

    # Rank by frequency
    entity_counter = Counter(entity_mentions)
    ranked_entities = []

    for name, count in entity_counter.most_common():
        word_count = len(name.split())
        relevance_score = count * word_count

        ranked_entities.append({
            'name': name,
            'type': 'UNKNOWN',  # Can't determine type without NER
            'first_mention_ms': entity_first_mention[name],
            'mention_count': count,
            'relevance_score': relevance_score,
            'context': entity_contexts[name]
        })

    # Filter: keep only entities mentioned more than once or multi-word entities
    ranked_entities = [
        e for e in ranked_entities
        if e['mention_count'] > 1 or len(e['name'].split()) > 1
    ]

    # Write output
    with open(output_path, 'w') as f:
        json.dump(ranked_entities, f, indent=2)

    print(f"Extracted {len(ranked_entities)} entities using fallback method")
    return len(ranked_entities)


def main():
    if len(sys.argv) != 3:
        print("Usage: python3 extract-entities.py <transcript.json> <output.json>")
        print("\nExtracts named entities (companies, products, people) from Whisper transcript.")
        sys.exit(1)

    transcript_path = sys.argv[1]
    output_path = sys.argv[2]

    # Validate input file exists
    if not Path(transcript_path).exists():
        print(f"Error: Transcript file not found: {transcript_path}", file=sys.stderr)
        sys.exit(1)

    # Create output directory if needed
    Path(output_path).parent.mkdir(parents=True, exist_ok=True)

    # Extract entities
    count = extract_entities_spacy(transcript_path, output_path)

    if count == 0:
        print("Warning: No entities extracted. Check transcript format.", file=sys.stderr)
        sys.exit(1)

    print(f"✓ Entities saved to {output_path}")


if __name__ == "__main__":
    main()
