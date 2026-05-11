# Autarquico Skills

Custom Claude Code skills, monorepo. Each subfolder is an independent skill installable in `~/.claude/skills/`.

## Available skills

### [`autarqui-video-gen`](./autarqui-video-gen)

Mini-estudio de producción de video. Composición vía Remotion, asset libraries (Pixabay/Pexels/Unsplash/Freesound), voz local (Piper/Coqui), subtítulos (Whisper.cpp), motion (GSAP/Three.js/Lottie/Manim), generación local de video con LTX-Video. **29 scenes tokenizadas, 6 visual styles, 14 demos incluidos. Cero APIs de pago.**

```bash
curl -sSL https://raw.githubusercontent.com/Autarquico/skills/main/autarqui-video-gen/scripts/quickstart.sh | bash
```

### [`autarqui-skillfactory`](./autarqui-skillfactory)

Methodology and tooling for engineering high-quality Claude Code skills. Phase-based router/creator with iterative analysis, regression questioning, evolution scoring, and multi-agent synthesis.

(Forked from SkillForge v5.1, rebranded for Autarquico internal use.)

```bash
TMP=$(mktemp -d) && git clone --depth 1 --filter=blob:none --no-checkout https://github.com/Autarquico/skills.git "$TMP" && git -C "$TMP" sparse-checkout set --cone autarqui-skillfactory && git -C "$TMP" checkout main && mkdir -p ~/.claude/skills && cp -r "$TMP/autarqui-skillfactory" ~/.claude/skills/ && rm -rf "$TMP" && echo "✓ installed at ~/.claude/skills/autarqui-skillfactory"
```

### [`autarqui-dockerfiledoc`](./autarqui-dockerfiledoc)

Dockerfile analyzer. Reviews any Dockerfile and produces an optimized, security-hardened, production-ready version with explanations covering layer efficiency, caching, base image selection, and MLOps patterns.

```bash
TMP=$(mktemp -d) && git clone --depth 1 --filter=blob:none --no-checkout https://github.com/Autarquico/skills.git "$TMP" && git -C "$TMP" sparse-checkout set --cone autarqui-dockerfiledoc && git -C "$TMP" checkout main && mkdir -p ~/.claude/skills && cp -r "$TMP/autarqui-dockerfiledoc" ~/.claude/skills/ && rm -rf "$TMP" && echo "✓ installed at ~/.claude/skills/autarqui-dockerfiledoc"
```

## Installing a skill manually

Clone the whole monorepo, copy the skill folder you want into `~/.claude/skills/`:

```bash
git clone https://github.com/Autarquico/skills.git /tmp/aq-skills
cp -r /tmp/aq-skills/<skill-name> ~/.claude/skills/
rm -rf /tmp/aq-skills
```

For skills with `scripts/install.sh` (like `autarqui-video-gen`), run it after copying.

## Adding a new skill

1. Create a subfolder named `autarqui-<name>/`
2. Add a `SKILL.md` with frontmatter (`name`, `description`, optional `license`, `model`)
3. Optionally add `scripts/`, `tools/`, assets, etc.
4. Update this README to list it
5. Commit + push

For methodology, see [`autarqui-skillfactory`](./autarqui-skillfactory).

## License

Each skill declares its own license in its `SKILL.md` frontmatter or top-level `LICENSE` file. Default for new skills: MIT.
