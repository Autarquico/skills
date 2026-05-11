/**
 * UIMockMobile — Generic iOS mobile UI mock for product demos.
 *
 * Tokenized version of the SigmaPromoVertical iOS mock pattern.
 * Caller provides:
 *   - app_name (shown in header next to logo glyph)
 *   - logo_glyph (e.g. "σ", "δ", or use a logo image via logo_path)
 *   - menu_items (bottom tab bar)
 *   - search_text (typing effect handled by parent or static)
 *   - empresa (top breadcrumb chip)
 *   - cards (KPI cards 2x2)
 *   - empresa_card (main content card)
 *
 * iOS chrome (status bar + home indicator) controlled by tokens.ios_chrome.
 */

import * as React from "react";
import { AbsoluteFill, Img, staticFile, useCurrentFrame } from "remotion";
import { useStyleTokens } from "../lib/tokens";
import { fadeIn } from "../lib/animations";
import type { LoadedFonts } from "../lib/fonts";

export interface UIMockMobileProps {
  /** App name in header (e.g. "SIGMA") */
  app_name: string;
  /** Optional logo glyph (Greek letter, etc.) — rendered with display font */
  logo_glyph?: string;
  /** Optional path to logo image under public/ (alternative to glyph) */
  logo_path?: string;
  /** Top user avatar text (e.g. "TU") */
  user_avatar_text?: string;
  /** Top breadcrumb */
  empresa_label?: string;
  empresa_name?: string;
  /** Search bar placeholder/text */
  search_text?: string;
  search_placeholder?: string;
  search_active?: boolean;
  /** KPI cards — 2x2 grid */
  kpi_cards?: Array<{ value: string; label: string; accent?: string }>;
  /** Main empresa card */
  empresa_card?: {
    initials: string;
    name: string;
    nif: string;
    badge?: string;
  };
  /** Bottom tab bar items */
  menu_items?: string[];
  active_menu_index?: number;
  scene_duration_frames?: number;
  fonts: LoadedFonts;
}

export const UIMockMobile: React.FC<UIMockMobileProps> = ({
  app_name,
  logo_glyph,
  logo_path,
  user_avatar_text = "TU",
  empresa_label = "EMPRESA",
  empresa_name,
  search_text,
  search_placeholder = "¿En qué puedo ayudarte?",
  search_active = false,
  kpi_cards = [],
  empresa_card,
  menu_items = [],
  active_menu_index = 0,
  scene_duration_frames,
  fonts,
}) => {
  const t = useStyleTokens();
  const frame = useCurrentFrame();
  const op = fadeIn(frame, 0, 18);

  return (
    <AbsoluteFill style={{ backgroundColor: t.colors.bg, opacity: op }}>
      {t.ios_chrome && <IOSStatusBar fonts={fonts} ink={t.colors.heading} />}

      {/* Header */}
      <div
        style={{
          position: "absolute",
          top: t.ios_chrome ? 70 : 0,
          left: 0,
          right: 0,
          padding: "32px 36px 18px 36px",
          display: "flex",
          alignItems: "center",
          justifyContent: "space-between",
          backgroundColor: t.colors.bg,
        }}
      >
        <div style={{ display: "flex", alignItems: "center", gap: 16 }}>
          {logo_path ? (
            <Img src={staticFile(logo_path)} style={{ width: 56, height: 56 }} />
          ) : logo_glyph ? (
            <div
              style={{
                fontFamily: fonts.displayItalic,
                fontStyle: "italic",
                fontWeight: 500,
                fontSize: 60,
                color: t.colors.heading,
                lineHeight: 1,
                width: 50,
                textAlign: "center",
              }}
            >
              {logo_glyph}
            </div>
          ) : null}
          <div
            style={{
              fontFamily: fonts.body,
              fontWeight: 500,
              fontSize: 26,
              color: t.colors.heading,
              letterSpacing: "0.18em",
            }}
          >
            {app_name}
          </div>
        </div>
        {user_avatar_text && (
          <div
            style={{
              width: 64,
              height: 64,
              borderRadius: "50%",
              backgroundColor: hexToA(getAccentOr(t, "#a3d9a5"), 0.25),
              color: getDeepInk(getAccentOr(t, "#a3d9a5")),
              display: "flex",
              alignItems: "center",
              justifyContent: "center",
              fontFamily: fonts.body,
              fontWeight: 500,
              fontSize: 22,
            }}
          >
            {user_avatar_text}
          </div>
        )}
      </div>

      {/* Content */}
      <div
        style={{
          position: "absolute",
          top: t.ios_chrome ? 220 : 150,
          left: 0,
          right: 0,
          bottom: t.ios_chrome ? 130 : 0,
          padding: "0 36px",
          overflow: "hidden",
        }}
      >
        {/* Empresa breadcrumb chip */}
        {empresa_name && (
          <div
            style={{
              display: "inline-flex",
              alignItems: "center",
              gap: 14,
              backgroundColor: hexToA(getAccentOr(t, "#a3d9a5"), 0.2),
              borderRadius: 999,
              padding: "12px 22px",
              fontFamily: fonts.body,
              fontWeight: 400,
              fontSize: 22,
              color: t.colors.ink,
              marginBottom: 28,
            }}
          >
            <span style={{ color: t.colors.muted, letterSpacing: "0.14em", fontSize: 16, fontWeight: 500 }}>
              {empresa_label}
            </span>
            <span style={{ fontFamily: fonts.displayItalic, fontStyle: "italic", fontWeight: 500 }}>
              {empresa_name}
            </span>
          </div>
        )}

        {/* Search bar */}
        <div
          style={{
            backgroundColor: t.colors.surface,
            border: `1.5px solid ${search_active ? t.colors.heading : t.colors.ruleSoft}`,
            borderRadius: 16,
            padding: "26px 28px",
            fontFamily: fonts.body,
            fontWeight: 400,
            fontSize: 28,
            color: search_text ? t.colors.ink : t.colors.faint,
            display: "flex",
            alignItems: "center",
            gap: 16,
            marginBottom: 34,
          }}
        >
          <div style={{ color: t.colors.muted, fontSize: 26 }}>★</div>
          {search_text || search_placeholder}
          {search_active && (
            <span
              style={{
                marginLeft: 4,
                width: 3,
                height: 30,
                backgroundColor: t.colors.ink,
                display: "inline-block",
              }}
            />
          )}
        </div>

        {/* KPI cards 2x2 */}
        {kpi_cards.length > 0 && (
          <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: 20, marginBottom: 30 }}>
            {kpi_cards.map((card, i) => (
              <KpiM key={i} card={card} t={t} fonts={fonts} />
            ))}
          </div>
        )}

        {/* Empresa card */}
        {empresa_card && (
          <div
            style={{
              border: `1px solid ${t.colors.ruleSoft}`,
              borderRadius: 16,
              padding: "28px 30px",
              backgroundColor: t.colors.bg,
            }}
          >
            <div style={{ display: "flex", alignItems: "center", justifyContent: "space-between", marginBottom: 22 }}>
              <div
                style={{
                  width: 76,
                  height: 76,
                  borderRadius: 12,
                  backgroundColor: t.colors.surface,
                  display: "flex",
                  alignItems: "center",
                  justifyContent: "center",
                  fontFamily: fonts.displayItalic,
                  fontStyle: "italic",
                  fontWeight: 500,
                  fontSize: 30,
                  color: t.colors.ink,
                }}
              >
                {empresa_card.initials}
              </div>
              {empresa_card.badge && (
                <div
                  style={{
                    backgroundColor: hexToA(getAccentOr(t, "#a3d9a5"), 0.25),
                    color: getDeepInk(getAccentOr(t, "#a3d9a5")),
                    fontFamily: fonts.body,
                    fontWeight: 500,
                    fontSize: 14,
                    letterSpacing: "0.16em",
                    padding: "8px 14px",
                    borderRadius: 999,
                  }}
                >
                  {empresa_card.badge}
                </div>
              )}
            </div>
            <div style={{ borderTop: `1px solid ${t.colors.ruleSoft}`, paddingTop: 20 }}>
              <div
                style={{
                  fontFamily: fonts.display,
                  fontWeight: 600,
                  fontSize: 32,
                  color: t.colors.heading,
                  marginBottom: 8,
                }}
              >
                {empresa_card.name}
              </div>
              <div
                style={{
                  fontFamily: fonts.body,
                  fontWeight: 400,
                  fontSize: 18,
                  color: t.colors.muted,
                }}
              >
                {empresa_card.nif}
              </div>
            </div>
          </div>
        )}
      </div>

      {/* Bottom tab bar */}
      {menu_items.length > 0 && (
        <div
          style={{
            position: "absolute",
            bottom: t.ios_chrome ? 0 : 0,
            left: 0,
            right: 0,
            height: t.ios_chrome ? 130 : 100,
            borderTop: `0.5px solid ${t.colors.ruleSoft}`,
            backgroundColor: "rgba(255,255,255,0.94)",
            display: "flex",
            alignItems: "flex-start",
            justifyContent: "space-around",
            paddingTop: 18,
          }}
        >
          {menu_items.map((label, i) => (
            <div
              key={label}
              style={{
                display: "flex",
                flexDirection: "column",
                alignItems: "center",
                gap: 6,
                fontFamily: fonts.body,
                fontWeight: 500,
                fontSize: 16,
                color: i === active_menu_index ? t.colors.heading : t.colors.muted,
              }}
            >
              <div
                style={{
                  width: 28,
                  height: 28,
                  border: `2px solid ${i === active_menu_index ? t.colors.heading : t.colors.muted}`,
                  borderRadius: 6,
                }}
              />
              {label}
            </div>
          ))}
        </div>
      )}

      {t.ios_chrome && <IOSHomeIndicator ink={t.colors.heading} />}
    </AbsoluteFill>
  );
};

// ---------------------------------------------------------------------------
// Helpers
// ---------------------------------------------------------------------------

const KpiM: React.FC<{
  card: { value: string; label: string; accent?: string };
  t: ReturnType<typeof useStyleTokens>;
  fonts: LoadedFonts;
}> = ({ card, t, fonts }) => {
  const accent = card.accent ?? t.colors.rule;
  return (
    <div
      style={{
        border: `1px solid ${t.colors.ruleSoft}`,
        borderTop: `4px solid ${accent}`,
        borderRadius: 16,
        padding: "26px 24px",
        backgroundColor: t.colors.bg,
      }}
    >
      <div
        style={{
          width: 48,
          height: 48,
          borderRadius: 10,
          backgroundColor: accent === t.colors.rule ? t.colors.surface : hexToA(accent, 0.2),
          marginBottom: 20,
        }}
      />
      <div
        style={{
          fontFamily: fonts.displayItalic,
          fontStyle: "italic",
          fontWeight: 500,
          fontSize: 56,
          color: t.colors.heading,
          lineHeight: 1,
          marginBottom: 8,
        }}
      >
        {card.value}
      </div>
      <div style={{ fontFamily: fonts.body, fontWeight: 400, fontSize: 20, color: t.colors.muted }}>
        {card.label}
      </div>
    </div>
  );
};

const IOSStatusBar: React.FC<{ fonts: LoadedFonts; ink: string }> = ({ fonts, ink }) => (
  <div
    style={{
      position: "absolute",
      top: 0,
      left: 0,
      right: 0,
      height: 60,
      display: "flex",
      alignItems: "center",
      justifyContent: "space-between",
      padding: "20px 50px 0 50px",
      fontFamily: fonts.body,
      fontWeight: 600,
      fontSize: 26,
      color: ink,
      zIndex: 10,
    }}
  >
    <div>9:41</div>
    <div style={{ display: "flex", alignItems: "center", gap: 10 }}>
      <div style={{ display: "flex", alignItems: "flex-end", gap: 3 }}>
        {[6, 8, 10, 12].map((h, i) => (
          <div key={i} style={{ width: 4, height: h, backgroundColor: ink, borderRadius: 1 }} />
        ))}
      </div>
      <div style={{ fontSize: 22, color: ink }}>⦿</div>
      <div
        style={{
          width: 38,
          height: 18,
          border: `1.5px solid ${ink}`,
          borderRadius: 4,
          padding: 2,
          position: "relative",
        }}
      >
        <div style={{ width: "85%", height: "100%", backgroundColor: ink, borderRadius: 1 }} />
      </div>
    </div>
  </div>
);

const IOSHomeIndicator: React.FC<{ ink: string }> = ({ ink }) => (
  <div
    style={{
      position: "absolute",
      bottom: 16,
      left: 0,
      right: 0,
      display: "flex",
      justifyContent: "center",
      zIndex: 10,
    }}
  >
    <div style={{ width: 360, height: 6, backgroundColor: ink, borderRadius: 3 }} />
  </div>
);

// Utility: prefer first accent color from tokens, fall back to a sane default
function getAccentOr(
  t: ReturnType<typeof useStyleTokens>,
  fallback: string,
): string {
  return t.colors.accent[0]?.hex || fallback;
}

// Utility: hex → rgba with alpha
function hexToA(hex: string, alpha: number): string {
  const h = hex.replace("#", "");
  const r = parseInt(h.slice(0, 2), 16);
  const g = parseInt(h.slice(2, 4), 16);
  const b = parseInt(h.slice(4, 6), 16);
  return `rgba(${r},${g},${b},${alpha})`;
}

// Utility: derive a deeper variant of an accent for use as text-on-soft-accent
function getDeepInk(hex: string): string {
  // Naive: darken by reducing each channel
  const h = hex.replace("#", "");
  const r = Math.max(0, parseInt(h.slice(0, 2), 16) - 70);
  const g = Math.max(0, parseInt(h.slice(2, 4), 16) - 50);
  const b = Math.max(0, parseInt(h.slice(4, 6), 16) - 70);
  return `rgb(${r},${g},${b})`;
}

export const UIMockMobileSchema = {
  app_name: { type: "string", required: true },
  logo_glyph: { type: "string", required: false },
  logo_path: { type: "string", required: false },
  user_avatar_text: { type: "string", required: false },
  empresa_label: { type: "string", required: false },
  empresa_name: { type: "string", required: false },
  search_text: { type: "string", required: false },
  search_placeholder: { type: "string", required: false },
  search_active: { type: "boolean", required: false },
  kpi_cards: { type: "array", required: false, of: "object" },
  empresa_card: { type: "object", required: false },
  menu_items: { type: "array", required: false, of: "string" },
  active_menu_index: { type: "number", required: false },
} as const;
