import * as React from "react";
import { AbsoluteFill, Sequence } from "remotion";
import { StyleProvider } from "../../lib/tokens";
import { loadFontsForStyle } from "../../lib/fonts";
import { HeroTitle } from "../../scenes/HeroTitle";
import { QuoteCard } from "../../scenes/QuoteCard";
import { ClosingCard } from "../../scenes/ClosingCard";
import { TOKENS } from "./tokens";

const FPS = 30;
const TOTAL_FRAMES = 30 * FPS;
const fonts = loadFontsForStyle(TOKENS);
const f = (s: number) => Math.round(s * FPS);

export const meta = {
  id: "demo-testimonial",
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
          eyebrow="TESTIMONIAL · CLIENTES"
          product_wordmark="DELTA"
          layout="vertical"
          scene_duration_frames={f(3)}
          fonts={fonts}
        />
      </Sequence>

      <Sequence from={f(3)} durationInFrames={f(11)}>
        <QuoteCard
          quote="Antes me costaba dos horas responder al CEO. Ahora pregunto y me responde en segundos. La diferencia es que pregunto cosas que antes no preguntaba."
          attribution_name="María García"
          attribution_role="Directora de Operaciones · Hostelería Norte S.L."
          initials="MG"
          scene_duration_frames={f(11)}
          fonts={fonts}
        />
      </Sequence>

      <Sequence from={f(14)} durationInFrames={f(13)}>
        <QuoteCard
          quote="Conectamos delta a nuestro ERP en una mañana. Sin migrar nada. Sin equipo técnico nuevo."
          attribution_name="Pablo Vega"
          attribution_role="CEO · Distribución Atlántica"
          initials="PV"
          scene_duration_frames={f(13)}
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
