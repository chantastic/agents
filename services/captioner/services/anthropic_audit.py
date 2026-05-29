#!/usr/bin/env python3
"""LLM terminology audit for captioner using Anthropic + 1Password key."""

import argparse, json, os, re, sys, urllib.error, urllib.request
from credentials import anthropic_key

MODEL = "claude-sonnet-4-5-20250929"


def compact_transcript(data):
    lines = []
    for i, u in enumerate(data.get('utterances') or []):
        lines.append(f"[{i}] {u.get('start'):.2f}-{u.get('end'):.2f} {u.get('transcript','')}")
    return "\n".join(lines)


def prompt(transcript_path, data, topic, glossary):
    return f"""You are auditing a Deepgram transcript for contextual noun/terminology transcription errors.

Return ONLY valid JSON matching this shape:
{{
  "version":"1.0",
  "source":{{"path":"{transcript_path}","format":"deepgram-json","duration":number}},
  "context":{{"topic":string,"glossary":[string]}},
  "model":{{"provider":"anthropic","name":"{MODEL}","reasoning":true,"temperature":0.1}},
  "summary":{{"accepted_count":number,"needs_review_count":number,"rejected_or_ignored_count":number,"notes":string}},
  "accepted":[correction],
  "needs_review":[correction],
  "rejected_or_ignored":[]
}}

Correction object:
{{"id":"corr_001","start":number,"end":number,"location":{{"kind":"utterance","utterance_index":number,"word_start_index":number,"word_end_index":number}},"original":string,"corrected":string,"category":"company_name|product_name|project_name|person_name|technical_term|acronym|capitalization|spacing_punctuation|other","confidence":0-1,"evidence":[string],"reason":string,"apply":true}}

Rules:
- Correct terminology, names, acronyms, product/company/project names, technical phrases.
- Do NOT fix grammar, fillers, repetitions, or style.
- Prefer false negatives over false positives.
- Use Deepgram utterance indexes shown below.
- Include word_start_index/word_end_index only when obvious from the utterance; otherwise omit them.
- Do not include no-op corrections where original == corrected.
- Put uncertain items in needs_review with apply=false.

Topic: {topic or '(infer from filename/transcript)'}
Glossary: {', '.join(glossary) if glossary else '(infer conservatively)'}

Transcript:
{compact_transcript(data)}
"""


def parse_json_text(text):
    text = (text or "").strip()
    if text.startswith("```"):
        text = re.sub(r"^```(?:json)?\s*", "", text)
        text = re.sub(r"\s*```$", "", text).strip()
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        start, end = text.find("{"), text.rfind("}")
        if start >= 0 and end > start:
            return json.loads(text[start:end + 1])
        raise


def call_anthropic(user_prompt):
    body = {
        "model": MODEL,
        "max_tokens": 12000,
        "temperature": 0.1,
        "messages": [{"role":"user","content":user_prompt}],
    }
    req = urllib.request.Request("https://api.anthropic.com/v1/messages", data=json.dumps(body).encode(), method="POST", headers={
        "x-api-key": anthropic_key(),
        "anthropic-version": "2023-06-01",
        "content-type": "application/json",
    })
    try:
        with urllib.request.urlopen(req, timeout=900) as resp:
            raw = resp.read().decode()
    except urllib.error.HTTPError as e:
        detail = e.read().decode(errors="replace")
        raise RuntimeError(f"Anthropic HTTP {e.code}: {detail}") from e
    out = json.loads(raw)
    text_blocks = []
    for block in out.get("content", []):
        if block.get("type") == "text":
            text_blocks.append(block.get("text", ""))
    text = "".join(text_blocks).strip()
    if not text:
        raise RuntimeError(f"Anthropic returned no text content. stop_reason={out.get('stop_reason')} raw={raw[:1000]}")
    try:
        return parse_json_text(text)
    except json.JSONDecodeError as e:
        debug_path = "/tmp/captioner-anthropic-response.txt"
        open(debug_path, "w").write(text)
        raise RuntimeError(f"Anthropic response was not valid JSON. Saved text to {debug_path}. First 500 chars: {text[:500]!r}") from e


def main():
    ap = argparse.ArgumentParser(description='Audit Deepgram transcript terminology with Anthropic')
    ap.add_argument('transcript')
    ap.add_argument('-o','--output', required=True)
    ap.add_argument('--topic', default='')
    ap.add_argument('--glossary', default='', help='Comma-separated terms')
    args = ap.parse_args()
    data = json.load(open(args.transcript))
    glossary = [x.strip() for x in args.glossary.split(',') if x.strip()]
    audit = call_anthropic(prompt(args.transcript, data, args.topic, glossary))
    with open(args.output, 'w') as f:
        json.dump(audit, f, indent=2); f.write('\n')
    print(f"wrote: {args.output}", file=sys.stderr)

if __name__ == '__main__': main()
