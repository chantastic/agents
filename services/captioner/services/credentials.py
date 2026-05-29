#!/usr/bin/env python3
"""1Password-only credential helpers for captioner."""

import shutil
import subprocess

DEEPGRAM_ACCOUNT = "thechans.1password.com"
DEEPGRAM_REF = "op://Private/Deepgram API Key/credential"
ANTHROPIC_ACCOUNT = "workos.1password.com"
ANTHROPIC_REF = "op://Employee/Anthropic API Key/credential"


def read_secret(ref: str, account: str) -> str:
    if not shutil.which("op"):
        raise RuntimeError("1Password CLI `op` not found")
    result = subprocess.run(["op", "read", "--account", account, ref], capture_output=True, text=True)
    if result.returncode != 0 or not result.stdout.strip():
        err = result.stderr.strip() or "empty secret"
        raise RuntimeError(f"Could not read 1Password secret {ref}: {err}")
    return result.stdout.strip()


def deepgram_key() -> str:
    return read_secret(DEEPGRAM_REF, DEEPGRAM_ACCOUNT)


def anthropic_key() -> str:
    return read_secret(ANTHROPIC_REF, ANTHROPIC_ACCOUNT)
