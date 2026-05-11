import * as React from "react";
import { AbsoluteFill, Sequence } from "remotion";
import { StyleProvider } from "../../lib/tokens";
import { loadFontsForStyle } from "../../lib/fonts";
import { HeroTitle } from "../../scenes/HeroTitle";
import { StepCard } from "../../scenes/StepCard";
import { TextCard } from "../../scenes/TextCard";
import { ClosingCard } from "../../scenes/ClosingCard";
import { TOKENS } from "./tokens";

const FPS = 30;
const TOTAL_FRAMES = 60 * FPS;
const fonts = loadFontsForStyle(TOKENS);
const f = (s: number) => Math.round(s * FPS);

export const meta = {
  id: "demo-how-it-works",
  durationInFrames: TOTAL_FRAMES,
  fps: FPS,
  width: 1080,
  height: 1920,
};

const ph = (seed: string) => `https://picsum.photos/seed/${seed}/900/506`;

const STEPS = [
  { title: "Pides una cuenta.", body: "30 segundos. Sin tarjeta." },
  { title: "Conectas tus sistemas.", body: "ERP, CRM, Excel, banco. Lo que tengas." },
  { title: "Preguntas en lenguaje normal.", body: "Como se lo preguntarías a un compañero." },
  { title: "Recibes la respuesta.", body: "En menos de un segundo. Con tus datos reales." },
  { title: "Compartes con tu equipo.", body: "Un link. Sin migraciones." },
];

const Project: React.FC = () => (
  <StyleProvider tokens={TOKENS}>
    <AbsoluteFill style={{ backgroundColor: TOKENS.colors.bg }}>
      <Sequence from={f(0)} durationInFrames={f(3)}>
        <HeroTitle
          eyebrow="EN 5 PASOS"
          product_wordmark="CÓMO FUNCIONA"
          layout="vertical"
          scene_duration_frames={f(3)}
          fonts={fonts}
        />
      </Sequence>

      {STEPS.map((s, i) => (
        <Sequence key={i} from={f(3 + i * 10)} durationInFrames={f(10)}>
          <StepCard
            step_number={i + 1}
            total_steps={5}
            title={s.title}
            body={s.body}
            image_src={ph(`how-${i + 1}`)}
            image_aspect="16:9"
            scene_duration_frames={f(10)}
            fonts={fonts}
          />
        </Sequence>
      ))}

      <Sequence from={f(53)} durationInFrames={f(4)}>
        <TextCard
          lines={["Empieza en", "autarqui.co"]}
          emphasis_line={1}
          alignment="center"
          scene_duration_frames={f(4)}
          fonts={fonts}
        />
      </Sequence>

      <Sequence from={f(57)} durationInFrames={f(3)}>
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
