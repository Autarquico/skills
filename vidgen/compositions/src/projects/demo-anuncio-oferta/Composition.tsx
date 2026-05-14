import * as React from "react";
import { AbsoluteFill, Sequence } from "remotion";
import { StyleProvider } from "../../lib/tokens";
import { loadFontsForStyle } from "../../lib/fonts";
import { PhotoBackground } from "../../scenes/PhotoBackground";
import { PriceCard } from "../../scenes/PriceCard";
import { TextCard } from "../../scenes/TextCard";
import { TOKENS } from "./tokens";

const FPS = 30;
const TOTAL_FRAMES = 30 * FPS;
const fonts = loadFontsForStyle(TOKENS);
const f = (s: number) => Math.round(s * FPS);

export const meta = {
  id: "demo-anuncio-oferta",
  durationInFrames: TOTAL_FRAMES,
  fps: FPS,
  width: 1080,
  height: 1920,
};

const ph = (seed: string, w = 1080, h = 1920) => `https://picsum.photos/seed/${seed}/${w}/${h}`;

const Project: React.FC = () => (
  <StyleProvider tokens={TOKENS}>
    <AbsoluteFill style={{ backgroundColor: TOKENS.colors.bg }}>
      <Sequence from={f(0)} durationInFrames={f(5)}>
        <PhotoBackground
          photo_src={ph("office-pro", 1080, 1920)}
          eyebrow="OFERTA · 3 DÍAS"
          headline="sigma anual."
          subline="Tu asesoría laboral y fiscal, sin esperas."
          text_position="bottom-left"
          overlay_opacity={0.5}
          ken_burns
          scene_duration_frames={f(5)}
          fonts={fonts}
        />
      </Sequence>

      <Sequence from={f(5)} durationInFrames={f(12)}>
        <PriceCard
          eyebrow="PRECIO LANZAMIENTO"
          product_name="sigma · plan anual"
          was_price="€1.188"
          price="€828"
          tagline="Hasta el viernes. Después: precio normal."
          cta="Quiero la oferta"
          scene_duration_frames={f(12)}
          fonts={fonts}
        />
      </Sequence>

      <Sequence from={f(17)} durationInFrames={f(7)}>
        <TextCard
          lines={["Cancelas cuando quieras.", "Tus datos siempre son tuyos."]}
          emphasis_line={1}
          scene_duration_frames={f(7)}
          fonts={fonts}
        />
      </Sequence>

      <Sequence from={f(24)} durationInFrames={f(6)}>
        <PhotoBackground
          photo_src={ph("desk-papers", 1080, 1920)}
          eyebrow="autarqui.co/sigma"
          headline="Empezar hoy."
          text_position="bottom-center"
          overlay_opacity={0.55}
          ken_burns
          scene_duration_frames={f(6)}
          fonts={fonts}
        />
      </Sequence>
    </AbsoluteFill>
  </StyleProvider>
);

export default Project;
