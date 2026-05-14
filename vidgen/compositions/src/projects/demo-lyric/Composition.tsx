import * as React from "react";
import { AbsoluteFill, Sequence } from "remotion";
import { StyleProvider } from "../../lib/tokens";
import { loadFontsForStyle } from "../../lib/fonts";
import { LyricLine } from "../../scenes/LyricLine";
import { ClosingCard } from "../../scenes/ClosingCard";
import { TOKENS } from "./tokens";

const FPS = 30;
const TOTAL_FRAMES = 20 * FPS;
const fonts = loadFontsForStyle(TOKENS);
const f = (s: number) => Math.round(s * FPS);

export const meta = {
  id: "demo-lyric",
  durationInFrames: TOTAL_FRAMES,
  fps: FPS,
  width: 1080,
  height: 1920,
};

// Lyric timing — for production, generate from beat-detect.py + manual sync.
// Each line gets its own Sequence with start/duration matching audio.
const LINES: Array<{ start: number; dur: number; text: string; next?: string; mode?: "bold" | "italic" | "minimal" }> = [
  { start: 0, dur: 2.5, text: "Tu negocio sabe.", next: "Lo que no sabes es preguntarle.", mode: "bold" },
  { start: 2.5, dur: 2.5, text: "Lo que no sabes", next: "es preguntarle.", mode: "italic" },
  { start: 5, dur: 3, text: "Cada dato.", mode: "bold" },
  { start: 8, dur: 3, text: "Cada cliente.", mode: "bold" },
  { start: 11, dur: 3, text: "Cada decisión.", mode: "italic" },
  { start: 14, dur: 3, text: "Una sola pregunta.", next: "Una sola respuesta.", mode: "bold" },
];

const Project: React.FC = () => (
  <StyleProvider tokens={TOKENS}>
    <AbsoluteFill style={{ backgroundColor: TOKENS.colors.bg }}>
      {LINES.map((l, i) => (
        <Sequence key={i} from={f(l.start)} durationInFrames={f(l.dur)}>
          <LyricLine
            text={l.text}
            next_text={l.next}
            mode={l.mode || "bold"}
            pulse_frames={20}
            scene_duration_frames={f(l.dur)}
            fonts={fonts}
          />
        </Sequence>
      ))}

      <Sequence from={f(17)} durationInFrames={f(3)}>
        <ClosingCard
          product_wordmark="DELTA"
          brand_wordmark="autarqui"
          brand_wordmark_ext=".co"
          scene_duration_frames={f(3)}
          fonts={fonts}
        />
      </Sequence>
    </AbsoluteFill>
  </StyleProvider>
);

export default Project;
