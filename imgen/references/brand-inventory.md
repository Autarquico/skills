# Brand Inventory Reference

> Load this when the user mentions a brand, asks for brand-aligned visuals,
> wants to create or manage brands, or when `--brand <name>` is passed.
>
> **Presets vs brands.** See `presets.md` for the lightweight alternative.
> Use brands when you need ongoing visual consistency, an editorial dossier,
> and visual anchoring through reference images.

## Layout

The inventory lives at `~/.banana/`:

```
~/.banana/
├── config.yml                    # { default_brand: <name|null> }
├── presets/                      # lightweight JSON presets (see presets.md)
└── brands/
    └── <name>/                   # one folder per brand, slug-safe
        ├── brand.yml             # tokens (the source of truth)
        ├── dossier.md            # editorial context for Claude
        └── references/           # logos + sample images (anchors)
            ├── logo.png
            ├── sample-01.jpg
            └── ...
```

## `brand.yml` schema

```yaml
name: my-brand                    # slug (a-z, 0-9, hyphen, underscore)
essence: "Single defensive sentence describing what the brand stands for."
colors:
  - "#000000"
  - "#FFFFFF"
typography:
  headline: "serif with fluid stroke"
  body: "geometric sans-serif"
materials:
  - "matte paper"
  - "raw concrete"
  - "linen"
lighting: "soft directional window light, overcast diffusion"
mood: "calm, considered, inevitable"
positive_anchors:                  # lifted into Style component
  - "Apple Newsroom product photography"
  - "Stripe Press book cover"
banned:                            # extra semantic exclusions for this brand
  - "gradient"
  - "neon"
  - "glassmorphism"
  - "HUD"
  - "robot hand"
default_ratio: "4:3"
default_resolution: "2K"
reference_images:                  # paths relative to ./references/
  - "logo.png"
  - "sample-01.jpg"
```

All fields are optional except `name` and `essence`. Missing fields fall back
to the global defaults from SKILL.md / prompt-engineering.md.

## Loading flow (what Claude does at Step 1.25)

1. Resolve a brand from: `--brand` flag → name mentioned in prompt → `default_brand`.
2. If a brand resolves and `~/.banana/brands/<name>/brand.yml` exists, load it.
3. Optionally load `dossier.md` for deeper editorial context if the generation
   is non-trivial (logo, hero, editorial piece).
4. Merge tokens into the Reasoning Brief as **floor**:
   - `colors`, `typography`, `lighting`, `mood` → defaults for those components
   - `positive_anchors` → added to the Style component
   - `banned` → extra semantic exclusions (positive-frame the prompt away from them)
   - `default_ratio`, `default_resolution` → used if the user did not specify
5. Resolve `reference_images` to absolute paths under `~/.banana/brands/<name>/references/`.
6. Pass them to Gemini via `gemini_chat` (MCP) or `scripts/generate.py --brand`
   (REST fallback). See `mcp-tools.md` → "Reference images / visual anchoring".

## Merge rules (precedence)

When multiple sources offer values for the same Reasoning Brief component:

```
user explicit instruction  >  brand.yml  >  preset  >  domain mode defaults  >  global defaults
```

- Brand `banned` tokens are **additive** to the global banned list, not a replacement.
- Brand `positive_anchors` are **additive** to the prestigious anchors the
  domain mode would already use.
- If the user explicitly contradicts a brand value ("ignore the brand palette,
  use red"), follow the user.

## Hybrid creation wizard

`scripts/brands.py init <name> --images path1,path2,...` is a **conversational
wizard** that uses Claude's multimodal capabilities (the current session, no
extra API call) rather than calling Gemini for analysis.

Flow:

1. **Inputs.** User provides `<name>` and a list of image paths (logos,
   reference photos, mood-board snippets).
2. **Sanity check.** Script verifies images exist and the brand slug is unused.
   Copies images into `~/.banana/brands/<name>/references/`.
3. **Claude analyzes.** The skill instructs Claude (via Read on each image) to
   extract: dominant palette (hex), materials, lighting, typographic feel,
   mood adjectives. Claude proposes a draft `brand.yml`.
4. **Claude asks.** Conversational follow-ups:
   - "In one sentence, what does this brand stand for?" → `essence`
   - "What MUST NOT appear in brand visuals?" → extra `banned` entries
   - "What's the canonical aspect ratio for hero assets?" → `default_ratio`
   - "Any prestigious references you want to anchor to?" → `positive_anchors`
5. **Write.** Script writes `brand.yml` + `dossier.md` and prints the inventory
   path. Suggests running `brands.py set-default <name>` if appropriate.

The wizard never invents `essence` or `positive_anchors` -- those are author
decisions, even when Claude has plenty of visual context.

## Importing a packaged brand

`scripts/brands.py import <path-to-folder>` copies a self-contained brand
folder (`brand.yml`, optional `dossier.md`, optional `references/`) into the
inventory. The folder name becomes the slug unless `--name` overrides.

Use this to:
- Migrate a brand authored elsewhere (e.g., older `brand-<name>.md` files).
- Share a brand bundle across machines (zip the folder, unzip, import).
- Seed a fresh install with brands kept in a private repo.

## Listing / showing / deleting

```bash
brands.py list                     # one line per brand with essence
brands.py show <name>              # full brand.yml + dossier
brands.py set-default <name>       # writes ~/.banana/config.yml
brands.py delete <name> --confirm  # irreversible
```

## Anti-patterns

- **Don't put company-confidential strategy in `dossier.md`** -- Claude reads
  it on every brand-aligned generation. Keep dossiers visual/editorial.
- **Don't bloat `reference_images`** -- 3–6 images is the sweet spot. More
  than ~10 dilutes the anchor and risks payload limits.
- **Don't use a brand for a one-off color try-out** -- create a preset
  instead. Brands are for sustained visual systems.
- **Don't edit `brand.yml` by hand for hex colors casually** -- run the wizard
  on an updated image set instead, so palette and references stay coherent.
