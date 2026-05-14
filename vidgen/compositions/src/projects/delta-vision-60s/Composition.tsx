/**
 * delta-vision-60s — La visión silenciosa.
 *
 * Narrative: chaos (500 personas, 12 sistemas, 0 visión) → delta observes →
 * order (1 pregunta · 1 respuesta · todo el negocio).
 *
 * Generated from script.json by render-director.
 */

import * as React from "react";
import { AbsoluteFill, Audio, Sequence, staticFile } from "remotion";

import { StyleProvider } from "../../lib/tokens";
import { loadFontsForStyle } from "../../lib/fonts";
import { buildMusicCurve, calcTrimBefore } from "../../lib/audio";

import { HeroTitle } from "../../scenes/HeroTitle";
import { TextCard } from "../../scenes/TextCard";
import { ListItem } from "../../scenes/ListItem";
import { MarkReveal } from "../../scenes/MarkReveal";
import { StatReveal } from "../../scenes/StatReveal";
import { MasterQuote } from "../../scenes/MasterQuote";
import { ClosingCard } from "../../scenes/ClosingCard";

import { TOKENS } from "./tokens";

const DURATION_S = 60;
const FPS = 30;
const WIDTH = 1080;
const HEIGHT = 1920;
const TOTAL_FRAMES = DURATION_S * FPS; // 1800

// Music: 132.466s file, play from frame 15 (0.5s) to frame 1710 (57s),
// silence on closing card (57-60s). trim_to_end aligns natural end of file
// with frame 1710 so the cut to silence feels musical.
const MUSIC_FILE_DURATION_S = 132.466;
const MUSIC_START_FRAME = 15;
const MUSIC_END_FRAME = 1710;
const MUSIC_TRIM_BEFORE = calcTrimBefore({
  audioFileDurationS: MUSIC_FILE_DURATION_S,
  startFrame: MUSIC_START_FRAME,
  endFrame: MUSIC_END_FRAME,
  fps: FPS,
});

const fonts = loadFontsForStyle(TOKENS);

export const meta = {
  id: "delta-vision-60s",
  durationInFrames: TOTAL_FRAMES,
  fps: FPS,
  width: WIDTH,
  height: HEIGHT,
};

const musicVolume = buildMusicCurve("editorial", {
  fps: FPS,
  fadeInFrame: 0,
  fullVolumeFrame: 75,
  fadeOutStartFrame: MUSIC_END_FRAME - MUSIC_START_FRAME - 30,
  fadeOutEndFrame: MUSIC_END_FRAME - MUSIC_START_FRAME,
});

const f = (s: number) => s * FPS;

const SCENES: Array<{ from: number; durationInFrames: number; el: React.ReactNode }> = [
  // S01 — Brand intro (0-3s)
  {
    from: f(0),
    durationInFrames: f(3),
    el: (
      <HeroTitle
        umbrella_logo="delta-vision-60s/alpha-logo.png"
        umbrella_wordmark="autarqui"
        umbrella_wordmark_ext=".co"
        eyebrow="PRESENTA"
        product_logo="delta-vision-60s/delta-logo.png"
        product_wordmark="DELTA"
        layout="vertical"
        scene_duration_frames={f(3)}
        fonts={fonts}
      />
    ),
  },
  // S02 — Hero question (3-10s)
  {
    from: f(3),
    durationInFrames: f(7),
    el: (
      <TextCard
        lines={["Tu empresa funciona.", "Pero ¿quién la ve", "entera?"]}
        emphasis_line={1}
        scene_duration_frames={f(7)}
        fonts={fonts}
      />
    ),
  },
  // S03 — List 01 (10-16s)
  {
    from: f(10),
    durationInFrames: f(6),
    el: (
      <ListItem
        numeral="01"
        text="500 personas haciendo su trabajo."
        scene_duration_frames={f(6)}
        fonts={fonts}
      />
    ),
  },
  // S04 — List 02 (16-22s)
  {
    from: f(16),
    durationInFrames: f(6),
    el: (
      <ListItem
        numeral="02"
        text="12 sistemas guardando los datos."
        scene_duration_frames={f(6)}
        fonts={fonts}
      />
    ),
  },
  // S05 — List 03 (22-28s)
  {
    from: f(22),
    durationInFrames: f(6),
    el: (
      <ListItem
        numeral="03"
        text="Cero visión de conjunto."
        scene_duration_frames={f(6)}
        fonts={fonts}
      />
    ),
  },
  // S06 — Pivot (28-33s)
  {
    from: f(28),
    durationInFrames: f(5),
    el: (
      <TextCard
        lines={["Hasta que alguien", "observa todo."]}
        emphasis_line={1}
        scene_duration_frames={f(5)}
        fonts={fonts}
      />
    ),
  },
  // S07 — Mark reveal (33-39s)
  {
    from: f(33),
    durationInFrames: f(6),
    el: (
      <MarkReveal
        logo_path="delta-vision-60s/delta-logo.png"
        wordmark="DELTA"
        wordmark_case="uppercase"
        tagline="El observador silencioso."
        scene_duration_frames={f(6)}
        fonts={fonts}
      />
    ),
  },
  // S08 — Promise (39-46s)
  {
    from: f(39),
    durationInFrames: f(7),
    el: (
      <TextCard
        lines={["Tú preguntas.", "Delta responde", "con todo lo que ya sabes."]}
        emphasis_line={1}
        scene_duration_frames={f(7)}
        fonts={fonts}
      />
    ),
  },
  // S09 — Stat reveal (46-52s)
  {
    from: f(46),
    durationInFrames: f(6),
    el: (
      <StatReveal
        eyebrow="EL TIEMPO QUE TARDA"
        value="< 1 s"
        label="una pregunta · una respuesta · todo el negocio"
        scene_duration_frames={f(6)}
        fonts={fonts}
      />
    ),
  },
  // S10 — Master quote (52-57s)
  {
    from: f(52),
    durationInFrames: f(5),
    el: (
      <MasterQuote
        text="autarqui.co hace empresas más autosuficientes."
        scene_duration_frames={f(5)}
        fonts={fonts}
      />
    ),
  },
  // S11 — Closing (57-60s, in silence)
  {
    from: f(57),
    durationInFrames: f(3),
    el: (
      <ClosingCard
        logo_path="delta-vision-60s/delta-logo.png"
        product_wordmark="DELTA"
        brand_wordmark="autarqui"
        brand_wordmark_ext=".co"
        scene_duration_frames={f(3)}
        fonts={fonts}
      />
    ),
  },
];

const DeltaVision60s: React.FC = () => {
  return (
    <StyleProvider tokens={TOKENS}>
      <AbsoluteFill style={{ backgroundColor: TOKENS.colors.bg }}>
        <Sequence from={MUSIC_START_FRAME} durationInFrames={MUSIC_END_FRAME - MUSIC_START_FRAME}>
          <Audio
            src={staticFile("delta-vision-60s/music.mp3")}
            trimBefore={MUSIC_TRIM_BEFORE}
            volume={musicVolume}
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

export default DeltaVision60s;
