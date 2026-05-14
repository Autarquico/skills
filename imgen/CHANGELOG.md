# Changelog

All notable changes to this skill are documented here.

## [2.0.0] — 2026-05-12

Rewrite of `banana-claude` v1.4.1 into a reusable, brand-agnostic skill.

### Added
- **Local brand inventory** at `~/.banana/brands/<name>/`. Each brand carries
  `brand.yml` (tokens), `dossier.md` (editorial context), and a `references/`
  folder of anchor images.
- **`scripts/brands.py`** — CRUD for the inventory plus a hybrid `init` wizard
  that scaffolds a brand from reference images for Claude to analyze.
- **Visual anchoring** in `scripts/generate.py` and `scripts/edit.py`. With
  `--brand <name>`, reference images are sent inline to Gemini so output
  follows the brand's palette / materials / typographic feel.
- **`references/brand-inventory.md`** — full protocol (schema, merge rules,
  wizard contract, visual-anchoring guidance).
- **Three-mode installer** (`install.sh --user|--repo|--plugin`). The `--user`
  mode installs into `~/.claude/skills/` so the skill works in **Claude Code
  CLI and Claude Desktop** from the same install.
- **`--brand`** and **`--no-default-brand`** flags on the REST fallback scripts;
  `default_brand` read from `~/.banana/config.yml`.

### Changed
- **Skill renamed** from `banana` to `autarqui-branding-image-generator`. The
  `/banana` user-facing command is preserved for muscle memory.
- **SKILL.md** orchestrator rewritten: Step 1.25 is now a generic
  brand-detection step (flag → mentioned → default → none), not hardcoded to a
  specific brand.
- **`references/presets.md`** trimmed back to lightweight presets; brand-grade
  presets moved to the inventory protocol. Added a generic `minimal-restraint`
  example preset.
- **`references/prompt-engineering.md`** restraint section renamed to apply to
  any minimal / editorial brand work (no brand hardcoded).
- **`references/mcp-tools.md`** documents the visual-anchoring path (MCP via
  `gemini_chat`, REST via the fallback script).

### Removed
- Hardcoded brand defaults block (the previous "Brand Defaults -- autarqui.co"
  section in SKILL.md). Equivalent behavior is now obtained by registering a
  brand in the inventory and (optionally) setting it as default.
- `references/brand-autarqui.md` (it now lives in users' private inventory
  via `brands.py import`).
- Three `autarqui-*` example presets from `presets.md`.

### Migration

Coming from `banana-claude` v1.x with the autarqui hardcoded layer:

1. Bundle the dossier and presets into a folder with this layout:
   ```
   autarqui-bundle/
     brand.yml
     dossier.md
     references/
       logo.png
       sample-01.jpg
   ```
2. Import it once: `brands.py import ./autarqui-bundle`
3. Optional: `brands.py set-default autarqui`

The skill's behavior with `--brand autarqui` matches the v1 hardcoded
defaults.

---

## Previous history (`banana-claude` v1.x)

Maintained at https://github.com/AgriciDaniel/banana-claude — preserved as
the upstream foundation. v1.4.1 was the last release before this rewrite.
