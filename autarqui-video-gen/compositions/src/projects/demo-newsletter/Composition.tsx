import * as React from "react";
import { AbsoluteFill, Sequence } from "remotion";
import { StyleProvider } from "../../lib/tokens";
import { loadFontsForStyle } from "../../lib/fonts";
import { HeroTitle } from "../../scenes/HeroTitle";
import { PhotoCardGrid } from "../../scenes/PhotoCardGrid";
import { TextCard } from "../../scenes/TextCard";
import { ClosingCard } from "../../scenes/ClosingCard";
import { TOKENS } from "./tokens";

const FPS = 30;
const TOTAL_FRAMES = 30 * FPS;
const fonts = loadFontsForStyle(TOKENS);
const f = (s: number) => Math.round(s * FPS);

export const meta = {
  id: "demo-newsletter",
  durationInFrames: TOTAL_FRAMES,
  fps: FPS,
  width: 1080,
  height: 1920,
};

const ph = (seed: string) => `https://picsum.photos/seed/${seed}/800/600`;

const Project: React.FC = () => (
  <StyleProvider tokens={TOKENS}>
    <AbsoluteFill style={{ backgroundColor: TOKENS.colors.bg }}>
      <Sequence from={f(0)} durationInFrames={f(3)}>
        <HeroTitle
          eyebrow="NEWSLETTER · MAYO 2026"
          product_wordmark="LO QUE PASÓ"
          layout="vertical"
          scene_duration_frames={f(3)}
          fonts={fonts}
        />
      </Sequence>

      <Sequence from={f(3)} durationInFrames={f(11)}>
        <PhotoCardGrid
          eyebrow="ESTA SEMANA · 4 NOTICIAS"
          items={[
            { photo_src: ph("news-1"), headline: "delta abre beta", caption: "Primeros 50 clientes invitados a probarlo." },
            { photo_src: ph("news-2"), headline: "sigma + agencias", caption: "Nuevo plan multi-empresa para asesorías." },
            { photo_src: ph("news-3"), headline: "Madrid + 1", caption: "Abrimos oficina en el centro." },
            { photo_src: ph("news-4"), headline: "Roadmap Q3", caption: "Nuevas integraciones, mismo precio." },
          ]}
          stagger_frames={10}
          scene_duration_frames={f(11)}
          fonts={fonts}
        />
      </Sequence>

      <Sequence from={f(14)} durationInFrames={f(11)}>
        <PhotoCardGrid
          eyebrow="VENIENDO EN JUNIO · 2 LANZAMIENTOS"
          items={[
            { photo_src: ph("news-5"), headline: "delta · multi-idioma", caption: "Pregunta y respuesta en EN/FR/PT." },
            { photo_src: ph("news-6"), headline: "sigma · firma digital", caption: "Contratos firmados en el móvil." },
          ]}
          stagger_frames={14}
          scene_duration_frames={f(11)}
          fonts={fonts}
        />
      </Sequence>

      <Sequence from={f(25)} durationInFrames={f(2)}>
        <TextCard
          lines={["Suscríbete en", "autarqui.co/news"]}
          emphasis_line={1}
          alignment="center"
          scene_duration_frames={f(2)}
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
