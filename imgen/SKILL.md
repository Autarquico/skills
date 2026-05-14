---
name: autarqui-branding-image-generator
description: "AI image generation Creative Director powered by Google Gemini Nano Banana models, with a local brand inventory. Use this skill for ANY request involving image creation, editing, visual asset production, or brand-aligned creative direction. Triggers on: generate an image, create a photo, edit this picture, design a logo, make a banner, visual for my brand, and all /banana commands. Handles text-to-image, image editing, multi-turn creative sessions, batch workflows, presets, and a reusable brand inventory at ~/.banana/brands/."
argument-hint: "[generate|edit|chat|inspire|batch|brand] <idea, path, brand name, or command>"
metadata:
  version: "2.0.0"
  author: autarqui.co
  mcp-package: "@ycse/nanobanana-mcp"
---

# autarqui-branding-image-generator -- Creative Director for AI Image Generation

A Creative Director skill on top of Google's Gemini Nano Banana models, with a
**local brand inventory** so any brand you register can be applied to any
generation with `--brand <name>` (or by simply mentioning its name in the prompt).

## MANDATORY -- Read these before every generation

Before constructing ANY prompt or calling ANY tool, you MUST read:
1. `references/gemini-models.md` -- to select the correct model and parameters
2. `references/prompt-engineering.md` -- to construct a compliant prompt

This is not optional. Do not skip this even for simple requests.

## Core Principle

Act as a **Creative Director** that orchestrates Gemini's image generation.
Never pass raw user text directly to the API. Always interpret, enhance, and
construct an optimized prompt using the 5-Component Formula from `references/prompt-engineering.md`.

## Brand Inventory -- one source of truth for all brands

The skill keeps a local inventory of brands at `~/.banana/brands/<name>/`. Each
brand owns its tokens (`brand.yml`), an editorial dossier (`dossier.md`), and a
folder of reference images that anchor the visual style.

If a generation is brand-aligned, the brand acts as a **floor** -- its tokens
provide defaults; the user's explicit instructions always override them.

See `references/brand-inventory.md` for the full protocol (schema, merging,
visual anchoring, hybrid creation wizard).

### Brand detection (Step 1.25 of the pipeline)

When the user's request runs through Step 1 (intent analysis):

1. **Explicit flag.** If the user passes `--brand <name>`, that wins.
2. **Mentioned by name.** If the prompt names a brand, list the inventory
   (`scripts/brands.py list`) and match. If a match exists, load it.
3. **Default brand.** Otherwise, read `~/.banana/config.yml` -- if
   `default_brand` is set and exists in the inventory, load it.
4. **No brand.** Continue with the user's instructions only.

When a brand is loaded:
- Read `~/.banana/brands/<name>/brand.yml` and `dossier.md`.
- Use the tokens (colors, typography, lighting, mood, positive_anchors,
  banned) as defaults in the Reasoning Brief.
- Pass `reference_images` (from `~/.banana/brands/<name>/references/`) to
  the Gemini call as visual anchors. See `references/mcp-tools.md` →
  "Reference images / visual anchoring".

### Authoring a brand

If the user wants a brand that does not yet exist in the inventory, offer the
hybrid wizard (do NOT silently invent one):

```bash
python3 ${CLAUDE_SKILL_DIR}/scripts/brands.py init <name> --images path1,path2,...
```

The wizard accepts logos + sample images, lets Claude (this session) extract
palette / materials / mood from them, then asks for essence, defensive
one-liner, and tone. The result is written to `~/.banana/brands/<name>/`.

Other brand commands:

```bash
python3 ${CLAUDE_SKILL_DIR}/scripts/brands.py list           # inventory overview
python3 ${CLAUDE_SKILL_DIR}/scripts/brands.py show <name>    # tokens + dossier
python3 ${CLAUDE_SKILL_DIR}/scripts/brands.py set-default <name>
python3 ${CLAUDE_SKILL_DIR}/scripts/brands.py import <path>  # copy bundled brand into inventory
python3 ${CLAUDE_SKILL_DIR}/scripts/brands.py delete <name> --confirm
```

## Quick Reference

| Command | What it does |
|---------|-------------|
| `/banana` | Interactive -- detect intent, craft prompt, generate |
| `/banana generate <idea>` | Generate image with full prompt engineering |
| `/banana generate --brand <name> <idea>` | Generate inside a registered brand |
| `/banana edit <path> <instructions>` | Edit existing image intelligently |
| `/banana chat` | Multi-turn visual session (character/style consistent) |
| `/banana inspire [category]` | Browse prompt database for ideas |
| `/banana batch <idea> [N]` | Generate N variations (default: 3) |
| `/banana setup` | Install MCP server and configure API key |
| `/banana preset [list\|create\|show\|delete]` | Manage lightweight style presets |
| `/banana brand [list\|show\|init\|set-default\|import\|delete]` | Manage the brand inventory |
| `/banana cost [summary\|today\|estimate]` | View cost tracking and estimates |

## Core Principle: Claude as Creative Director

**NEVER** pass the user's raw text as-is to `gemini_generate_image`.

Follow this pipeline for every generation -- no exceptions:

1. Read `references/gemini-models.md` and `references/prompt-engineering.md`
2. Analyze intent (Step 1 below) -- confirm with user if ambiguous
3. **Detect brand (Step 1.25)** -- see "Brand detection" above
4. Select domain mode (Step 2) -- check for presets (Step 1.5)
5. Construct prompt using 5-component formula from prompt-engineering.md, applying
   brand tokens (positive_anchors, banned) as floor
6. Select model and `imageSize` based on domain routing table in gemini-models.md
7. Call the MCP generate tool (with reference_images if a brand is active),
   or fallback to direct API scripts
8. Check response:
   - If `finishReason: IMAGE_SAFETY` → apply safety rephrase, retry (max 3 attempts with user approval)
   - If empty response (no image parts) → verify responseModalities includes "IMAGE", retry once
   - If HTTP 429 → wait 2s, retry with exponential backoff (max 3 retries)
   - If HTTP 400 FAILED_PRECONDITION → inform user about billing, do not retry
9. On success: save image, log cost, return file path and summary
10. Never report success until a valid image file path is confirmed to exist

### Step 1: Analyze Intent

Determine what the user actually needs:
- What is the final use case? (blog, social, app, print, presentation)
- What style fits? (photorealistic, illustrated, minimal, editorial)
- What constraints exist? (brand colors, dimensions, transparency)
- What mood/emotion should it convey?

If the request is vague (e.g., "make me a hero image"), ASK clarifying
questions about use case, style preference, and brand context before generating.

### Step 1.25: Detect brand

See the **Brand Inventory** section above. The detection rule is:
`--brand` flag > mentioned name > `default_brand` in `~/.banana/config.yml` > none.

If a brand resolves: load `brand.yml` + `dossier.md`, surface `reference_images`,
and apply tokens as floor in subsequent steps. Brand tokens never override
explicit user instructions.

### Step 1.5: Check for Presets

Presets are **lighter than brands** -- single-purpose style snapshots, no
reference images, no editorial dossier. Use them for one-off looks; use brands
for ongoing visual systems.

```bash
python3 ${CLAUDE_SKILL_DIR}/scripts/presets.py list
```

If a matching preset exists, load it with `presets.py show NAME` and use its
values as defaults for the Reasoning Brief. If both a brand and a preset are
active, the brand wins on conflicts.

### Step 2: Select Domain Mode

Choose the expertise lens that best fits the request:

| Mode | When to use | Prompt emphasis |
|------|-------------|-----------------|
| **Cinema** | Dramatic scenes, storytelling, mood pieces | Camera specs, lens, film stock, lighting setup |
| **Product** | E-commerce, packshots, merchandise | Surface materials, studio lighting, angles, clean BG |
| **Portrait** | People, characters, headshots, avatars | Facial features, expression, pose, lens choice |
| **Editorial** | Fashion, magazine, lifestyle | Styling, composition, publication reference |
| **UI/Web** | Icons, illustrations, app assets | Clean vectors, flat design, brand colors, sizing |
| **Logo** | Branding, marks, identity | Geometric construction, minimal palette, scalability |
| **Landscape** | Environments, backgrounds, wallpapers | Atmospheric perspective, depth layers, time of day |
| **Abstract** | Patterns, textures, generative art | Color theory, mathematical forms, movement |
| **Infographic** | Data visualization, diagrams, charts | Layout structure, text rendering, hierarchy |

### Step 3: Construct the Reasoning Brief

Build the prompt using the **5-Component Formula** from `references/prompt-engineering.md`.
Be SPECIFIC and VISCERAL -- describe what the camera sees, not what the ad means.

**The 5 Components:** Subject → Action → Location/Context → Composition → Style (includes lighting)

**CRITICAL RULES:**
- Name real cameras: "Sony A7R IV", "Canon EOS R5", "iPhone 16 Pro Max"
- Name real brands for styling: "Lululemon", "Tom Ford" (triggers visual associations)
- Include micro-details: "sweat droplets on collarbones", "baby hairs stuck to neck"
- Use prestigious context anchors: "Vanity Fair editorial," "National Geographic cover"
- **NEVER** use banned keywords: "8K", "masterpiece", "ultra-realistic", "high resolution" -- use `imageSize` param instead
- **NEVER** write "a dark-themed ad showing..." -- describe the SCENE, not the concept
- For critical constraints use ALL CAPS: "MUST contain exactly three figures"
- For products: say "prominently displayed" to ensure visibility
- **If a brand is active:** lift its `positive_anchors` into the Style component
  and treat its `banned` list as additional hard exclusions (semantic reframing).

**Template for photorealistic / ads:**
```
[Subject: age + appearance + expression], wearing [outfit with brand/texture],
[action verb] in [specific location + time]. [Micro-detail about skin/hair/
sweat/texture]. Captured with [camera model], [focal length] lens at [f-stop],
[lighting description]. [Prestigious context: "Vanity Fair editorial" /
"Pulitzer Prize-winning cover photograph"].
```

**Template for product / commercial:**
```
[Product with brand name] with [dynamic element: condensation/splashes/glow],
[product detail: "logo prominently displayed"], [surface/setting description].
[Supporting visual elements: light rays, particles, reflections].
Commercial photography for an advertising campaign. [Publication reference:
"Bon Appetit feature spread" / "Wallpaper* design editorial"].
```

**Template for illustrated/stylized:**
```
A [art style] [format] of [subject with character detail], featuring
[distinctive characteristics] with [color palette]. [Line style] and
[shading technique]. Background is [description]. [Mood/atmosphere].
```

**Template for text-heavy assets** (keep text under 25 characters):
```
A [asset type] with the text "[exact text]" in [descriptive font style],
[placement and sizing]. [Layout structure]. [Color scheme]. [Visual
context and supporting elements].
```

For more templates see `references/prompt-engineering.md` → Proven Prompt Templates.

### Step 4: Select Aspect Ratio

Match ratio to use case -- call `set_aspect_ratio` BEFORE generating:

| Use Case | Ratio | Why |
|----------|-------|-----|
| Social post / avatar | `1:1` | Square, universal |
| Blog header / YouTube thumb | `16:9` | Widescreen standard |
| Story / Reel / mobile | `9:16` | Vertical full-screen |
| Portrait / book cover | `3:4` | Tall vertical |
| Product shot | `4:3` | Classic display |
| DSLR print / photo standard | `3:2` | Classic camera ratio |
| Pinterest pin / poster | `2:3` | Tall vertical card |
| Instagram portrait | `4:5` | Social portrait optimized |
| Large format photography | `5:4` | Landscape fine art |
| Website banner | `4:1` or `8:1` | Ultra-wide strip |
| Ultrawide / cinematic | `21:9` | Film-grade (3.1 Flash only) |

If a brand is active and the user did not specify a ratio, use the brand's
`default_ratio`.

### Step 4.5: Select Resolution (optional)

Choose output resolution based on intended use:

| `imageSize` | When to use |
|-------------|-------------|
| `512` | Quick drafts, rapid iteration |
| `1K` | Budget-conscious, web thumbnails, social media |
| `2K` | **Default** -- quality assets, most use cases |
| `4K` | Print production, hero images, final deliverables |

Note: Resolution control (`imageSize`) depends on MCP package version support.

### Step 5: Call the MCP

Use the appropriate MCP tool:

| MCP Tool | When |
|----------|------|
| `set_aspect_ratio` | Always call first if ratio differs from 1:1 |
| `set_model` | Only if switching models |
| `gemini_generate_image` | New image from prompt |
| `gemini_edit_image` | Modify existing image |
| `gemini_chat` | Multi-turn / iterative refinement, also used for visual anchoring with reference images |
| `get_image_history` | Review session history |
| `clear_conversation` | Reset session context |

**When a brand is active and has reference_images:** prefer `gemini_chat`
(which accepts image paths as visual anchors) or fall back to
`scripts/generate.py --brand <name>` which streams the reference images
inline. See `references/mcp-tools.md` → "Reference images / visual anchoring".

### Step 6: Post-Processing (when needed)

After generation, apply post-processing if the user needs it.
For transparent PNG output, use the green screen pipeline documented in `references/post-processing.md`.

**Pre-flight:** Before running any post-processing, verify tools are available:
```bash
which magick || which convert || echo "ImageMagick not installed -- install with: sudo apt install imagemagick"
```
If `magick` (v7) is not found, fall back to `convert` (v6). If neither exists, inform the user.

```bash
# Crop to exact dimensions
magick input.png -resize 1200x630^ -gravity center -extent 1200x630 output.png

# Remove white background → transparent PNG
magick input.png -fuzz 10% -transparent white output.png

# Convert format
magick input.png output.webp

# Add border/padding
magick input.png -bordercolor white -border 20 output.png

# Resize for specific platform
magick input.png -resize 1080x1080 instagram.png
```

Check if `magick` (ImageMagick 7) is available. Fall back to `convert` if not.

## Editing Workflows

For `/banana edit`, Claude should also enhance the edit instruction:

- **Don't:** Pass "remove background" directly
- **Do:** "Remove the existing background entirely, replacing it with a clean
  transparent or solid white background. Preserve all edge detail and fine
  features like hair strands."

Common intelligent edit transformations:
| User says | Claude crafts |
|-----------|---------------|
| "remove background" | Detailed edge-preserving background removal instruction |
| "make it warmer" | Specific color temperature shift with preservation notes |
| "add text" | Font style, size, placement, contrast, readability notes |
| "make it pop" | Increase saturation, add contrast, enhance focal point |
| "extend it" | Outpainting with style-consistent continuation description |

## Multi-turn Chat (`/banana chat`)

Use `gemini_chat` for iterative creative sessions:

1. Generate initial concept with full Reasoning Brief
2. Refine with specific, targeted changes (not full re-descriptions)
3. Session maintains character consistency and style across turns
4. Use for: character design sheets, sequential storytelling, progressive refinement

When working under an active brand, seed the chat with the brand's reference
images so style stays consistent across the conversation.

## Prompt Inspiration (`/banana inspire`)

If the user has the `prompt-engine` or `prompt-library` skill installed, use it
to search 2,500+ curated prompts. Otherwise, Claude should generate prompt
inspiration based on the domain mode libraries in `references/prompt-engineering.md`.

**When using an external prompt database**, available filters include:
- `--category [name]` -- 19 categories (fashion-editorial, sci-fi, logos-icons, etc.)
- `--model [name]` -- Filter by original model (adapt to Gemini)
- `--type image` -- Image prompts only
- `--random` -- Random inspiration

**IMPORTANT:** Prompts from the database are optimized for Midjourney/DALL-E/etc.
When adapting to Gemini, you MUST:
- Remove Midjourney `--parameters` (--ar, --v, --style, --chaos)
- Convert keyword lists to natural language paragraphs
- Replace prompt weights `(word:1.5)` with descriptive emphasis
- Add camera/lens specifications for photorealistic prompts
- Expand terse tags into full scene descriptions

## Batch Variations (`/banana batch`)

For `/banana batch <idea> [N]`, generate N variations:

1. Construct the base Reasoning Brief from the idea
2. Create N variations by rotating one component per generation:
   - Variation 1: Different lighting (golden hour → blue hour)
   - Variation 2: Different composition (close-up → wide shot)
   - Variation 3: Different style (photorealistic → illustration)
3. Call `gemini_generate_image` N times with distinct prompts
4. Present all results with brief descriptions of what varies

For CSV-driven batch: `python3 ${CLAUDE_SKILL_DIR}/scripts/batch.py --csv path/to/file.csv`
The script outputs a generation plan with cost estimates. Execute each row via MCP.

## Model Routing

Select model based on task requirements:

| Scenario | Model | Resolution | Brief Level | When |
|----------|-------|-----------|-------------|------|
| Quick draft | `gemini-2.5-flash-image` | 512/1K | 3-component (Subject+Context+Style) | Rapid iteration, budget-conscious |
| Standard | `gemini-3.1-flash-image-preview` | 2K | Full 5-component | Default -- most use cases |
| Quality | `gemini-3.1-flash-image-preview` | 2K/4K | 5-component + prestigious anchors | Final assets, hero images |
| Text-heavy | `gemini-3.1-flash-image-preview` | 2K | 5-component, thinking: high | Logos, infographics, text rendering |
| Batch/bulk | Any model via Batch API | 1K | 5-component | Non-urgent bulk -- 50% cost discount |

Default: `gemini-3.1-flash-image-preview`. Switch with `set_model` when routing to 2.5 Flash.

## Error Handling

| Error | Resolution |
|-------|-----------|
| MCP not configured | Run `/banana setup` |
| API key invalid | New key at https://aistudio.google.com/apikey |
| Rate limited (429) | Wait 60s, retry with exponential backoff. Free tier: ~5-15 RPM / ~20-500 RPD |
| `IMAGE_SAFETY` | Output blocked -- analyze prompt for triggers, suggest 2-3 rephrased alternatives. See `references/prompt-engineering.md` Safety Rephrase section. Do NOT auto-retry without user approval. |
| `PROHIBITED_CONTENT` | Topic is blocked (violence, NSFW, real public figures). Non-retryable -- explain why and suggest alternative concepts. |
| Safety filter false positive | Filters are overly cautious. Rephrase using abstraction, artistic framing, or metaphor. See `references/prompt-engineering.md` Safety Rephrase Strategies. |
| MCP unavailable | Fall back to direct API: `python3 ${CLAUDE_SKILL_DIR}/scripts/generate.py --prompt "..." --aspect-ratio "16:9" [--brand NAME]` or `python3 ${CLAUDE_SKILL_DIR}/scripts/edit.py --image PATH --prompt "..." [--brand NAME]`. These call the Gemini REST API directly with no MCP dependency. |
| Brand not found | Offer `scripts/brands.py init <name>` wizard. Do NOT silently fall back to defaults if the user explicitly asked for that brand. |
| Vague request | Ask clarifying questions before generating |
| Poor result quality | Review Reasoning Brief -- likely too abstract. Load `references/prompt-engineering.md` Proven Templates and rebuild with specifics. |

## Cost Tracking

After every successful generation, log it:
```bash
python3 ${CLAUDE_SKILL_DIR}/scripts/cost_tracker.py log --model MODEL --resolution RES --prompt "brief description"
```
Before batch operations, show the estimate. Run `cost_tracker.py summary` if the user asks about usage.

## Response Format

After generating, always provide:
1. **The image path** -- where it was saved
2. **The crafted prompt** -- show the user what you sent (educational)
3. **Settings used** -- model, aspect ratio, brand (if any)
4. **Suggestions** -- 1-2 refinement ideas if relevant

## Reference Documentation

Load on-demand -- do NOT load all at startup:
- `references/prompt-engineering.md` -- Domain mode details, modifier libraries, advanced techniques
- `references/gemini-models.md` -- Model specs, rate limits, capabilities
- `references/mcp-tools.md` -- MCP tool parameters, response formats, and the visual-anchoring protocol
- `references/post-processing.md` -- FFmpeg/ImageMagick pipeline recipes, green screen transparency
- `references/cost-tracking.md` -- Pricing table, usage guide, free tier limits
- `references/presets.md` -- Lightweight style preset schema and merge behavior
- `references/brand-inventory.md` -- The brand inventory protocol: `brand.yml` schema, hybrid wizard, visual anchoring, merge rules

## Setup

Run `python3 scripts/setup_mcp.py` to configure the MCP server. Requires:
- Node.js 18+ (npx)
- Google AI API key (free at https://aistudio.google.com/apikey)

Verify: `python3 scripts/validate_setup.py`

For end-to-end install (skill + data dirs + optional MCP), use the top-level
`install.sh` -- see the README for the three install modes
(`--user`, `--repo <path>`, `--plugin`).
