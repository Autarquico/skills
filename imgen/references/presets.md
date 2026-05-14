# Style Presets Reference

> Load this on-demand when the user asks about presets or quick style snapshots.
>
> **Presets vs brands.** Presets are **lightweight** -- a single JSON file with
> colors, style, typography, lighting, mood, default ratio/resolution. They
> have no reference images and no editorial dossier. Use them for one-off
> looks. For an ongoing visual system (logo, packshot, editorial), use the
> **brand inventory** at `~/.banana/brands/<name>/` instead. See
> `brand-inventory.md`.

## Preset Schema

Each preset is stored as `~/.banana/presets/NAME.json`:

```json
{
  "name": "tech-saas",
  "description": "Clean tech SaaS brand",
  "colors": ["#2563EB", "#1E40AF", "#F8FAFC"],
  "style": "clean minimal tech illustration, flat vectors, soft shadows",
  "typography": "bold geometric sans-serif",
  "lighting": "bright diffused studio, no harsh shadows",
  "mood": "professional, trustworthy, modern",
  "default_ratio": "16:9",
  "default_resolution": "2K"
}
```

## Example Presets

### tech-saas
- **Colors:** #2563EB, #1E40AF, #F8FAFC (blue + white)
- **Style:** Clean minimal tech illustration, flat vectors, soft shadows
- **Typography:** Bold geometric sans-serif
- **Mood:** Professional, trustworthy, modern

### luxury-brand
- **Colors:** #1A1A1A, #C9A96E, #FAFAF5 (black + gold + cream)
- **Style:** Elegant high-end photography, rich textures, deep contrast
- **Typography:** Thin elegant serif, generous letter-spacing
- **Mood:** Exclusive, sophisticated, aspirational

### editorial-magazine
- **Colors:** #000000, #FFFFFF, #FF3B30 (black + white + accent red)
- **Style:** Bold editorial photography, strong geometric composition
- **Typography:** Condensed all-caps sans-serif headlines
- **Mood:** Bold, provocative, contemporary

### minimal-restraint
- **Colors:** #000000, #FFFFFF (monochrome)
- **Style:** Apple Newsroom / Stripe Press editorial restraint, matte materials,
  generous negative space, single focal point, calm centered composition.
- **Typography:** Serif with fluid stroke (display); geometric sans-serif (body).
- **Lighting:** Soft directional window light, overcast diffusion, no drama.
- **Mood:** Calm, considered, inevitable.
- **Default ratio:** 4:3
- **Default resolution:** 2K

## How Presets Merge into Reasoning Brief

When a preset is active, Claude uses its values as defaults for the Reasoning Brief:
1. **Colors** → inform palette descriptions in Context and Style components
2. **Style** → becomes the base for the Style component
3. **Typography** → used for any text rendering
4. **Lighting** → becomes the base for the Lighting component
5. **Mood** → influences Action and Context components

User instructions always override preset values. If a user says "make it dark"
but the preset has bright lighting, follow the user's instruction.

**When a brand is also active**, the brand wins on conflicts -- presets behave
as a softer overlay.

## Managing Presets

```bash
# List presets
presets.py list

# Show details
presets.py show tech-saas

# Create interactively (Claude fills in details from conversation)
presets.py create NAME --colors "#hex,#hex" --style "..." --mood "..."

# Delete
presets.py delete NAME --confirm
```
