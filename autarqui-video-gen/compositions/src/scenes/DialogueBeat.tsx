/**
 * DialogueBeat — Editorial "— question / dry reaction" pair.
 *
 * From delta launch pattern: a quote dialogue prefixed with em-dash, followed
 * by a smaller muted reaction line. Reads like a transcribed conversation.
 */

import * as React from "react";
import { AbsoluteFill, useCurrentFrame, useVideoConfig } from "remotion";
import { useStyleTokens } from "../lib/tokens";
import { fadeIn, sceneOpacity, defaultPacing } from "../lib/animations";
import type { LoadedFonts } from "../lib/fonts";

export interface DialogueBeatProps {
  question: string;
  reaction: string;
  scene_duration_frames?: number;
  fonts: LoadedFonts;
}

export const DialogueBeat: React.FC<DialogueBeatProps> = ({
  question,
  reaction,
  scene_duration_frames,
  fonts,
}) => {
  const t = useStyleTokens();
  const frame = useCurrentFrame();
  const { fps, durationInFrames } = useVideoConfig();
  const total = scene_duration_frames ?? durationInFrames;
  const { inFrames, outFrames } = defaultPacing(t, fps);

  const op = sceneOpacity(frame, 0, total, inFrames, outFrames);
  const qOp = fadeIn(frame, 0, inFrames);
  const rOp = fadeIn(frame, Math.round(inFrames * 1.5), Math.round(inFrames * 1.1));

  return (
    <AbsoluteFill
      style={{
        backgroundColor: t.colors.bg,
        justifyContent: "center",
        alignItems: "flex-start",
        paddingLeft: "8%",
        paddingRight: "8%",
        opacity: op,
      }}
    >
      <div
        style={{
          fontFamily: fonts.displayItalic,
          fontStyle: "italic",
          fontWeight: 400,
          fontSize: Math.round(t.layout.list_item.main_font_size_px * 0.85),
          lineHeight: 1.22,
          letterSpacing: "-0.012em",
          color: t.colors.heading,
          maxWidth: "92%",
          opacity: qOp,
        }}
      >
        — {question}
      </div>
      <div
        style={{
          marginTop: 38,
          paddingLeft: 56,
          fontFamily: fonts.displayItalic,
          fontStyle: "italic",
          fontWeight: 400,
          fontSize: Math.round(t.layout.list_item.main_font_size_px * 0.49),
          lineHeight: 1.4,
          color: t.colors.muted,
          maxWidth: "84%",
          opacity: rOp,
        }}
      >
        {reaction}
      </div>
    </AbsoluteFill>
  );
};

export const DialogueBeatSchema = {
  question: { type: "string", required: true },
  reaction: { type: "string", required: true },
} as const;
