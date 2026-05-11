import * as React from "react";
import { AbsoluteFill, Sequence } from "remotion";
import { StyleProvider } from "../../lib/tokens";
import { loadFontsForStyle } from "../../lib/fonts";
import { HeroTitle } from "../../scenes/HeroTitle";
import { BarChart } from "../../scenes/BarChart";
import { LineChart } from "../../scenes/LineChart";
import { TextCard } from "../../scenes/TextCard";
import { ClosingCard } from "../../scenes/ClosingCard";
import { TOKENS } from "./tokens";

const FPS = 30;
const TOTAL_FRAMES = 30 * FPS;
const fonts = loadFontsForStyle(TOKENS);
const f = (s: number) => Math.round(s * FPS);

export const meta = {
  id: "demo-data-viz",
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
          eyebrow="DATOS · Q1 2026"
          product_wordmark="EL TRIMESTRE"
          layout="vertical"
          scene_duration_frames={f(3)}
          fonts={fonts}
        />
      </Sequence>

      <Sequence from={f(3)} durationInFrames={f(10)}>
        <BarChart
          title="Tiempo medio por consulta"
          subtitle="minutos · histórico vs. delta"
          bars={[
            { label: "Antes", value: 95 },
            { label: "Mes 1", value: 58 },
            { label: "Mes 2", value: 22 },
            { label: "Mes 3", value: 4, highlight: true },
          ]}
          stagger_frames={10}
          scene_duration_frames={f(10)}
          fonts={fonts}
        />
      </Sequence>

      <Sequence from={f(13)} durationInFrames={f(9)}>
        <LineChart
          title="Preguntas hechas al negocio"
          subtitle="por semana · 2026"
          points={[12, 18, 24, 31, 47, 68, 94, 142, 198, 247]}
          x_labels={["Sem 1", "", "", "", "Sem 5", "", "", "", "", "Sem 10"]}
          highlight_end="247"
          scene_duration_frames={f(9)}
          fonts={fonts}
        />
      </Sequence>

      <Sequence from={f(22)} durationInFrames={f(5)}>
        <TextCard
          lines={["Cuando preguntar es barato,", "se pregunta más."]}
          emphasis_line={1}
          alignment="center"
          scene_duration_frames={f(5)}
          fonts={fonts}
        />
      </Sequence>

      <Sequence from={f(27)} durationInFrames={f(3)}>
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
