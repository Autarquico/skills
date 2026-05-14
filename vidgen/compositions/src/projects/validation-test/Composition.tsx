/**
 * validation-test — exercises previously untested scenes.
 *
 * 30s 9:16: HeroTitle → KineticType → ThreeScene → UIMockMobile → ChatOverlay → ClosingCard.
 * If this renders without errors, the scene library is fully validated.
 */

import * as React from "react";
import { AbsoluteFill, Sequence } from "remotion";

import { StyleProvider } from "../../lib/tokens";
import { loadFontsForStyle } from "../../lib/fonts";

import { HeroTitle } from "../../scenes/HeroTitle";
import { KineticType } from "../../scenes/KineticType";
import { ThreeScene } from "../../scenes/ThreeScene";
import { UIMockMobile } from "../../scenes/UIMockMobile";
import { ChatOverlay } from "../../scenes/ChatOverlay";
import { ClosingCard } from "../../scenes/ClosingCard";

import { TOKENS } from "./tokens";

const FPS = 30;
const TOTAL_FRAMES = 30 * FPS;

const fonts = loadFontsForStyle(TOKENS);

export const meta = {
  id: "validation-test",
  durationInFrames: TOTAL_FRAMES,
  fps: FPS,
  width: 1080,
  height: 1920,
};

const f = (s: number) => Math.round(s * FPS);

const SCENES: Array<{ from: number; durationInFrames: number; el: React.ReactNode }> = [
  {
    from: f(0),
    durationInFrames: f(3),
    el: (
      <HeroTitle
        eyebrow="VALIDATION TEST"
        product_wordmark="SCENES"
        layout="vertical"
        scene_duration_frames={f(3)}
        fonts={fonts}
      />
    ),
  },
  {
    from: f(3),
    durationInFrames: f(6),
    el: (
      <KineticType
        text="Tipografía cinética con word-stagger."
        pattern="word-stagger"
        stagger_frames={4}
        unit_duration_frames={20}
        italic
        scene_duration_frames={f(6)}
        fonts={fonts}
      />
    ),
  },
  {
    from: f(9),
    durationInFrames: f(6),
    el: <ThreeScene template="particle-field" scene_duration_frames={f(6)} />,
  },
  {
    from: f(15),
    durationInFrames: f(6),
    el: (
      <UIMockMobile
        app_name="DEMO"
        logo_glyph="δ"
        user_avatar_text="TU"
        empresa_name="Tu Empresa S.L."
        search_text="¿Cómo vamos este mes?"
        search_active
        kpi_cards={[
          { value: "1", label: "Empresas" },
          { value: "5", label: "Empleados" },
          { value: "—", label: "Nóminas" },
          { value: "3", label: "Avisos" },
        ]}
        empresa_card={{
          initials: "TE",
          name: "Tu Empresa S.L.",
          nif: "B–XX·XXX·XXX",
          badge: "PROPIETARIO",
        }}
        menu_items={["Inicio", "Empleados", "Nóminas", "Más"]}
        active_menu_index={0}
        scene_duration_frames={f(6)}
        fonts={fonts}
      />
    ),
  },
  {
    from: f(21),
    durationInFrames: f(6),
    el: (
      <ChatOverlay
        agent_name="Demo Agent"
        agent_glyph="δ"
        agent_status="· en línea"
        user_question="¿Cómo vamos este mes?"
        answer_eyebrow="RESPUESTA · < 2 s"
        answer_headline="Vas un 12% por encima del objetivo."
        answer_stats={[
          { label: "FACTURADO", value: "€48.200" },
          { label: "VS OBJETIVO", value: "+12%" },
          { label: "CLIENTES NUEVOS", value: "7" },
          { label: "TICKET MEDIO", value: "€890" },
        ]}
        actions={[
          { text: "Ver detalle", primary: true },
          { text: "Compartir" },
        ]}
        fonts={fonts}
      />
    ),
  },
  {
    from: f(27),
    durationInFrames: f(3),
    el: (
      <ClosingCard
        logo_path="validation-test/delta-logo.png"
        product_wordmark="DEMO"
        brand_wordmark="autarqui"
        brand_wordmark_ext=".co"
        scene_duration_frames={f(3)}
        fonts={fonts}
      />
    ),
  },
];

const ValidationTest: React.FC = () => {
  return (
    <StyleProvider tokens={TOKENS}>
      <AbsoluteFill style={{ backgroundColor: TOKENS.colors.bg }}>
        {SCENES.map((s, i) => (
          <Sequence key={i} from={s.from} durationInFrames={s.durationInFrames}>
            {s.el}
          </Sequence>
        ))}
      </AbsoluteFill>
    </StyleProvider>
  );
};

export default ValidationTest;
