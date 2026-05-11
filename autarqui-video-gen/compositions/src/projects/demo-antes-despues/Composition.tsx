import * as React from "react";
import { AbsoluteFill, Sequence } from "remotion";
import { StyleProvider } from "../../lib/tokens";
import { loadFontsForStyle } from "../../lib/fonts";
import { HeroTitle } from "../../scenes/HeroTitle";
import { SplitScreen } from "../../scenes/SplitScreen";
import { TextCard } from "../../scenes/TextCard";
import { ClosingCard } from "../../scenes/ClosingCard";
import { TOKENS } from "./tokens";

const FPS = 30;
const TOTAL_FRAMES = 30 * FPS;
const fonts = loadFontsForStyle(TOKENS);
const f = (s: number) => Math.round(s * FPS);

export const meta = {
  id: "demo-antes-despues",
  durationInFrames: TOTAL_FRAMES,
  fps: FPS,
  width: 1080,
  height: 1920,
};

const ph = (seed: string, w = 1080, h = 1080) => `https://picsum.photos/seed/${seed}/${w}/${h}`;

const Project: React.FC = () => (
  <StyleProvider tokens={TOKENS}>
    <AbsoluteFill style={{ backgroundColor: TOKENS.colors.bg }}>
      <Sequence from={f(0)} durationInFrames={f(3)}>
        <HeroTitle
          eyebrow="ANTES · DESPUÉS"
          product_wordmark="EL CAMBIO"
          layout="vertical"
          scene_duration_frames={f(3)}
          fonts={fonts}
        />
      </Sequence>

      <Sequence from={f(3)} durationInFrames={f(10)}>
        <SplitScreen
          left={{
            photo_src: ph("messy-desk", 1080, 960),
            label: "Excels que no se hablan.",
            sublabel: "12 pestañas. 4 personas. 0 visión.",
          }}
          right={{
            photo_src: ph("clean-desk", 1080, 960),
            label: "Una pregunta. Una respuesta.",
            sublabel: "Tus datos, donde siempre han estado.",
          }}
          layout="vertical"
          wipe_reveal
          scene_duration_frames={f(10)}
          fonts={fonts}
        />
      </Sequence>

      <Sequence from={f(13)} durationInFrames={f(9)}>
        <SplitScreen
          left={{
            photo_src: ph("manual-papers", 1080, 960),
            label: "Buscar el dato.",
            sublabel: "Dos horas. Tres personas implicadas.",
          }}
          right={{
            photo_src: ph("phone-clean", 1080, 960),
            label: "Tener el dato.",
            sublabel: "Menos de un segundo.",
          }}
          layout="vertical"
          wipe_reveal
          scene_duration_frames={f(9)}
          fonts={fonts}
        />
      </Sequence>

      <Sequence from={f(22)} durationInFrames={f(5)}>
        <TextCard
          lines={["El cambio se ve.", "Tú decides cuándo empezar."]}
          emphasis_line={1}
          alignment="center"
          scene_duration_frames={f(5)}
          fonts={fonts}
        />
      </Sequence>

      <Sequence from={f(27)} durationInFrames={f(3)}>
        <ClosingCard
          logo_path=""
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
