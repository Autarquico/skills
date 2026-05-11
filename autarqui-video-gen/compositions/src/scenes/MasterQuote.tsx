/**
 * MasterQuote — Centered pull quote with hairline rules above and below.
 *
 * From the dossier `blockquote.master` treatment. Used for the master line
 * (e.g. "autarqui.co hace empresas más autosuficientes").
 */

import * as React from "react";
import { AbsoluteFill, useCurrentFrame, useVideoConfig } from "remotion";
import { useStyleTokens } from "../lib/tokens";
import { fadeIn, sceneOpacity, defaultPacing } from "../lib/animations";
import type { LoadedFonts } from "../lib/fonts";

export interface MasterQuoteProps {
  text: string;
  scene_duration_frames?: number;
  fonts: LoadedFonts;
}

export const MasterQuote: React.FC<MasterQuoteProps> = ({ text, scene_duration_frames, fonts }) => {
  const t = useStyleTokens();
  const frame = useCurrentFrame();
  const { fps, durationInFrames } = useVideoConfig();
  const total = scene_duration_frames ?? durationInFrames;
  const { inFrames, outFrames } = defaultPacing(t, fps);

  const op = sceneOpacity(frame, 0, total, inFrames, outFrames);
  const textOp = fadeIn(frame, 0, inFrames);
  const isCenter = t.layout.master_quote.alignment === "center";

  return (
    <AbsoluteFill
      style={{
        backgroundColor: t.colors.bg,
        justifyContent: "center",
        alignItems: "center",
        paddingLeft: "8%",
        paddingRight: "8%",
        opacity: op,
      }}
    >
      <div style={{ width: "84%", maxWidth: 900 }}>
        {t.layout.master_quote.has_rules && (
          <div style={{ height: 1, backgroundColor: t.colors.rule, width: "100%" }} />
        )}
        <div
          style={{
            fontFamily: fonts.displayItalic,
            fontStyle: "italic",
            fontWeight: 500,
            fontSize: t.layout.master_quote.font_size_px,
            lineHeight: 1.3,
            letterSpacing: "-0.01em",
            color: t.colors.heading,
            textAlign: isCenter ? "center" : "left",
            padding: "44px 0",
            opacity: textOp,
          }}
        >
          {text}
        </div>
        {t.layout.master_quote.has_rules && (
          <div style={{ height: 1, backgroundColor: t.colors.rule, width: "100%" }} />
        )}
      </div>
    </AbsoluteFill>
  );
};

export const MasterQuoteSchema = {
  text: { type: "string", required: true },
} as const;
