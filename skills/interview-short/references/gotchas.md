# Failures already hit, and their fixes

| Symptom | Cause | Fix (already in the scripts unless noted) |
|---|---|---|
| Cuts clip the first word or leak the previous one | Whisper token offsets run 0.3–0.5 s early | DTW word times (`--dtw large.v3.turbo -nfa`); `probe_cut.sh` + `FORCE` for stubborn edges |
| Whole-short transcript skips lines or invents words | Whisper on jump cuts | Verify with `check_clips.sh` (each clip alone) |
| `--dtw` gives `t_dtw = -1` | Flash attention on | Pass `-nfa` |
| ffmpeg has no `drawtext` / `subtitles` | Homebrew build without freetype/libass | PIL caption cards for the preview; AE text layers for the final |
| One frame of the previous camera shot flashes as a graphic ends | Timeline built from container durations (audio a few ms longer per clip), drifting 0.6 s | Whole-frame clips with audio trimmed to match; timeline from frame counts |
| AE renders the camera plate black | Footage file replaced in place; AE serves its cache | New `plate-N.mp4` per cut |
| First frames of a cutaway are blank paper | Elements pop in from 0 % a few frames after the cut | Elements in the first 0.15 s land on frame 0 at 85 % / part-drawn |
| A stamp is visible for the whole scene | Two keyframes 0.01 s apart merged after frame snapping | Hold key one frame before the slam (see the FIRED stamp) |
| Captions look merged in thumbnails | Black outline between letters at small scale | Check at full resolution; outline is a separate layer under the fill |
| AE script errors "Can not set expression" / null property | Effect params by index or display name | matchNames (graphics.md §7) |
| `Error Code: 9988`, "An output module failed", "Disk Full" | Disk full; AE's disk cache grew to 31 GB | Ask Michael to empty AE's disk cache (Settings → Media & Disk Cache); `run_ae.sh` warns under 8 GB free. Never delete it yourself |
| `rm` of a relative glob after `cd` is blocked | Harness safety check | Don't clean up that way; outputs are overwritten anyway |
| `while read …; ffmpeg …` loop processes one line | ffmpeg eats stdin | `ffmpeg -nostdin` |
| Mix peaks above 0 dBFS; loudnorm won't stay linear | SFX transients | Limiter before loudnorm (`master.py`) |
| SFX stem shows speech, nonsense levels | Render audio offset ~21 ms by AAC | `sfxcheck.py` aligns by cross-correlation first |
| Can't browse Artlist | Agent browsers can't sign in; Work Chrome profile blocks AppleScript JS | Codex + the brief (sfx.md) |
