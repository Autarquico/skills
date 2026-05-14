/**
 * ChatOverlay — Full-screen chat conversation overlay.
 *
 * Tokenized version of the SigmaPromoVertical full-screen chat.
 * Shows: chat header (back arrow + agent name) + user question bubble +
 * agent response panel (with rich content slots) + optional thinking indicator.
 */

import * as React from "react";
import { AbsoluteFill, useCurrentFrame } from "remotion";
import { useStyleTokens } from "../lib/tokens";
import { fadeIn } from "../lib/animations";
import type { LoadedFonts } from "../lib/fonts";

export interface ChatOverlayProps {
  /** Agent name shown in chat header */
  agent_name: string;
  /** Optional agent logo glyph (Greek letter, etc.) */
  agent_glyph?: string;
  /** Status text under agent name */
  agent_status?: string;
  /** The user's question (text bubble at top) */
  user_question: string;
  /** Show "thinking" dots indicator */
  show_thinking?: boolean;
  /** The headline answer (large italic display) */
  answer_headline?: string;
  /** Optional eyebrow above headline (e.g. "RESPUESTA · < 2s") */
  answer_eyebrow?: string;
  /** Optional grid of stat-like data */
  answer_stats?: Array<{ label: string; value: string }>;
  /** Optional action buttons */
  actions?: Array<{ text: string; primary?: boolean }>;
  fonts: LoadedFonts;
}

export const ChatOverlay: React.FC<ChatOverlayProps> = ({
  agent_name,
  agent_glyph,
  agent_status = "· disponible",
  user_question,
  show_thinking = false,
  answer_headline,
  answer_eyebrow,
  answer_stats = [],
  actions = [],
  fonts,
}) => {
  const t = useStyleTokens();
  const frame = useCurrentFrame();
  const accent = t.colors.accent[0]?.hex;
  const op = fadeIn(frame, 0, 18);

  const headerTop = t.ios_chrome ? 70 : 0;

  return (
    <AbsoluteFill style={{ backgroundColor: t.colors.bg, opacity: op }}>
      {/* Chat header */}
      <div
        style={{
          position: "absolute",
          top: headerTop,
          left: 0,
          right: 0,
          padding: "32px 36px 18px 36px",
          display: "flex",
          alignItems: "center",
          gap: 18,
          borderBottom: `0.5px solid ${t.colors.ruleSoft}`,
        }}
      >
        <div style={{ fontFamily: fonts.body, fontWeight: 500, fontSize: 24, color: t.colors.muted }}>←</div>
        <div style={{ display: "flex", alignItems: "center", gap: 14 }}>
          {agent_glyph && (
            <div
              style={{
                fontFamily: fonts.displayItalic,
                fontStyle: "italic",
                fontWeight: 500,
                fontSize: 44,
                color: t.colors.heading,
                lineHeight: 1,
                width: 36,
                textAlign: "center",
              }}
            >
              {agent_glyph}
            </div>
          )}
          <div>
            <div style={{ fontFamily: fonts.body, fontWeight: 600, fontSize: 22, color: t.colors.heading }}>
              {agent_name}
            </div>
            {agent_status && (
              <div
                style={{
                  fontFamily: fonts.body,
                  fontWeight: 400,
                  fontSize: 16,
                  color: accent ? darken(accent) : t.colors.muted,
                }}
              >
                {agent_status}
              </div>
            )}
          </div>
        </div>
      </div>

      {/* User question bubble */}
      <div
        style={{
          position: "absolute",
          top: headerTop + 150,
          right: 36,
          maxWidth: "78%",
          backgroundColor: t.colors.heading,
          color: t.colors.bg,
          borderRadius: 26,
          borderBottomRightRadius: 6,
          padding: "20px 26px",
          fontFamily: fonts.body,
          fontWeight: 400,
          fontSize: 26,
          lineHeight: 1.35,
        }}
      >
        {user_question}
      </div>

      {/* Thinking indicator */}
      {show_thinking && (
        <div
          style={{
            position: "absolute",
            top: headerTop + 290,
            left: 36,
            display: "flex",
            alignItems: "center",
            gap: 12,
          }}
        >
          {agent_glyph && (
            <div
              style={{
                fontFamily: fonts.displayItalic,
                fontStyle: "italic",
                fontWeight: 500,
                fontSize: 36,
                color: t.colors.muted,
                width: 32,
              }}
            >
              {agent_glyph}
            </div>
          )}
          <div
            style={{
              display: "flex",
              gap: 6,
              padding: "16px 20px",
              backgroundColor: t.colors.surface,
              borderRadius: 22,
            }}
          >
            <Dot delay={0} color={t.colors.muted} />
            <Dot delay={0.3} color={t.colors.muted} />
            <Dot delay={0.6} color={t.colors.muted} />
          </div>
        </div>
      )}

      {/* Answer panel — full-width below question */}
      {answer_headline && (
        <div
          style={{
            position: "absolute",
            top: headerTop + 290,
            left: 24,
            right: 24,
            bottom: 60,
            backgroundColor: t.colors.bg,
            borderRadius: 28,
            border: `1px solid ${t.colors.ruleSoft}`,
            padding: "40px 36px",
            display: "flex",
            flexDirection: "column",
          }}
        >
          {answer_eyebrow && (
            <div
              style={{
                fontFamily: fonts.body,
                fontWeight: 500,
                fontSize: 16,
                letterSpacing: "0.18em",
                color: t.colors.muted,
                marginBottom: 22,
              }}
            >
              {answer_eyebrow}
            </div>
          )}
          <div
            style={{
              fontFamily: fonts.displayItalic,
              fontStyle: "italic",
              fontWeight: 500,
              fontSize: 56,
              color: t.colors.heading,
              lineHeight: 1.18,
              marginBottom: 28,
              letterSpacing: "-0.012em",
            }}
          >
            {answer_headline}
          </div>

          {answer_stats.length > 0 && (
            <div
              style={{
                borderTop: `1px solid ${t.colors.ruleSoft}`,
                paddingTop: 26,
                display: "grid",
                gridTemplateColumns: "1fr 1fr",
                gap: "22px 28px",
                marginBottom: 30,
              }}
            >
              {answer_stats.map((s, i) => (
                <div key={i}>
                  <div
                    style={{
                      color: t.colors.muted,
                      fontSize: 16,
                      fontWeight: 500,
                      letterSpacing: "0.12em",
                      fontFamily: fonts.body,
                      marginBottom: 4,
                    }}
                  >
                    {s.label}
                  </div>
                  <div
                    style={{
                      color: t.colors.heading,
                      fontWeight: 500,
                      fontSize: 28,
                      fontFamily: fonts.display,
                    }}
                  >
                    {s.value}
                  </div>
                </div>
              ))}
            </div>
          )}

          <div style={{ flex: 1 }} />

          {actions.length > 0 && (
            <div style={{ display: "flex", gap: 14 }}>
              {actions.map((a, i) => (
                <div
                  key={i}
                  style={{
                    flex: 1,
                    padding: "22px",
                    borderRadius: 14,
                    backgroundColor: a.primary ? t.colors.heading : t.colors.bg,
                    color: a.primary ? t.colors.bg : t.colors.heading,
                    border: a.primary ? "none" : `1.5px solid ${t.colors.rule}`,
                    fontFamily: fonts.body,
                    fontWeight: 500,
                    fontSize: 22,
                    textAlign: "center",
                  }}
                >
                  {a.text}
                </div>
              ))}
            </div>
          )}
        </div>
      )}
    </AbsoluteFill>
  );
};

const Dot: React.FC<{ delay: number; color: string }> = ({ delay, color }) => {
  const frame = useCurrentFrame();
  const phase = (frame / 30 + delay) % 1.2;
  const op = phase < 0.6 ? 0.4 + (phase * 0.6) / 0.6 : 1 - ((phase - 0.6) * 0.6) / 0.6;
  return <div style={{ width: 12, height: 12, backgroundColor: color, borderRadius: "50%", opacity: op }} />;
};

function darken(hex: string): string {
  const h = hex.replace("#", "");
  const r = Math.max(0, parseInt(h.slice(0, 2), 16) - 60);
  const g = Math.max(0, parseInt(h.slice(2, 4), 16) - 40);
  const b = Math.max(0, parseInt(h.slice(4, 6), 16) - 60);
  return `rgb(${r},${g},${b})`;
}

export const ChatOverlaySchema = {
  agent_name: { type: "string", required: true },
  agent_glyph: { type: "string", required: false },
  agent_status: { type: "string", required: false },
  user_question: { type: "string", required: true },
  show_thinking: { type: "boolean", required: false },
  answer_headline: { type: "string", required: false },
  answer_eyebrow: { type: "string", required: false },
  answer_stats: { type: "array", required: false, of: "object" },
  actions: { type: "array", required: false, of: "object" },
} as const;
