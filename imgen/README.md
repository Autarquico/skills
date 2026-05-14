# autarqui-branding-image-generator

> AI image generation Creative Director for Claude — powered by Google's Gemini
> Nano Banana models, with a local **brand inventory** so any brand you register
> gets reused across every generation.

**v2.0.0** · Works in **Claude Code CLI** and **Claude Desktop** · MIT License

---

## What this skill does

1. **Turns Claude into a Creative Director** for image generation. Claude
   interprets your intent, selects the right domain expertise (cinema, product,
   portrait, editorial, logo, UI, etc.), and constructs a fully optimized
   prompt using the 5-component formula before calling Gemini.
2. **Keeps a local brand inventory** at `~/.banana/brands/<name>/`. Each brand
   owns its palette, typography, materials, lighting, mood, banned tokens, and
   a folder of reference images that anchor the visual style on every call.
3. **Routes the right model** for the job: Nano Banana 2
   (`gemini-3.1-flash-image-preview`) for quality, Nano Banana original
   (`gemini-2.5-flash-image`) for budget drafts.
4. **Falls back to stdlib REST scripts** when MCP is unavailable — zero pip
   dependencies, works on any system with Python 3.8+.

---

## Quick start

This skill lives inside the [Autarquico skills monorepo](https://github.com/Autarquico/skills).
Install it with the bundled `install.sh`:

```bash
# From inside this skill folder
bash install.sh --with-mcp AIza...     # API key from aistudio.google.com/apikey
```

Then, in Claude Code or Claude Desktop:

> "Generate a hero image for a coffee brand launch — minimal editorial, soft window light"

---

## Installation

### Option A — single command (recommended)

From inside this folder (in the monorepo or wherever you cloned/copied it):

```bash
bash install.sh                          # install / update only
bash install.sh --with-mcp AIza...       # install + configure MCP
bash install.sh --uninstall              # remove from ~/.claude/skills/
```

`install.sh` copies the skill into `~/.claude/skills/autarqui-branding-image-generator/`
— the path read by **both Claude Code CLI and Claude Desktop** — creates
`~/.banana/{presets,brands}/` for the local inventory, and (with `--with-mcp`)
wires `@ycse/nanobanana-mcp` into your Claude config.

### Option B — manual copy (no installer)

The skill is a flat folder; copy it directly:

```bash
cp -r autarqui-branding-image-generator ~/.claude/skills/
mkdir -p ~/.banana/{presets,brands}
```

Then either run `setup_mcp.py` or export `GOOGLE_AI_API_KEY` (see the API key
section below).

### Option C — sparse checkout from the monorepo

If you don't want the whole monorepo locally:

```bash
TMP=$(mktemp -d) && \
  git clone --depth 1 --filter=blob:none --no-checkout https://github.com/Autarquico/skills.git "$TMP" && \
  git -C "$TMP" sparse-checkout set --cone autarqui-branding-image-generator && \
  git -C "$TMP" checkout main && \
  mkdir -p ~/.claude/skills && \
  cp -r "$TMP/autarqui-branding-image-generator" ~/.claude/skills/ && \
  rm -rf "$TMP" && \
  bash ~/.claude/skills/autarqui-branding-image-generator/install.sh
```

---

## Prerequisites

| Requirement | Why | Notes |
|---|---|---|
| **Python 3.8+** | Brand inventory CRUD, REST fallback scripts, hybrid wizard, cost tracking | **Required.** Stdlib only — no `pip install` needed. |
| Node.js **18+** | MCP server (`npx @ycse/nanobanana-mcp`) | Optional — only if you use MCP instead of (or alongside) the REST fallback. |
| `GOOGLE_AI_API_KEY` | Calls to the Gemini API | Free key at https://aistudio.google.com/apikey |
| ImageMagick (optional) | Post-processing (crop, transparent PNG, format conversion) | `magick` v7 preferred, `convert` v6 works |

### Python is required

Every command in the brand layer goes through Python: `brands.py` (CRUD +
wizard), `generate.py` / `edit.py` (REST fallback with `--brand` visual
anchoring), `presets.py`, `cost_tracker.py`, `batch.py`, `setup_mcp.py`,
`validate_setup.py`. The scripts use only the standard library, so there are
no dependencies to install — but Python itself must be on the machine.

macOS and most Linux distros ship Python 3 already. Check with:

```bash
python3 --version    # must be ≥ 3.8
```

If your output is older, or `python3` is missing, install it with **uv**
(recommended — see below) or your OS package manager.

### Recommended: use `uv` to manage Python

[`uv`](https://github.com/astral-sh/uv) is a single static binary from Astral
that installs and pins Python versions without touching the system Python. It
is the cleanest way to make sure this skill always has a working interpreter.

**Install uv (one line):**

```bash
# macOS / Linux
curl -LsSf https://astral.sh/uv/install.sh | sh

# Windows (PowerShell)
powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"

# Or via Homebrew
brew install uv
```

**Install Python through uv:**

```bash
uv python install 3.12        # any 3.8+ version works; 3.12 is a good default
uv python list                # see what's installed and where
```

uv-managed Pythons live under `~/.local/share/uv/python/` and are exposed via
shims, so `python3` in your shell will resolve to the uv version automatically
once installed.

**Run a script through uv (no venv, no install step):**

```bash
uv run --python 3.12 \
  ~/.claude/skills/autarqui-branding-image-generator/scripts/brands.py list
```

Because every script in this skill is **stdlib-only**, `uv run` is effectively
just `python3` with a guaranteed version — no PEP 723 inline metadata, no
`pyproject.toml`, no virtualenv needed.

**If you ever extend the scripts with pip deps** (we currently don't), uv also
gives you fast installs:

```bash
uv pip install <package>      # global, into the active uv-managed Python
```

### Living without Python (limited)

If Python is genuinely not available, you can still use the skill in a reduced
mode: only the **MCP path** without `--brand`. You'll lose the brand
inventory, the wizard, the REST fallback, and visual anchoring. Claude will
generate images via `gemini_generate_image` based purely on the crafted
prompt. We don't recommend this — Python is small and the brand inventory is
the point of the rewrite.

---

## Configuring the Google AI Studio API key

Every Gemini call — through MCP or through the REST fallback scripts —
needs a `GOOGLE_AI_API_KEY`. Get one (free) here:
**https://aistudio.google.com/apikey** → *Create API key*. The key starts with
`AIza...`. To exceed the free quota, enable billing on the same Google Cloud
project.

There are three ways to make the key available; the first two are the common
setup, the third is for one-off testing.

### Option A — MCP server config (recommended for daily use)

`setup_mcp.py` writes the key into Claude's MCP config (`~/.claude.json`) so
the MCP server picks it up automatically when Claude starts.

```bash
# At install time:
bash install.sh --user --with-mcp AIza...

# After installing, non-interactive:
python3 ~/.claude/skills/autarqui-branding-image-generator/scripts/setup_mcp.py --key AIza...

# Interactive (prompts for the key):
python3 ~/.claude/skills/autarqui-branding-image-generator/scripts/setup_mcp.py
```

This adds (or updates) an entry equivalent to:

```json
{
  "mcpServers": {
    "nanobanana-mcp": {
      "command": "npx",
      "args": ["-y", "@ycse/nanobanana-mcp"],
      "env": { "GOOGLE_AI_API_KEY": "AIza..." }
    }
  }
}
```

**Restart Claude Code / Claude Desktop** after this so it reloads the MCP
config.

### Option B — environment variable (for the REST fallback scripts)

`generate.py` and `edit.py` read `GOOGLE_AI_API_KEY` (or `GOOGLE_API_KEY` as
fallback) from the environment. Use this when you run the scripts directly
from a terminal — e.g. for `--brand` visual anchoring via the REST path, or
for batch jobs.

```bash
# Persistent — add to ~/.zshrc (macOS default) or ~/.bashrc
echo 'export GOOGLE_AI_API_KEY=AIza...' >> ~/.zshrc
source ~/.zshrc

# Verify
echo "$GOOGLE_AI_API_KEY"
```

Options A and B can — and usually should — **coexist**: MCP for normal
in-Claude usage, env var for terminal/script usage.

### Option C — `--api-key` flag (one-off)

```bash
python3 .../scripts/generate.py --prompt "test" --api-key AIza...
python3 .../scripts/edit.py    --image foo.png --prompt "..." --api-key AIza...
```

Useful for quick smoke tests; not recommended for normal use because the key
ends up in shell history.

### Validate

```bash
python3 ~/.claude/skills/autarqui-branding-image-generator/scripts/validate_setup.py
```

This checks that the MCP entry exists, Node and Python are reachable, the API
key resolves, and the skill directory is in place.

### Security notes

- **Do not commit the key.** If you put it in `~/.zshrc`, make sure that file
  is not tracked by a public dotfiles repo.
- On shared machines, prefer a keychain or secrets manager (macOS:
  `security add-generic-password`) and export the variable only at runtime.
- If a key leaks, **revoke it** at https://aistudio.google.com/apikey and
  generate a new one. Then re-run `setup_mcp.py --key NEW_KEY`.

---

## Basic usage

Once installed, talk to Claude naturally. The skill triggers on intent
("generate", "create an image", "design a logo", "make a banner", etc.) and
on the `/banana` command.

```text
"Generate a product hero for matte ceramic mug, soft window light, 4:3"
"Edit ~/Desktop/photo.png → remove the background and make it transparent"
"Design a minimal logo for a fintech startup, monochrome"
"Batch 5 variations of: athletic portrait, golden hour, editorial"
```

### Slash commands

```text
/banana                          interactive
/banana generate <idea>          generate from prompt
/banana generate --brand X <i>   generate inside a registered brand
/banana edit <path> <instr>      edit an existing image
/banana chat                     multi-turn visual session
/banana batch <idea> [N]         N variations (default 3)
/banana inspire [category]       browse prompt ideas
/banana setup                    install/configure MCP
/banana preset list|show|create|delete
/banana brand list|show|init|set-default|import|delete
/banana cost summary|today|estimate
```

---

## Brands (local inventory)

Brands are richer than presets: each brand has tokens, an editorial dossier,
and **reference images** that get passed to Gemini as visual anchors.

```
~/.banana/
├── config.yml              # { default_brand: <name|null> }
└── brands/
    └── my-brand/
        ├── brand.yml       # tokens (palette, materials, mood, anchors, banned)
        ├── dossier.md      # editorial context for Claude
        └── references/     # 3–6 reference images (logos, samples)
```

### Create a brand (hybrid wizard)

```bash
python3 ~/.claude/skills/autarqui-branding-image-generator/scripts/brands.py \
  init my-brand --images logo.png,packshot-01.jpg,packshot-02.jpg
```

The wizard:

1. Copies images into `~/.banana/brands/my-brand/references/`
2. Scaffolds `brand.yml` and `dossier.md`
3. Hands off to **Claude** (this session, no extra API call) to read the
   images and propose palette, materials, lighting, and mood
4. Asks you for non-derivable fields: **essence**, **banned tokens**, ratio

### Manage the inventory

```bash
brands.py list                     # one line per brand with essence
brands.py show my-brand            # full brand.yml + dossier
brands.py set-default my-brand     # used when no --brand flag is passed
brands.py import ./my-bundle/      # bring a brand folder into the inventory
brands.py delete my-brand --confirm
```

### `brand.yml` schema

```yaml
name: my-brand
essence: "One defensive sentence about what this brand stands for."
colors: ["#000000", "#FFFFFF"]
typography:
  headline: "serif with fluid stroke"
  body: "geometric sans-serif"
materials: ["matte paper", "raw concrete", "linen"]
lighting: "soft directional window light, overcast diffusion"
mood: "calm, considered, inevitable"
positive_anchors:
  - "Apple Newsroom product photography"
  - "Stripe Press book cover"
banned: ["gradient", "neon", "glassmorphism", "HUD"]
default_ratio: "4:3"
default_resolution: "2K"
reference_images: ["logo.png", "packshot-01.jpg"]
```

Full protocol (loading rules, merge precedence, visual anchoring details) is in
[`references/brand-inventory.md`](references/brand-inventory.md).

### Presets vs brands

Use a **preset** for a one-off color/style snapshot
(`~/.banana/presets/NAME.json`). Use a **brand** for an ongoing visual system
with reference images and an editorial dossier. When both are active, the
brand wins on conflicts.

---

## Compatibility

| Surface | Status | Notes |
|---|---|---|
| Claude Code CLI | ✅ | Reads `~/.claude/skills/` (or `--plugin-dir .`) |
| Claude Desktop | ✅ | Same skills directory (`~/.claude/skills/`) |
| MCP (`@ycse/nanobanana-mcp`) | ✅ | Default path. `scripts/setup_mcp.py` configures it. |
| REST fallback | ✅ | `scripts/generate.py` / `scripts/edit.py`. Stdlib only. |
| Visual anchoring (`--brand`) | ✅ | Reference images sent inline to Gemini |

---

## Active models (March 2026)

| Model | Status | Use for |
|---|---|---|
| `gemini-3.1-flash-image-preview` | **Default.** Nano Banana 2. | Quality, hero assets, full feature set |
| `gemini-2.5-flash-image` | Active. Nano Banana original. | Budget drafts, free tier |
| `gemini-3-pro-image-preview` | **DEAD** since 2026-03-09. | Do not use. |

---

## Costs

The skill logs every generation to `~/.banana/cost_log.json`:

```bash
python3 ~/.claude/skills/autarqui-branding-image-generator/scripts/cost_tracker.py summary
```

Free tier (Google AI Studio): roughly 5–15 RPM and 20–500 RPD depending on the
model. See `references/cost-tracking.md`.

---

## Development

Skill layout (flat, monorepo-style):

```
autarqui-branding-image-generator/
├── SKILL.md                                   # orchestrator
├── references/                                # load-on-demand reference docs
│   ├── brand-inventory.md
│   ├── gemini-models.md
│   ├── prompt-engineering.md
│   ├── mcp-tools.md
│   ├── presets.md
│   ├── post-processing.md
│   └── cost-tracking.md
├── scripts/                                   # CRUD + REST fallback (stdlib only)
│   ├── brands.py
│   ├── generate.py
│   ├── edit.py
│   ├── presets.py
│   ├── batch.py
│   ├── cost_tracker.py
│   ├── setup_mcp.py
│   └── validate_setup.py
├── install.sh
├── README.md
├── CHANGELOG.md
├── CITATION.cff
├── CLAUDE.md
└── LICENSE
```

To iterate locally: edit files here, then re-run `bash install.sh` to push
changes into `~/.claude/skills/`. In Claude Code, run `/reload-plugins` (or
restart Claude Desktop) to pick them up.

---

## Versioning

Version is mirrored across:

- `.claude-plugin/plugin.json` → `version`
- `skills/autarqui-branding-image-generator/SKILL.md` → `metadata.version`
- `CITATION.cff` → `version` + `date-released`
- `CHANGELOG.md` → new section per release

`marketplace.json` does **not** carry a version field (plugin.json wins per
Anthropic docs).

---

## Citation

If this skill is useful for your work:

```bibtex
@software{autarqui_branding_image_generator,
  author    = {autarqui.co},
  title     = {autarqui-branding-image-generator: Creative Director for AI image generation with local brand inventory},
  year      = {2026},
  url       = {https://github.com/<your-org>/autarqui-branding-image-generator},
  version   = {2.0.0}
}
```

---

## License

MIT — see [LICENSE](LICENSE).

Maintained by [autarqui.co](https://autarqui.co). Built on the foundation of
`banana-claude` (v1.x) by AgriciDaniel; the v2 rewrite generalizes the brand
layer into a reusable local inventory.
