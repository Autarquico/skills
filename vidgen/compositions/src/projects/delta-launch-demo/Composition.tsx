/**
 * delta-launch-demo — Composition.
 *
 * Validates the full token-driven pipeline:
 *   visual-style.md (autarqui-co)  →  TOKENS const (this file's import)
 *   →  StyleProvider context  →  scenes from library  →  render
 *
 * This is what the render-director generates per-project.
 */

import * as React from "react";
import { AbsoluteFill, Audio, Sequence, staticFile } from "remotion";

import { StyleProvider } from "../../lib/tokens";
import { loadFontsForStyle } from "../../lib/fonts";
import { buildMusicCurve, calcTrimBefore } from "../../lib/audio";

import { TextCard } from "../../scenes/TextCard";
import { HeroTitle } from "../../scenes/HeroTitle";
import { ListItem } from "../../scenes/ListItem";
import { MasterQuote } from "../../scenes/MasterQuote";
import { ClosingCard } from "../../scenes/ClosingCard";

import { TOKENS } from "./tokens";

// === Static metadata =========================================================

const DURATION_S = 30;
const FPS = 30;
const WIDTH = 1080;
const HEIGHT = 1920;
const TOTAL_FRAMES = DURATION_S * FPS; // 900

// Music alignment: file is 132s long; play from frame 15 to frame 810 (27s),
// silence on closing card 810→900. trimBefore lines up the file's end with
// frame 810 — same approach validated in the source session.
const MUSIC_FILE_DURATION_S = 132.466;
const MUSIC_START_FRAME = 15;
const MUSIC_END_FRAME = 810;
const MUSIC_TRIM_BEFORE = calcTrimBefore({
  audioFileDurationS: MUSIC_FILE_DURATION_S,
  startFrame: MUSIC_START_FRAME,
  endFrame: MUSIC_END_FRAME,
  fps: FPS,
});

const fonts = loadFontsForStyle(TOKENS);

export const meta = {
  id: "delta-launch-demo",
  durationInFrames: TOTAL_FRAMES,
  fps: FPS,
  width: WIDTH,
  height: HEIGHT,
};

const musicVolume = buildMusicCurve("editorial", {
  fps: FPS,
  fadeInFrame: MUSIC_START_FRAME,
  fullVolumeFrame: MUSIC_START_FRAME + 75,
  fadeOutStartFrame: MUSIC_END_FRAME - 30,
  fadeOutEndFrame: MUSIC_END_FRAME,
});

// === Scene timing (frames) ===================================================

const SCENES: Array<{ from: number; durationInFrames: number; el: React.ReactNode }> = [
  {
    from: 0 * FPS,
    durationInFrames: 3 * FPS,
    el: (
      <HeroTitle
        umbrella_logo="delta-launch-demo/alpha-logo.png"
        umbrella_wordmark="autarqui"
        umbrella_wordmark_ext=".co"
        eyebrow="PRESENTA"
        product_logo="delta-launch-demo/delta-logo.png"
        product_wordmark="DELTA"
        layout="vertical"
        scene_duration_frames={3 * FPS}
        fonts={fonts}
      />
    ),
  },
  {
    from: 3 * FPS,
    durationInFrames: 6 * FPS,
    el: (
      <TextCard
        lines={[
          "Tu negocio sabe más",
          "de lo que crees.",
          "El problema es que no puedes preguntarle.",
        ]}
        emphasis_line={2}
        scene_duration_frames={6 * FPS}
        fonts={fonts}
      />
    ),
  },
  {
    from: 9 * FPS,
    durationInFrames: 6 * FPS,
    el: (
      <ListItem
        numeral="01"
        text="Ese cliente que no ha vuelto desde febrero."
        scene_duration_frames={6 * FPS}
        fonts={fonts}
      />
    ),
  },
  {
    from: 15 * FPS,
    durationInFrames: 6 * FPS,
    el: (
      <ListItem
        numeral="02"
        text="La factura que vence el martes y nadie ha mirado."
        scene_duration_frames={6 * FPS}
        fonts={fonts}
      />
    ),
  },
  {
    from: 21 * FPS,
    durationInFrames: 6 * FPS,
    el: (
      <MasterQuote
        text="autarqui.co hace empresas más autosuficientes."
        scene_duration_frames={6 * FPS}
        fonts={fonts}
      />
    ),
  },
  {
    from: 27 * FPS,
    durationInFrames: 3 * FPS,
    el: (
      <ClosingCard
        logo_path="delta-launch-demo/delta-logo.png"
        product_wordmark="DELTA"
        brand_wordmark="autarqui"
        brand_wordmark_ext=".co"
        scene_duration_frames={3 * FPS}
        fonts={fonts}
      />
    ),
  },
];

// === Composition =============================================================

const DeltaLaunchDemo: React.FC = () => {
  return (
    <StyleProvider tokens={TOKENS}>
      <AbsoluteFill style={{ backgroundColor: TOKENS.colors.bg }}>
        <Sequence from={MUSIC_START_FRAME} durationInFrames={MUSIC_END_FRAME - MUSIC_START_FRAME}>
          <Audio
            src={staticFile("delta-launch-demo/music.mp3")}
            trimBefore={MUSIC_TRIM_BEFORE}
            volume={(f) => musicVolume(f + MUSIC_START_FRAME)}
          />
        </Sequence>

        {SCENES.map((s, i) => (
          <Sequence key={i} from={s.from} durationInFrames={s.durationInFrames}>
            {s.el}
          </Sequence>
        ))}
      </AbsoluteFill>
    </StyleProvider>
  );
};

export default DeltaLaunchDemo;
