# Projects

Each subfolder is one video. Drop a `Composition.tsx` that exports a default React component plus a `meta` object with `{id, durationInFrames, fps, width, height}` and `Root.tsx` will auto-discover it.

## Conventions

- Folder name = project id (kebab-case)
- Folder layout:
  ```
  <id>/
  ├── Composition.tsx     # required — exports default + meta
  ├── script.json          # the source-of-truth declarative script
  ├── assets/              # optional project-specific assets
  └── *.tsx                # optional custom scenes (not in shared library)
  ```

## Generating a Composition.tsx

The render-director (in `directors/render-director.md`) reads `script.json` and writes `Composition.tsx` automatically. You don't normally hand-write it.

A generated `Composition.tsx` looks like:

```tsx
import { AbsoluteFill, Sequence, Audio, staticFile } from "remotion";
import { loadStyle, StyleProvider } from "../../lib/tokens";
import { loadFontsForStyle } from "../../lib/fonts";
import { buildMusicCurve, calcTrimBefore } from "../../lib/audio";
import { SCENES } from "../../scenes";
import scriptData from "./script.json";

const tokens = loadStyle(scriptData.style);
const fonts = loadFontsForStyle(tokens);

export const meta = {
  id: scriptData.project_id,
  durationInFrames: scriptData.duration_s * scriptData.fps,
  fps: scriptData.fps,
  width: scriptData.aspect_ratio === "9:16" ? 1080 : 1920,
  height: scriptData.aspect_ratio === "9:16" ? 1920 : 1080,
};

export default function Composition() {
  return (
    <StyleProvider tokens={tokens}>
      <AbsoluteFill style={{ backgroundColor: tokens.colors.bg }}>
        {/* Music with trimBefore aligned to script.audio_mix */}
        {/* Scenes via Sequence with timing from script.json */}
      </AbsoluteFill>
    </StyleProvider>
  );
}
```
