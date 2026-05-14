import * as React from "react";
import { AbsoluteFill, Sequence } from "remotion";
import { StyleProvider } from "../../lib/tokens";
import { loadFontsForStyle } from "../../lib/fonts";
import { PhotoBackground } from "../../scenes/PhotoBackground";
import { PhotoSlideshow } from "../../scenes/PhotoSlideshow";
import { PhotoCard } from "../../scenes/PhotoCard";
import { ClosingCard } from "../../scenes/ClosingCard";
import { TOKENS } from "./tokens";

const FPS = 30;
const TOTAL_FRAMES = 30 * FPS;
const fonts = loadFontsForStyle(TOKENS);
const f = (s: number) => Math.round(s * FPS);

export const meta = {
  id: "demo-foto-instagram",
  durationInFrames: TOTAL_FRAMES,
  fps: FPS,
  width: 1080,
  height: 1920,
};

// Picsum.photos delivers deterministic placeholder photos via seed.
const ph = (seed: string, w = 1080, h = 1920) => `https://picsum.photos/seed/${seed}/${w}/${h}`;

const Project: React.FC = () => (
  <StyleProvider tokens={TOKENS}>
    <AbsoluteFill style={{ backgroundColor: TOKENS.colors.bg }}>
      <Sequence from={f(0)} durationInFrames={f(4)}>
        <PhotoBackground
          photo_src={ph("collection-hero", 1080, 1920)}
          eyebrow="OTOÑO 2026"
          headline="La nueva colección está fuera."
          text_position="bottom-left"
          overlay_opacity={0.45}
          ken_burns
          scene_duration_frames={f(4)}
          fonts={fonts}
        />
      </Sequence>

      <Sequence from={f(4)} durationInFrames={f(8)}>
        <PhotoSlideshow
          photos={[
            { src: ph("product-1", 1080, 1920) },
            { src: ph("product-2", 1080, 1920) },
            { src: ph("product-3", 1080, 1920) },
            { src: ph("product-4", 1080, 1920) },
          ]}
          hold_per_photo_s={1.5}
          crossfade_s={0.5}
          scene_duration_frames={f(8)}
        />
      </Sequence>

      <Sequence from={f(12)} durationInFrames={f(8)}>
        <PhotoCard
          photo_src={ph("craft-1", 880, 1100)}
          eyebrow="HECHO EN ESPAÑA"
          caption="Tirada limitada · 200 unidades."
          photo_aspect="4:5"
          ken_burns
          scene_duration_frames={f(8)}
          fonts={fonts}
        />
      </Sequence>

      <Sequence from={f(20)} durationInFrames={f(8)}>
        <PhotoBackground
          photo_src={ph("city-bokeh", 1080, 1920)}
          eyebrow="ENVÍO GRATIS · LOS DOMINGOS LLEGA EL LUNES"
          headline="autarqui.co/coleccion"
          text_position="center"
          overlay_opacity={0.55}
          ken_burns
          scene_duration_frames={f(8)}
          fonts={fonts}
        />
      </Sequence>

      <Sequence from={f(28)} durationInFrames={f(2)}>
        <ClosingCard
          logo_path=""
          brand_wordmark="autarqui"
          brand_wordmark_ext=".co"
          scene_duration_frames={f(2)}
          fonts={fonts}
        />
      </Sequence>
    </AbsoluteFill>
  </StyleProvider>
);

export default Project;
