# Autarquico Skills

Custom Claude Code skills, monorepo. Each subfolder is an independent skill installable in `~/.claude/skills/`.

## Available skills

### [`vidgen`](./vidgen)

Mini-estudio de producción de video. Composición vía Remotion, asset libraries (Pixabay/Pexels/Unsplash/Freesound), voz local (Piper/Coqui), subtítulos (Whisper.cpp), motion (GSAP/Three.js/Lottie/Manim), generación local de video con LTX-Video. **29 scenes tokenizadas, 6 visual styles, 14 demos incluidos. Cero APIs de pago.**

```bash
curl -sSL https://raw.githubusercontent.com/Autarquico/skills/main/vidgen/scripts/quickstart.sh | bash
```

### [`skillbuilder`](./skillbuilder)

Methodology and tooling for engineering high-quality Claude Code skills. Phase-based router/creator with iterative analysis, regression questioning, evolution scoring, and multi-agent synthesis.

(Forked from SkillForge v5.1, rebranded for Autarquico internal use.)

```bash
TMP=$(mktemp -d) && git clone --depth 1 --filter=blob:none --no-checkout https://github.com/Autarquico/skills.git "$TMP" && git -C "$TMP" sparse-checkout set --cone skillbuilder && git -C "$TMP" checkout main && mkdir -p ~/.claude/skills && cp -r "$TMP/skillbuilder" ~/.claude/skills/ && rm -rf "$TMP" && echo "✓ installed at ~/.claude/skills/skillbuilder"
```

### [`dockerfiledoctor`](./dockerfiledoctor)

Dockerfile analyzer. Reviews any Dockerfile and produces an optimized, security-hardened, production-ready version with explanations covering layer efficiency, caching, base image selection, and MLOps patterns.

```bash
TMP=$(mktemp -d) && git clone --depth 1 --filter=blob:none --no-checkout https://github.com/Autarquico/skills.git "$TMP" && git -C "$TMP" sparse-checkout set --cone dockerfiledoctor && git -C "$TMP" checkout main && mkdir -p ~/.claude/skills && cp -r "$TMP/dockerfiledoctor" ~/.claude/skills/ && rm -rf "$TMP" && echo "✓ installed at ~/.claude/skills/dockerfiledoctor"
```

### [`pm`](./pm)

Sistema PM multi-proyecto. Reconcilia specs (`docs/specs/`), GitHub Projects board y `docs/STATUS.md` vía un `.pm/config.yaml` por repo. Usa GitHub MCP + `gh` CLI. Idioma operativo: español.

**Comandos:**
- `/pm sync` — reconciliación día a día (board ← PRs, specs ← board, STATUS ← board)
- `/pm adopt` — adopta repo existente añadiendo scaffolding PM sin tocar código
- `/pm init <codename>` — crea proyecto nuevo: repo + GitHub Project + scaffolding
- `/pm spec new <slug>` — crea spec en `docs/specs/<slug>.md` desde template
- `/pm spec adopt <file.md>` — convierte markdown genérico en spec formal (interactivo)
- `/pm spec to-issue <slug>` — promueve spec draft a issue del board
- `/pm bots process` — triage de PRs de bots: merge patch/minor verdes, cierra superseded/stale
- `/pm bots review <pr>` — analiza major bump: breaking changes → call sites → spec + sub-issues

```bash
TMP=$(mktemp -d) && git clone --depth 1 --filter=blob:none --no-checkout https://github.com/Autarquico/skills.git "$TMP" && git -C "$TMP" sparse-checkout set --cone pm && git -C "$TMP" checkout main && mkdir -p ~/.claude/skills && cp -r "$TMP/pm" ~/.claude/skills/ && rm -rf "$TMP" && echo "✓ installed at ~/.claude/skills/pm"
```

### [`imgen`](./imgen)

AI image generation Creative Director powered by Google Gemini Nano Banana, with a **local brand inventory** at `~/.banana/brands/`. Register a brand once (palette, materials, reference images) and apply it to any generation with `--brand <name>`. Works in Claude Code CLI and Claude Desktop. Python stdlib only — no pip deps. Requires a free Google AI Studio API key.

```bash
TMP=$(mktemp -d) && git clone --depth 1 --filter=blob:none --no-checkout https://github.com/Autarquico/skills.git "$TMP" && git -C "$TMP" sparse-checkout set --cone imgen && git -C "$TMP" checkout main && mkdir -p ~/.claude/skills && cp -r "$TMP/imgen" ~/.claude/skills/ && rm -rf "$TMP" && bash ~/.claude/skills/imgen/install.sh && echo "✓ installed at ~/.claude/skills/imgen"
```

## Installing a skill manually

Clone the whole monorepo, copy the skill folder you want into `~/.claude/skills/`:

```bash
git clone https://github.com/Autarquico/skills.git /tmp/aq-skills
cp -r /tmp/aq-skills/<skill-name> ~/.claude/skills/
rm -rf /tmp/aq-skills
```

For skills with `scripts/install.sh` (like `vidgen`), run it after copying.

## Adding a new skill

1. Create a subfolder with a short, memorable name
2. Add a `SKILL.md` with frontmatter (`name`, `description`, optional `license`, `model`)
3. Optionally add `scripts/`, `tools/`, assets, etc.
4. Update this README to list it
5. Commit + push

For methodology, see [`skillbuilder`](./skillbuilder).

## License

Each skill declares its own license in its `SKILL.md` frontmatter or top-level `LICENSE` file. Default for new skills: MIT.
