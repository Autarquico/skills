#!/usr/bin/env python3
"""
new_project.py — scaffold a new project workspace.

Creates:
  compositions/src/projects/<id>/
    ├── script.json          (skeleton: hero-title + closing-card placeholder)
    ├── tokens.ts            (generated from styles/<slug>.visual-style.md)
    └── Composition.tsx      (skeleton importing scenes)
  compositions/public/<id>/  (asset folder)

Then registers the project in compositions/src/Root.tsx.

Usage:
  new_project.py <id> [--style autarqui-co] [--aspect 9:16] [--duration 60] [--music <path>]
"""

import argparse
import json
import re
import shutil
import subprocess
import sys
from pathlib import Path

SKILL_DIR = Path(__file__).resolve().parents[2]
COMPOSITIONS_DIR = SKILL_DIR / "compositions"
SCRIPTS_DIR = SKILL_DIR / "scripts"


def main():
    p = argparse.ArgumentParser()
    p.add_argument("id", help="Project id (kebab-case)")
    p.add_argument("--style", default="autarqui-co")
    p.add_argument("--aspect", default="9:16", choices=["9:16", "16:9", "1:1", "4:5"])
    p.add_argument("--duration", type=int, default=60)
    p.add_argument("--fps", type=int, default=30)
    p.add_argument("--music", help="Path to music file to stage in public/<id>/")
    p.add_argument("--title", help="Human title")
    args = p.parse_args()

    project_id = args.id
    if not re.match(r"^[a-z0-9][a-z0-9-]*[a-z0-9]$", project_id):
        sys.exit(
            f"ERROR: project id must be kebab-case (lowercase letters, digits, dashes). Got: {project_id}"
        )

    project_dir = COMPOSITIONS_DIR / "src" / "projects" / project_id
    public_dir = COMPOSITIONS_DIR / "public" / project_id

    if project_dir.exists():
        sys.exit(f"ERROR: project already exists at {project_dir}")

    print(f"==> Creating project: {project_id}")
    print(f"    style:    {args.style}")
    print(f"    aspect:   {args.aspect}  ({_aspect_to_size(args.aspect)})")
    print(f"    duration: {args.duration}s @ {args.fps}fps")

    project_dir.mkdir(parents=True)
    public_dir.mkdir(parents=True)

    # 1. Copy music if provided
    music_in_public = None
    if args.music:
        src = Path(args.music).expanduser()
        if not src.exists():
            sys.exit(f"ERROR: music file not found: {src}")
        dst = public_dir / src.name
        shutil.copy(src, dst)
        music_in_public = f"{project_id}/{src.name}"
        print(f"    music:    {dst}")

    # 2. Generate tokens.ts via resolve_style.py
    tokens_path = project_dir / "tokens.ts"
    print(f"==> Resolving style → {tokens_path}")
    subprocess.run(
        [
            sys.executable,
            str(SCRIPTS_DIR / "lib" / "resolve_style.py"),
            "--slug",
            args.style,
            "--to",
            str(tokens_path),
        ],
        check=True,
    )

    # 3. Write skeleton script.json
    script = _skeleton_script(project_id, args, music_in_public)
    (project_dir / "script.json").write_text(json.dumps(script, indent=2, ensure_ascii=False), encoding="utf-8")
    print(f"==> Wrote {project_dir/'script.json'}")

    # 4. Write skeleton Composition.tsx
    width, height = _aspect_to_size(args.aspect)
    comp_tsx = _skeleton_composition_tsx(
        project_id=project_id,
        title=args.title or project_id,
        duration_s=args.duration,
        fps=args.fps,
        width=width,
        height=height,
        music_in_public=music_in_public,
    )
    (project_dir / "Composition.tsx").write_text(comp_tsx, encoding="utf-8")
    print(f"==> Wrote {project_dir/'Composition.tsx'}")

    # 5. Register in Root.tsx
    _register_in_root(project_id)
    print(f"==> Registered in compositions/src/Root.tsx")

    print()
    print(f"DONE. Next steps:")
    print(f"  1. Drop assets (logos, images) in:  {public_dir}")
    print(f"  2. Edit:                             {project_dir/'script.json'}")
    print(f"  3. Reflect in:                       {project_dir/'Composition.tsx'}")
    print(f"  4. Render:                           avg render {project_id}")


def _aspect_to_size(aspect: str) -> tuple[int, int]:
    return {
        "9:16": (1080, 1920),
        "16:9": (1920, 1080),
        "1:1": (1080, 1080),
        "4:5": (1080, 1350),
    }[aspect]


def _skeleton_script(project_id: str, args, music_in_public: str | None) -> dict:
    return {
        "project_id": project_id,
        "title": args.title or project_id,
        "duration_s": args.duration,
        "aspect_ratio": args.aspect,
        "fps": args.fps,
        "style": args.style,
        "music": music_in_public,
        "scenes": [
            {
                "id": "s01_hero",
                "type": "hero-title",
                "t_in_s": 0,
                "t_out_s": min(3, args.duration),
                "props": {
                    "eyebrow": "TODO — eyebrow",
                    "product_wordmark": "TODO",
                    "layout": "vertical" if args.aspect == "9:16" else "horizontal",
                },
            },
            {
                "id": "s02_text",
                "type": "text-card",
                "t_in_s": min(3, args.duration),
                "t_out_s": max(min(3, args.duration), args.duration - 3),
                "props": {
                    "lines": ["Línea 1", "Línea 2"],
                    "emphasis_line": 1,
                },
            },
            {
                "id": "s99_close",
                "type": "closing-card",
                "t_in_s": max(0, args.duration - 3),
                "t_out_s": args.duration,
                "props": {
                    "logo_path": "TODO/logo.png",
                    "brand_wordmark": "autarqui",
                    "brand_wordmark_ext": ".co",
                },
            },
        ],
        "audio_mix": {
            "music": (
                {
                    "fade_in_at_s": 0.5,
                    "fade_in_duration_s": 2,
                    "trim_to_end": True,
                    "end_at_s": args.duration - 3,
                    "fade_out_duration_s": 0,
                }
                if music_in_public
                else None
            )
        },
    }


def _skeleton_composition_tsx(
    *,
    project_id: str,
    title: str,
    duration_s: int,
    fps: int,
    width: int,
    height: int,
    music_in_public: str | None,
) -> str:
    audio_block = ""
    if music_in_public:
        audio_block = f'''
        <Sequence from={{15}} durationInFrames={{TOTAL_FRAMES - 15 - 90}}>
          <Audio src={{staticFile("{music_in_public}")}} volume={{musicVolume}} />
        </Sequence>'''
    music_imports = ', buildMusicCurve' if music_in_public else ''
    music_curve = ""
    if music_in_public:
        music_curve = f'''
const musicVolume = buildMusicCurve("editorial", {{
  fps: {fps},
  fadeInFrame: 0,
  fullVolumeFrame: 75,
  fadeOutStartFrame: TOTAL_FRAMES - 15 - 120,
  fadeOutEndFrame: TOTAL_FRAMES - 15 - 90,
}});'''
    audio_import = '\nimport { Audio, Sequence, staticFile } from "remotion";' if music_in_public else ""

    return f'''/**
 * {project_id} — {title}
 *
 * Skeleton generated by `avg new`. Edit script.json + this file to build the video.
 */

import * as React from "react";
import {{ AbsoluteFill, Sequence }} from "remotion";{audio_import}

import {{ StyleProvider }} from "../../lib/tokens";
import {{ loadFontsForStyle }} from "../../lib/fonts";{music_imports and ', // ' + music_imports.lstrip(', ') or ''}
{f'import {{ {music_imports.lstrip(", ")} }} from "../../lib/audio";' if music_in_public else ""}

import {{ HeroTitle }} from "../../scenes/HeroTitle";
import {{ TextCard }} from "../../scenes/TextCard";
import {{ ClosingCard }} from "../../scenes/ClosingCard";
// Add more scene imports as needed: ListItem, MasterQuote, MarkReveal, StatReveal,
// KpiRow, KineticType, ThreeScene, LottiePlay, UIMockMobile, UIMockDesktop, ChatOverlay

import {{ TOKENS }} from "./tokens";

const DURATION_S = {duration_s};
const FPS = {fps};
const WIDTH = {width};
const HEIGHT = {height};
const TOTAL_FRAMES = DURATION_S * FPS;

const fonts = loadFontsForStyle(TOKENS);

export const meta = {{
  id: "{project_id}",
  durationInFrames: TOTAL_FRAMES,
  fps: FPS,
  width: WIDTH,
  height: HEIGHT,
}};
{music_curve}

const f = (s: number) => Math.round(s * FPS);

const SCENES: Array<{{ from: number; durationInFrames: number; el: React.ReactNode }}> = [
  {{
    from: f(0),
    durationInFrames: f(3),
    el: (
      <HeroTitle
        eyebrow="TODO — eyebrow"
        product_wordmark="TODO"
        layout="{('vertical' if width < height else 'horizontal')}"
        scene_duration_frames={{f(3)}}
        fonts={{fonts}}
      />
    ),
  }},
  {{
    from: f(3),
    durationInFrames: f({duration_s} - 6),
    el: (
      <TextCard
        lines={{["Línea 1", "Línea 2"]}}
        emphasis_line={{1}}
        scene_duration_frames={{f({duration_s} - 6)}}
        fonts={{fonts}}
      />
    ),
  }},
  {{
    from: f({duration_s} - 3),
    durationInFrames: f(3),
    el: (
      <ClosingCard
        logo_path="TODO/logo.png"
        brand_wordmark="autarqui"
        brand_wordmark_ext=".co"
        scene_duration_frames={{f(3)}}
        fonts={{fonts}}
      />
    ),
  }},
];

const Project: React.FC = () => {{
  return (
    <StyleProvider tokens={{TOKENS}}>
      <AbsoluteFill style={{{{ backgroundColor: TOKENS.colors.bg }}}}>{audio_block}
        {{SCENES.map((s, i) => (
          <Sequence key={{i}} from={{s.from}} durationInFrames={{s.durationInFrames}}>
            {{s.el}}
          </Sequence>
        ))}}
      </AbsoluteFill>
    </StyleProvider>
  );
}};

export default Project;
'''


def _register_in_root(project_id: str) -> None:
    root_path = COMPOSITIONS_DIR / "src" / "Root.tsx"
    src = root_path.read_text(encoding="utf-8")

    # Build the new import line
    var_name = _id_to_var(project_id)
    import_line = f'import * as {var_name} from "./projects/{project_id}/Composition";\n'

    # Skip if already registered
    if f'"./projects/{project_id}/Composition"' in src:
        return

    # Insert import after the last existing project import
    last_import_re = re.compile(
        r'(import \* as \w+ from "\./projects/[a-z0-9-]+/Composition";\n)'
    )
    matches = list(last_import_re.finditer(src))
    if matches:
        insert_at = matches[-1].end()
        src = src[:insert_at] + import_line + src[insert_at:]
    else:
        # No existing imports — insert before "const PROJECTS"
        src = src.replace(
            "const PROJECTS = [",
            import_line + "\nconst PROJECTS = [",
        )

    # Add to PROJECTS array
    arr_re = re.compile(r"const PROJECTS = \[(.*?)\];", re.DOTALL)
    m = arr_re.search(src)
    if m:
        body = m.group(1).strip()
        if var_name in body:
            return  # already there
        new_body = (body + (", " if body else "") + var_name).strip()
        src = src[: m.start()] + f"const PROJECTS = [{new_body}];" + src[m.end():]

    root_path.write_text(src, encoding="utf-8")


def _id_to_var(project_id: str) -> str:
    parts = project_id.split("-")
    return "".join(p.capitalize() for p in parts)


if __name__ == "__main__":
    main()
