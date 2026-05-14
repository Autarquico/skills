# CLAUDE.md — development context for autarqui-branding-image-generator

Read this when working inside this repository.

## What this repo is

A Claude **skill** + **plugin** that turns Claude into a Creative Director for
image generation on top of Google's Gemini Nano Banana models. The defining
feature is a **local brand inventory** at `~/.banana/brands/<name>/` — any
brand registered there is reusable across every generation through
`--brand <name>` or the default-brand mechanism.

Designed to run in **both Claude Code CLI and Claude Desktop** from a single
install path (`~/.claude/skills/autarqui-branding-image-generator/`).

## Repo layout

- `.claude-plugin/plugin.json` — plugin manifest
- `.claude-plugin/marketplace.json` — marketplace catalog
- `skills/autarqui-branding-image-generator/` — the skill itself
  - `SKILL.md` — orchestrator
  - `references/*.md` — load-on-demand reference docs
  - `scripts/*.py` — CRUD and REST fallback (stdlib only)
- `agents/brief-constructor.md` — subagent for prompt construction
- `install.sh` — single-command installer (modes: `--user`, `--repo`, `--plugin`)

## Model status (as of May 2026)

- `gemini-3.1-flash-image-preview` — Active default (Nano Banana 2)
- `gemini-2.5-flash-image` — Active (Nano Banana original; free tier)
- `gemini-3-pro-image-preview` — Shut down 2026-03-09. Do not use.

## How to test changes

1. **Plugin mode:** `claude --plugin-dir .`
2. **User mode:** `bash install.sh --user` (then restart Claude / `/reload-plugins`)
3. **Repo vendoring:** `bash install.sh --repo /tmp/test-skills-repo`
4. Validate scripts:
   ```bash
   python3 skills/autarqui-branding-image-generator/scripts/brands.py list
   python3 skills/autarqui-branding-image-generator/scripts/generate.py --help
   ```
5. End-to-end brand: `brands.py init test --images foo.png`, then ask Claude to
   "generate something --brand test".

## File responsibilities

| File | Purpose |
|---|---|
| `skills/autarqui-branding-image-generator/SKILL.md` | Main orchestrator. Edit to change Claude's behavior. |
| `skills/.../references/gemini-models.md` | Model roster, routing, resolution defaults. |
| `skills/.../references/prompt-engineering.md` | 5-component formula, banned keywords, restraint anchors. |
| `skills/.../references/mcp-tools.md` | MCP tool params + visual-anchoring protocol. |
| `skills/.../references/brand-inventory.md` | Inventory protocol, `brand.yml` schema, hybrid wizard. |
| `skills/.../references/presets.md` | Lightweight preset schema and merge rules. |
| `skills/.../scripts/brands.py` | CRUD for `~/.banana/brands/` + loader helpers. |
| `skills/.../scripts/generate.py` | REST fallback for generation, accepts `--brand`. |
| `skills/.../scripts/edit.py` | REST fallback for editing, accepts `--brand`. |
| `skills/.../scripts/presets.py` | CRUD for `~/.banana/presets/`. |
| `install.sh` | Single-command installer (3 modes). |

## Scripts use stdlib only

`brands.py`, `generate.py`, `edit.py`, `presets.py`, `cost_tracker.py` rely
only on Python's stdlib (`urllib.request`, `json`, `argparse`, `pathlib`,
`base64`, `mimetypes`). Do **not** add `google-genai`, `requests`, or
`PyYAML`. The custom YAML reader/writer in `brands.py` is a strict subset
sufficient for the schema; if it stops being enough, add complexity inside
that helper rather than introducing a dependency.

## Key constraints

- `imageSize` must be UPPERCASE: "1K", "2K", "4K". Lowercase fails silently.
- Gemini generates ONE image per API call. No batch parameter.
- No `negativePrompt` parameter. Use semantic reframing in the prompt and
  the brand's `banned` list.
- `responseModalities` must include "IMAGE" or the API returns text only.
- Reference images: max ~14 per request. The skill caps at 14 for generation,
  13 for editing (leaves one slot for the source image).
- NEVER use banned keywords in prompts ("8K", "masterpiece", "ultra-realistic",
  "high resolution"). Use prestigious context anchors instead.

## Versioning

Bump in ALL of these when releasing:

1. `.claude-plugin/plugin.json` → `version`
2. `skills/autarqui-branding-image-generator/SKILL.md` → `metadata.version`
3. `CITATION.cff` → `version` + `date-released`
4. README badges if present
5. New section in `CHANGELOG.md`

Do NOT add `version` to `marketplace.json` — plugin.json wins silently per
Anthropic docs.

## Plugin development notes

- `.claude-plugin/` holds ONLY `plugin.json` and `marketplace.json`.
- `skills/` and `agents/` live at plugin root, not inside `.claude-plugin/`.
- `${CLAUDE_PLUGIN_ROOT}` resolves to the plugin cache dir; use it in hooks
  and MCP configs.
- `${CLAUDE_SKILL_DIR}` is a semantic marker for script paths in SKILL.md;
  works in plugin and standalone mode.
- Relative paths (`references/`, `scripts/`) resolve relative to SKILL.md.
- Test locally with `claude --plugin-dir .` then `/reload-plugins` after edits.
- Validate with `claude plugin validate .` before releasing.
