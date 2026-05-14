import * as React from "react";
import { AbsoluteFill, Sequence } from "remotion";
import { StyleProvider } from "../../lib/tokens";
import { loadFontsForStyle } from "../../lib/fonts";
import { HeroTitle } from "../../scenes/HeroTitle";
import { StepCard } from "../../scenes/StepCard";
import { ScreenAnnotation } from "../../scenes/ScreenAnnotation";
import { TextCard } from "../../scenes/TextCard";
import { ClosingCard } from "../../scenes/ClosingCard";
import { TOKENS } from "./tokens";

const FPS = 30;
const TOTAL_FRAMES = 60 * FPS;
const fonts = loadFontsForStyle(TOKENS);
const f = (s: number) => Math.round(s * FPS);

export const meta = {
  id: "demo-tutorial-60s",
  durationInFrames: TOTAL_FRAMES,
  fps: FPS,
  width: 1080,
  height: 1920,
};

const ph = (seed: string, w: number, h: number) => `https://picsum.photos/seed/${seed}/${w}/${h}`;

const Project: React.FC = () => (
  <StyleProvider tokens={TOKENS}>
    <AbsoluteFill style={{ backgroundColor: TOKENS.colors.bg }}>
      <Sequence from={f(0)} durationInFrames={f(4)}>
        <HeroTitle
          eyebrow="TUTORIAL · 60 SEGUNDOS"
          product_wordmark="GENERAR NÓMINA"
          layout="vertical"
          scene_duration_frames={f(4)}
          fonts={fonts}
        />
      </Sequence>

      <Sequence from={f(4)} durationInFrames={f(11)}>
        <StepCard
          step_number={1}
          total_steps={4}
          title="Conecta tu empresa."
          body="Una sola vez. Después se queda."
          image_src={ph("step-connect", 900, 506)}
          image_aspect="16:9"
          scene_duration_frames={f(11)}
          fonts={fonts}
        />
      </Sequence>

      <Sequence from={f(15)} durationInFrames={f(11)}>
        <StepCard
          step_number={2}
          total_steps={4}
          title="Añade empleados."
          body="O importa de tu antiguo sistema."
          image_src={ph("step-employees", 900, 506)}
          image_aspect="16:9"
          scene_duration_frames={f(11)}
          fonts={fonts}
        />
      </Sequence>

      <Sequence from={f(26)} durationInFrames={f(13)}>
        <ScreenAnnotation
          screenshot_src={ph("step-validate", 1080, 1400)}
          caption="Paso 3 · Valida los conceptos del mes."
          annotations={[
            { type: "circle", x_pct: 78, y_pct: 35, size_pct: 22, appear_at_s: 1, color: "#e8a560" },
            { type: "callout", x_pct: 78, y_pct: 22, text: "Aquí revisas y editas", appear_at_s: 1.5, color: "#e8a560" },
            { type: "arrow", from_x_pct: 50, from_y_pct: 70, to_x_pct: 70, to_y_pct: 50, appear_at_s: 4, color: "#a3d9a5" },
            { type: "callout", x_pct: 50, y_pct: 80, text: "Confirma para generar", appear_at_s: 4.5, color: "#a3d9a5" },
          ]}
          scene_duration_frames={f(13)}
          fonts={fonts}
        />
      </Sequence>

      <Sequence from={f(39)} durationInFrames={f(11)}>
        <StepCard
          step_number={4}
          total_steps={4}
          title="Genera y envía."
          body="Las nóminas llegan al empleado y la remesa al banco."
          image_src={ph("step-send", 900, 506)}
          image_aspect="16:9"
          scene_duration_frames={f(11)}
          fonts={fonts}
        />
      </Sequence>

      <Sequence from={f(50)} durationInFrames={f(7)}>
        <TextCard
          lines={["8 minutos.", "Una vez al mes."]}
          emphasis_line={1}
          alignment="center"
          scene_duration_frames={f(7)}
          fonts={fonts}
        />
      </Sequence>

      <Sequence from={f(57)} durationInFrames={f(3)}>
        <ClosingCard
          logo_path=""
          product_wordmark="SIGMA"
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
