# System facts

## Environment
- Keyboard is Dvorak. Key names mean Dvorak characters. "Physical" means QWERTY position.
- Terminal: Ghostty. herdr and tmux are both in use. Don't assume one or the other.
- Editor: nvim (kickstart). Browser for testing: Chrome.
- `~/Developer` projects. `~/Sites` sites. `~/internal-apps` work. `~/dotfiles` system config (stow).
- `~/.config` is its own repo. `~/.codex` belongs to Codex; don't touch it.
- Personal services: `auth.chan.dev`, `devices.chan.dev`, `captioner.chan.dev`.

## Durable system
- Installing a tool means adding it to the Brewfile or `bundle-node`, stowing, and committing. Don't ask.

## Git
- The git remote org decides whether a repo is work or personal.
- After a change, commit in logical chunks and push. Leave unrelated in-flight work alone.
- Personal repos: push to main. Work repos: open a PR.
- New repos: personal account, public.
- Remotes use SSH, never HTTPS.

## Secrets
- Fetch keys with `op`. Work account for work repos, personal otherwise.
- Never write secrets into tracked files.

## Building
- Host on Cloudflare Workers. Pushing to main auto-deploys.
- Scripts: whatever fits. Bash when simple.
- Tests guard user experience. Test what the user sees, not internals.

## Working with me
- When blocked (device unresponsive, flaky service), route around it and keep going. Report at the end.
- Dashboards: CLI/API first, then browser automation, then a Codex Computer Use handoff.
- If I repeat a request, you misunderstood it. Restate it in one line before acting.
