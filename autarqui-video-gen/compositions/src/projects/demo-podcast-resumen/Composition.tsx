import * as React from "react";
import { AbsoluteFill, Sequence } from "remotion";
import { StyleProvider } from "../../lib/tokens";
import { loadFontsForStyle } from "../../lib/fonts";
import { HeroTitle } from "../../scenes/HeroTitle";
import { WaveformOverlay } from "../../scenes/WaveformOverlay";
import { TextCard } from "../../scenes/TextCard";
import { ClosingCard } from "../../scenes/ClosingCard";
import { TOKENS } from "./tokens";

const FPS = 30;
const TOTAL_FRAMES = 30 * FPS;
const fonts = loadFontsForStyle(TOKENS);
const f = (s: number) => Math.round(s * FPS);

export const meta = {
  id: "demo-podcast-resumen",
  durationInFrames: TOTAL_FRAMES,
  fps: FPS,
  width: 1080,
  height: 1920,
};

const Project: React.FC = () => (
  <StyleProvider tokens={TOKENS}>
    <AbsoluteFill style={{ backgroundColor: TOKENS.colors.bg }}>
      <Sequence from={f(0)} durationInFrames={f(3)}>
        <HeroTitle
          eyebrow="PODCAST · EPISODIO 47"
          product_wordmark="LO MEJOR EN 30s"
          layout="vertical"
          scene_duration_frames={f(3)}
          fonts={fonts}
        />
      </Sequence>

      <Sequence from={f(3)} durationInFrames={f(10)}>
        <WaveformOverlay
          mode="synthetic"
          eyebrow="MIN 12:34"
          quote="No buscamos sustituir a nadie. Buscamos que las preguntas que antes no se hacían empiecen a hacerse."
          attribution="— María García · Directora de Operaciones"
          show_playhead
          scene_duration_frames={f(10)}
          fonts={fonts}
        />
      </Sequence>

      <Sequence from={f(13)} durationInFrames={f(10)}>
        <WaveformOverlay
          mode="synthetic"
          eyebrow="MIN 24:18"
          quote="La diferencia no es la velocidad. Es que ahora pregunto cosas que antes no compensaba el tiempo de buscar."
          attribution="— Pablo Vega · CEO"
          show_playhead
          scene_duration_frames={f(10)}
          fonts={fonts}
        />
      </Sequence>

      <Sequence from={f(23)} durationInFrames={f(4)}>
        <TextCard
          lines={["Episodio completo en", "autarqui.co/podcast"]}
          emphasis_line={1}
          alignment="center"
          scene_duration_frames={f(4)}
          fonts={fonts}
        />
      </Sequence>

      <Sequence from={f(27)} durationInFrames={f(3)}>
        <ClosingCard
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
